PYTHON ?= python3
EXTRACTOR := extract_chatgpt_html.py
IMPORT_DIR := import
OUTPUT_DIR := import_json
VIEWER_DIR := viewer
VIEWER_SERVER := $(VIEWER_DIR)/server.py
CAPTURE_SCRIPT := scripts/capture_chatgpt_tab.sh
RELEASE_BUILD_SCRIPT := scripts/build-release-bundle.sh
RELEASE_VERIFY_SCRIPT := scripts/verify-release-bundle.sh
PORT ?= 8000
VERSION ?= v0.0.1
RELEASE_ARTIFACT := dist/release/ChatGPTDialogs-$(patsubst v%,%,$(VERSION)).zip

HTML_FILES := $(wildcard $(IMPORT_DIR)/*.html)
JSON_FILES := $(patsubst $(IMPORT_DIR)/%.html,$(OUTPUT_DIR)/%.json,$(HTML_FILES))

.PHONY: help dirs extract-all capture-browser capture-browser-extract serve-viewer test release-bundle verify-release-bundle clean

help:
	@echo "Targets:"
	@echo "  make extract-all  Extract all HTML files from $(IMPORT_DIR)/ into $(OUTPUT_DIR)/"
	@echo "  make capture-browser Capture the front browser tab HTML into $(IMPORT_DIR)/"
	@echo "  make capture-browser-extract Capture the front browser tab and extract JSON"
	@echo "  make serve-viewer Start the viewer app for $(OUTPUT_DIR)/ on port $(PORT)"
	@echo "  make test         Run extractor regression tests"
	@echo "  make release-bundle VERSION=v0.0.1 Build a minimal release bundle"
	@echo "  make verify-release-bundle VERSION=v0.0.1 Verify a built release bundle"
	@echo "  make clean        Remove extracted JSON files from $(OUTPUT_DIR)/"

dirs:
	@mkdir -p $(IMPORT_DIR) $(OUTPUT_DIR)

extract-all: dirs $(JSON_FILES)
	@echo "Extracted $(words $(JSON_FILES)) file(s) into $(OUTPUT_DIR)/"

$(OUTPUT_DIR)/%.json: $(IMPORT_DIR)/%.html $(EXTRACTOR) | dirs
	@$(PYTHON) $(EXTRACTOR) "$<" -o "$@"

capture-browser: dirs
	@bash $(CAPTURE_SCRIPT)

capture-browser-extract: dirs
	@AUTO_EXTRACT=1 bash $(CAPTURE_SCRIPT)

serve-viewer:
	@$(PYTHON) $(VIEWER_SERVER) --port $(PORT) --repo-root . --dialog-dir $(OUTPUT_DIR)

test:
	@$(PYTHON) -m unittest discover -s tests -p 'test_*.py'

release-bundle:
	@./$(RELEASE_BUILD_SCRIPT) "$(VERSION)" .

verify-release-bundle:
	@./$(RELEASE_VERIFY_SCRIPT) "$(RELEASE_ARTIFACT)"

clean:
	@rm -f $(OUTPUT_DIR)/*.json
