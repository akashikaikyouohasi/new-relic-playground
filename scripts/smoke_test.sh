#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://localhost:8000}"

# --- 色定義 ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

# --- jq 検出 ---
HAS_JQ=false
if command -v jq &>/dev/null; then
  HAS_JQ=true
fi

# --- エンドポイント定義 ---
# 形式: "METHOD|PATH|BODY"  (BODY が空なら "-")

HEALTH_ENDPOINTS=(
  "GET|/|-"
  "GET|/health|-"
)

APM_ENDPOINTS=(
  "GET|/api/apm/fast|-"
  "GET|/api/apm/slow|-"
  "GET|/api/apm/variable?delay_ms=300|-"
  "GET|/api/apm/cpu-intensive|-"
)

ERRORS_ENDPOINTS=(
  'GET|/api/errors/unhandled|-'
  'GET|/api/errors/handled|-'
  'GET|/api/errors/http-error?status_code=422|-'
  'POST|/api/errors/custom-error|{"error_message":"test error","user_id":"u-123","order_id":"o-456"}'
)

TRACING_ENDPOINTS=(
  "GET|/api/tracing/external-call|-"
  "GET|/api/tracing/chained-calls|-"
  "GET|/api/tracing/parallel-calls|-"
)

LOGS_ENDPOINTS=(
  "GET|/api/logs/basic|-"
  "GET|/api/logs/structured|-"
  "GET|/api/logs/with-error|-"
)

CUSTOM_ENDPOINTS=(
  'POST|/api/custom/event|{"event_type":"TestEvent","attributes":{"source":"smoke_test"}}'
  'POST|/api/custom/metric|{"metric_name":"test.metric","value":42.0}'
  'POST|/api/custom/batch-events|{"event_type":"BatchTest","count":5}'
)

INSTRUMENTATION_ENDPOINTS=(
  "GET|/api/custom-instrumentation/function-trace|-"
  'POST|/api/custom-instrumentation/background-task|{"task_name":"smoke_test","items":3}'
  "GET|/api/custom-instrumentation/custom-attributes|-"
)

CATEGORY_NAMES=("Health" "APM" "Errors" "Tracing" "Logs" "Custom Events" "Instrumentation")
CATEGORY_ARRAYS=(
  HEALTH_ENDPOINTS
  APM_ENDPOINTS
  ERRORS_ENDPOINTS
  TRACING_ENDPOINTS
  LOGS_ENDPOINTS
  CUSTOM_ENDPOINTS
  INSTRUMENTATION_ENDPOINTS
)

# --- ヘルパー関数 ---

get_endpoints() {
  local arr_name="${CATEGORY_ARRAYS[$1]}[@]"
  echo "${!arr_name}"
}

get_endpoint_count() {
  local arr_name="${CATEGORY_ARRAYS[$1]}[@]"
  local arr=("${!arr_name}")
  echo "${#arr[@]}"
}

colorize_status() {
  local code="$1"
  if [[ "$code" -ge 200 && "$code" -lt 300 ]]; then
    echo -e "${GREEN}${code}${RESET}"
  elif [[ "$code" -ge 400 ]]; then
    echo -e "${RED}${code}${RESET}"
  else
    echo -e "${YELLOW}${code}${RESET}"
  fi
}

format_json() {
  if $HAS_JQ; then
    jq . 2>/dev/null || cat
  else
    cat
  fi
}

execute_endpoint() {
  local entry="$1"
  local method path body
  IFS='|' read -r method path body <<< "$entry"

  local url="${BASE_URL}${path}"
  echo -e "\n${BOLD}>>> ${method} ${url}${RESET}"

  local curl_args=(-s -w '\n%{http_code}' -X "$method")
  if [[ "$body" != "-" ]]; then
    curl_args+=(-H 'Content-Type: application/json' -d "$body")
    echo -e "${CYAN}Body: ${body}${RESET}"
  fi

  local response
  response=$(curl "${curl_args[@]}" "$url" 2>&1) || {
    echo -e "${RED}接続エラー: サーバーに接続できません${RESET}"
    return 1
  }

  local status_code
  status_code=$(echo "$response" | tail -1)
  local response_body
  response_body=$(echo "$response" | sed '$d')

  echo -e "<<< $(colorize_status "$status_code")"
  echo "$response_body" | format_json
}

wait_for_enter() {
  echo ""
  read -rp "[Enter] で続行..."
}

run_category() {
  local cat_idx="$1"
  local arr_name="${CATEGORY_ARRAYS[$cat_idx]}[@]"
  local endpoints=("${!arr_name}")
  local name="${CATEGORY_NAMES[$cat_idx]}"

  echo -e "\n${BOLD}=== ${name} (全 ${#endpoints[@]} エンドポイント) ===${RESET}"
  for entry in "${endpoints[@]}"; do
    execute_endpoint "$entry"
  done
}

run_all() {
  for i in "${!CATEGORY_NAMES[@]}"; do
    run_category "$i"
  done
  echo -e "\n${GREEN}${BOLD}全エンドポイントの実行が完了しました${RESET}"
}

# --- カテゴリ内メニュー ---

category_menu() {
  local cat_idx="$1"
  local arr_name="${CATEGORY_ARRAYS[$cat_idx]}[@]"
  local endpoints=("${!arr_name}")
  local name="${CATEGORY_NAMES[$cat_idx]}"

  while true; do
    echo -e "\n${BOLD}--- ${name} ---${RESET}"
    for i in "${!endpoints[@]}"; do
      local entry="${endpoints[$i]}"
      local method path body
      IFS='|' read -r method path body <<< "$entry"
      printf "  %d) %-5s %s\n" "$((i + 1))" "$method" "$path"
    done
    echo "  a) このカテゴリを全て実行"
    echo "  b) 戻る"
    echo ""
    read -rp "> " choice

    case "$choice" in
      [0-9]*)
        local idx=$((choice - 1))
        if [[ $idx -ge 0 && $idx -lt ${#endpoints[@]} ]]; then
          execute_endpoint "${endpoints[$idx]}"
          wait_for_enter
        else
          echo -e "${RED}無効な番号です${RESET}"
        fi
        ;;
      a)
        run_category "$cat_idx"
        wait_for_enter
        ;;
      b)
        return
        ;;
      *)
        echo -e "${RED}無効な入力です${RESET}"
        ;;
    esac
  done
}

# --- メインメニュー ---

main_menu() {
  while true; do
    echo -e "\n${BOLD}=== New Relic Playground - Smoke Test ===${RESET}"
    echo -e "BASE_URL: ${CYAN}${BASE_URL}${RESET}"
    echo ""
    echo "カテゴリを選択:"
    for i in "${!CATEGORY_NAMES[@]}"; do
      local count
      count=$(get_endpoint_count "$i")
      printf "  %d) %-18s (%d endpoints)\n" "$((i + 1))" "${CATEGORY_NAMES[$i]}" "$count"
    done
    echo "  a) 全て実行"
    echo "  q) 終了"
    echo ""
    read -rp "> " choice

    case "$choice" in
      [1-7])
        category_menu "$((choice - 1))"
        ;;
      a)
        run_all
        wait_for_enter
        ;;
      q)
        echo "終了します"
        exit 0
        ;;
      *)
        echo -e "${RED}無効な入力です${RESET}"
        ;;
    esac
  done
}

# --- エントリポイント ---
main_menu
