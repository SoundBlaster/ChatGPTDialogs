#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <tag> [repo_root]" >&2
  exit 1
}

tag="${1:-}"
repo_root_arg="${2:-.}"

if [[ -z "${tag}" ]]; then
  usage
fi

repo_root="$(cd "${repo_root_arg}" && pwd)"
version="${tag#v}"
release_name="ChatGPTDialogs-${version}"
output_dir="${OUTPUT_DIR:-${repo_root}/dist/release}"
bundle_parent="$(mktemp -d "${TMPDIR:-/tmp}/chatgptdialogs-release.XXXXXX")"
bundle_root="${bundle_parent}/${release_name}"
artifact_zip="${output_dir}/${release_name}.zip"
artifact_sums="${output_dir}/${release_name}.sha256sum"
trap 'rm -rf "${bundle_parent}"' EXIT

mkdir -p "${output_dir}" "${bundle_root}"

copy_file() {
  local relative_path="$1"
  mkdir -p "$(dirname "${bundle_root}/${relative_path}")"
  cp -p "${repo_root}/${relative_path}" "${bundle_root}/${relative_path}"
}

copy_file "README.md"
copy_file "LICENSE"
copy_file "Makefile"
copy_file "extract_chatgpt_html.py"
copy_file "EXTRACTOR_README.md"
copy_file "CAPTURE_README.md"
copy_file "scripts/capture_chatgpt_tab.sh"
copy_file "scripts/browser_eval.js"
copy_file "viewer/index.html"
copy_file "viewer/server.py"

rm -f "${artifact_zip}" "${artifact_sums}"
(cd "${bundle_parent}" && zip -qr "${artifact_zip}" "${release_name}")

if command -v sha256sum >/dev/null 2>&1; then
  checksum_cmd=(sha256sum)
elif command -v shasum >/dev/null 2>&1; then
  checksum_cmd=(shasum -a 256)
else
  echo "Neither sha256sum nor shasum is available" >&2
  exit 1
fi

"${checksum_cmd[@]}" "${artifact_zip}" > "${artifact_sums}"

cat <<EOF
ARTIFACT_DIR=${output_dir}
ARTIFACT_ZIP=${artifact_zip}
ARTIFACT_SUMS=${artifact_sums}
RELEASE_BUNDLE=${release_name}
EOF
