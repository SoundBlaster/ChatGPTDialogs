#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <artifact_zip>" >&2
  exit 1
}

artifact_zip="${1:-}"
if [[ -z "${artifact_zip}" ]]; then
  usage
fi

if [[ ! -f "${artifact_zip}" ]]; then
  echo "Missing artifact zip: ${artifact_zip}" >&2
  exit 1
fi

artifact_dir="$(cd "$(dirname "${artifact_zip}")" && pwd)"
artifact_base="$(basename "${artifact_zip}" .zip)"
artifact_sums="${artifact_dir}/${artifact_base}.sha256sum"

if [[ ! -f "${artifact_sums}" ]]; then
  echo "Missing artifact checksum file: ${artifact_sums}" >&2
  exit 1
fi

if command -v sha256sum >/dev/null 2>&1; then
  checksum_verify_cmd=(sha256sum -c)
elif command -v shasum >/dev/null 2>&1; then
  checksum_verify_cmd=(shasum -a 256 -c)
else
  echo "Neither sha256sum nor shasum is available" >&2
  exit 1
fi

"${checksum_verify_cmd[@]}" "${artifact_sums}"

tmpdir="$(mktemp -d "${TMPDIR:-/tmp}/chatgptdialogs-verify.XXXXXX")"
trap 'rm -rf "${tmpdir}"' EXIT

unzip -q "${artifact_zip}" -d "${tmpdir}"

bundle_root="${tmpdir}/${artifact_base}"
if [[ ! -d "${bundle_root}" ]]; then
  echo "Bundle root missing: ${bundle_root}" >&2
  exit 1
fi

while IFS= read -r -d '' path; do
  if [[ "${path}" != "${bundle_root}" && "${path}" != "${bundle_root}/"* ]]; then
    echo "Unexpected file outside bundle root: ${path#${tmpdir}/}" >&2
    exit 1
  fi
done < <(find "${tmpdir}" -mindepth 1 -type f -print0)

required_files=(
  "README.md"
  "LICENSE"
  "Makefile"
  "extract_chatgpt_html.py"
  "EXTRACTOR_README.md"
  "CAPTURE_README.md"
  "scripts/capture_chatgpt_tab.sh"
  "scripts/browser_eval.js"
  "viewer/index.html"
  "viewer/server.py"
)

for relative_path in "${required_files[@]}"; do
  if [[ ! -f "${bundle_root}/${relative_path}" ]]; then
    echo "Missing required file in bundle: ${relative_path}" >&2
    exit 1
  fi
done

while IFS= read -r -d '' path; do
  relative_path="${path#${bundle_root}/}"
  case "${relative_path}" in
    README.md|LICENSE|Makefile|extract_chatgpt_html.py|EXTRACTOR_README.md|CAPTURE_README.md|scripts/capture_chatgpt_tab.sh|scripts/browser_eval.js|viewer/index.html|viewer/server.py)
      ;;
    *)
      echo "Unexpected file in bundle: ${relative_path}" >&2
      exit 1
      ;;
  esac
done < <(find "${bundle_root}" -type f -print0)

echo "Release bundle verified: ${artifact_zip}"
