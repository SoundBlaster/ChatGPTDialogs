# ChatGPTDialogs

ChatGPTDialogs is a small macOS-first toolkit for capturing an open ChatGPT conversation from the browser, converting the saved HTML into JSON, and reviewing the result in a local viewer.

## Repository Layout

- `extract_chatgpt_html.py`: Converts saved ChatGPT web HTML pages into normalized JSON dialog files.
- `scripts/capture_chatgpt_tab.sh`: Mac capture helper that saves the current browser conversation HTML into `import/`.
- `scripts/browser_eval.js`: JXA bridge used by the capture script to run JavaScript in the active browser tab.
- `viewer/`: Local folder-based viewer/editor for dialogs in `import_json/`.
- `tests/fixtures/`: public HTML/JSON regression corpus for the extractor.
- `tests/test_extract_chatgpt_html.py`: extractor regression tests.
- `import/`: Local runtime directory for captured ChatGPT HTML.
- `import_json/`: Local runtime directory for extracted JSON.
- `exports/`: Optional checked-in exports directory.
- `page_example/`: Example HTML reference material.
- `pre_ideal_example_markdown/`: Draft/reference markdown content.
- `EXTRACTOR_README.md`: Detailed notes for the extraction scripts.
- `CAPTURE_README.md`: Browser-capture manual for the Mac automation flow.

## Main Workflows

### 1. Capture the current browser tab into `import/`

Use this when you want to save the current ChatGPT web page as raw HTML and then turn it into JSON locally.

Capture only:

```bash
make capture-browser
```

Capture and extract immediately:

```bash
make capture-browser-extract
```

This workflow:

1. Chooses the frontmost supported browser, or another running supported browser if Terminal is frontmost.
2. Activates that browser and waits briefly for focus to settle.
3. Auto-scrolls the page to load more content.
4. Saves the page HTML into `import/`.
5. Optionally extracts JSON into `import_json/`.

### 2. Open the local viewer

```bash
make serve-viewer
```

The viewer reads dialogs from `import_json/`.

### 3. Run extractor regression tests

```bash
make test
```

Tests use the checked-in public corpus under `tests/fixtures/`.

Supported browsers:

- `Safari`
- `Google Chrome`
- `Brave Browser`
- `Chromium`

Safari note:

- Safari capture requires `Allow JavaScript from Apple Events` in the `Developer` section of Safari Settings.

You can tune timing with variables such as:

```bash
ACTIVATION_DELAY=2 SCROLL_PAUSE=2 MAX_SCROLLS=30 make capture-browser
```

## Expected Data Shape

Extracted JSON files are expected to contain:

```json
{
  "title": "Conversation Title",
  "source_file": "/absolute/path/to/file.html",
  "message_count": 42,
  "messages": [
    {
      "role": "user",
      "content": "..."
    },
    {
      "role": "assistant",
      "content": "..."
    }
  ]
}
```

Each message may also include `turn_id`, `message_id`, and `source`.

## Working Conventions

- There is no package manager or compiled build step.
- Runtime capture outputs in `import/` and `import_json/` are local working files; checked-in public fixtures live under `tests/fixtures/`.
- Prefer ASCII unless the file already contains non-ASCII text.
- Do not overwrite checked-in exports unless that is the explicit goal.
- Before finishing work, verify the worktree with:

```bash
git status --short
```

## Current Caveats

- Browser capture on macOS depends on Automation permissions for the terminal app controlling the browser.
- ChatGPT DOM structure changes over time, so extractor regressions should be guarded with `make test`.
- `import/` and `import_json/` are ignored runtime directories; fixtures belong under `tests/fixtures/`.

## Related Documents

- `EXTRACTOR_README.md`: script usage details for capture and extraction.
- `CAPTURE_README.md`: Mac browser-capture workflow for saving live ChatGPT tabs into `import/` and `import_json/`.
- `ARCHITECTURE_DECISION.md`: functional module boundaries and recommended future repo split.
- `AGENTS.md`: contributor instructions for coding style, validation, and export handling.
