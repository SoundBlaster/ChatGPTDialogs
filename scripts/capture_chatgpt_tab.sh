#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
IMPORT_DIR="${ROOT_DIR}/import"
EXTRACTOR="${ROOT_DIR}/extract_chatgpt_html.py"
BROWSER_EVAL_SCRIPT="${ROOT_DIR}/scripts/browser_eval.js"

mkdir -p "${IMPORT_DIR}"

AUTO_EXTRACT="${AUTO_EXTRACT:-0}"
ACTIVATION_DELAY="${ACTIVATION_DELAY:-1}"
SCROLL_PAUSE="${SCROLL_PAUSE:-1}"
MAX_SCROLLS="${MAX_SCROLLS:-18}"
NOTIFY="${NOTIFY:-1}"
FRONT_BROWSER="${BROWSER:-}"
SUPPORTED_BROWSERS=("Safari" "Google Chrome" "Brave Browser" "Chromium")

is_supported_browser() {
  local name="${1:-}"
  for browser in "${SUPPORTED_BROWSERS[@]}"; do
    if [[ "${name}" == "${browser}" ]]; then
      return 0
    fi
  done
  return 1
}

browser_is_running() {
  local name="${1}"
  local result
  result="$(osascript -e "tell application \"System Events\" to return exists application process \"${name}\"" 2>/dev/null || true)"
  [[ "${result}" == "true" ]]
}

pick_browser_interactively() {
  local choice
  choice="$(
    osascript <<'APPLESCRIPT'
set browserChoices to {}
tell application "System Events"
	repeat with browserName in {"Safari", "Google Chrome", "Brave Browser", "Chromium"}
		if exists application process (contents of browserName) then set end of browserChoices to (contents of browserName)
	end repeat
end tell

if (count of browserChoices) is 0 then
	error "No supported browser is running."
end if

if (count of browserChoices) is 1 then
	return item 1 of browserChoices
end if

set picked to choose from list browserChoices with prompt "Choose the browser to capture from" default items {item 1 of browserChoices}
if picked is false then
	error "No browser selected."
end if
return item 1 of picked
APPLESCRIPT
  )"
  printf '%s\n' "${choice}"
}

if [[ -z "${FRONT_BROWSER}" ]]; then
  FRONT_BROWSER="$(osascript -e 'tell application "System Events" to get name of first application process whose frontmost is true')"
fi

if ! is_supported_browser "${FRONT_BROWSER}"; then
  running_browsers=()
  for browser in "${SUPPORTED_BROWSERS[@]}"; do
    if browser_is_running "${browser}"; then
      running_browsers+=("${browser}")
    fi
  done

  if [[ "${#running_browsers[@]}" -eq 1 ]]; then
    FRONT_BROWSER="${running_browsers[0]}"
  elif [[ "${#running_browsers[@]}" -gt 1 ]]; then
    FRONT_BROWSER="$(pick_browser_interactively)"
  else
    echo "Unsupported or non-browser front app: ${FRONT_BROWSER}" >&2
    echo "No supported running browser was found. Start Safari, Google Chrome, Brave Browser, or Chromium, or set BROWSER=Safari." >&2
    exit 1
  fi
fi

run_js() {
  osascript -l JavaScript "${BROWSER_EVAL_SCRIPT}" "${FRONT_BROWSER}" "$1"
}

notify_done() {
  local title="${1}"
  local message="${2}"

  if [[ "${NOTIFY}" != "1" ]]; then
    return 0
  fi

  printf '\a' || true

  osascript - "${title}" "${message}" <<'APPLESCRIPT' >/dev/null 2>&1 || true
on run argv
	set notificationTitle to item 1 of argv
	set notificationMessage to item 2 of argv
	display notification notificationMessage with title notificationTitle
end run
APPLESCRIPT
}

echo "Using browser: ${FRONT_BROWSER}"
echo "Auto-scrolling the active tab to load more content..."

osascript -e "tell application \"${FRONT_BROWSER}\" to activate" >/dev/null 2>&1 || true
sleep "${ACTIVATION_DELAY}"

last_height=""
stable_count=0
for ((i=1; i<=MAX_SCROLLS; i++)); do
  height="$(run_js 'var e = document.scrollingElement || document.body; window.scrollTo(0, e.scrollHeight); String(e.scrollHeight);')"
  sleep "${SCROLL_PAUSE}"
  if [[ "${height}" == "${last_height}" ]]; then
    stable_count=$((stable_count + 1))
  else
    stable_count=0
  fi
  last_height="${height}"
  if [[ "${stable_count}" -ge 2 ]]; then
    break
  fi
done

title="$(run_js 'document.title || "chatgpt-dialog";')"
url="$(run_js 'location.href;')"

slug="$(
  python3 - "${title}" <<'PY'
import re
import sys
import unicodedata

title = unicodedata.normalize("NFKC", sys.argv[1].strip()) or "chatgpt-dialog"
slug = re.sub(r"[^\w.-]+", "_", title, flags=re.UNICODE)
slug = re.sub(r"_+", "_", slug)
slug = slug.strip("._-")[:180]
print(slug or "chatgpt-dialog")
PY
)"

output_path="${IMPORT_DIR}/${slug}.html"
if [[ -e "${output_path}" ]]; then
  timestamp="$(date +"%Y%m%d_%H%M%S")"
  output_path="${IMPORT_DIR}/${slug}_${timestamp}.html"
fi

echo "Capturing HTML from:"
echo "  ${url}"

run_js 'document.documentElement.outerHTML;' > "${output_path}"

echo "Saved HTML to:"
echo "  ${output_path}"

if [[ "${AUTO_EXTRACT}" == "1" ]]; then
  json_path="${ROOT_DIR}/import_json/$(basename "${output_path%.html}.json")"
  python3 "${EXTRACTOR}" "${output_path}" -o "${json_path}"
  echo "Saved JSON to:"
  echo "  ${json_path}"
  notify_done "ChatGPTDialogs Capture Complete" "Saved HTML and JSON for $(basename "${output_path}")"
else
  notify_done "ChatGPTDialogs Capture Complete" "Saved HTML to $(basename "${output_path}")"
fi
