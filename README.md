# ChatGPTDialogs

ChatGPTDialogs is an extractor-first repository for converting saved ChatGPT HTML pages into normalized JSON dialogs and validating the parser against a checked-in regression corpus.

The viewer/editor now lives in the separate `ContextBuilder` repository. This repository keeps the extractor, its fixtures, and the HTML/JSON contract. The browser-capture scripts remain here for now as local workflow helpers, but they are not part of the `ContextBuilder` boundary.

Quick start:

```bash
python3 extract_chatgpt_html.py path/to/dialog.html -o path/to/dialog.json
```

## Main Workflows

### 1. Extract saved HTML into JSON

Convert a single saved ChatGPT page:

```bash
python3 extract_chatgpt_html.py import/example.html -o import_json/example.json
```

Batch-extract all local HTML files from `import/` into `import_json/`:

```bash
make extract-all
```

### 2. Run extractor regression tests

```bash
make test
```

Tests use the checked-in public corpus under `tests/fixtures/`.

### 3. Detect lineage and generate relationships

When exporting ChatGPT conversations at different times or from branches, exported JSON files often share identical `message_id` sequences at the beginning. The lineage detection script identifies these relationships and generates a manifest:

```bash
make detect-lineage
```

This outputs `import_json/lineage.json` with detected prefix relationships in ContextBuilder-compatible format:
- Files with no shared messages are marked as roots
- Files where another file's entire sequence is a prefix are marked as branches
- Each branch records the parent conversation_id and the branch point (last shared message_id)
- All relationships use `link_type: "branch"` (both continuations and divergences are branches)

Example:
```json
{
  "conversation_id": "SpecGraph_-_DB_Schema_Query_Language",
  "file": "SpecGraph_-_DB_Schema_Query_Language.json",
  "message_count": 10,
  "lineage": {
    "parents": [
      {
        "conversation_id": "SpecGraph_-_Модель",
        "message_id": "a25d74ee-fc64-4d83-b7cd-bf8dc7309219",
        "link_type": "branch"
      }
    ]
  }
}
```

### 4. Optional local browser capture

If you still use the legacy local capture flow, you can save the active ChatGPT tab into `import/` and optionally extract it into `import_json/`:

```bash
make capture-browser
make capture-browser-extract
```

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

### 5. Open extracted JSON in ContextBuilder

`ContextBuilder` is the local viewer/editor for extracted dialogs. Point it at `import_json/` or at another directory containing compatible dialog JSON files.

## JSON Contract

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

Any viewer or downstream tool should treat this JSON shape as the stable file-level contract.

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

## Repository Layout

- `extract_chatgpt_html.py`: converts saved ChatGPT HTML pages into normalized JSON dialog files.
- `tests/fixtures/`: public HTML/JSON regression corpus for the extractor.
- `tests/test_extract_chatgpt_html.py`: extractor regression tests.
- `tests/test_detect_lineage.py`: lineage detection tests.
- `scripts/capture_chatgpt_tab.sh`: local macOS capture helper that saves the current browser conversation HTML into `import/`.
- `scripts/browser_eval.js`: JXA bridge used by the capture script to run JavaScript in the active browser tab.
- `scripts/detect_lineage.py`: detects shared message-ID prefixes and generates ContextBuilder-compatible lineage metadata.
- `.github/workflows/release.yml`: GitHub Actions workflow that publishes minimal release bundles for `v*` tags.
- `import/`: local runtime directory for captured ChatGPT HTML.
- `import_json/`: local runtime directory for extracted JSON.
- `page_example/`: example HTML reference material.
- `pre_ideal_example_markdown/`: draft/reference markdown content.
- `EXTRACTOR_README.md`: detailed notes for the extraction flow.
- `CAPTURE_README.md`: local browser-capture manual for the legacy Mac workflow.
- `ARCHITECTURE_DECISION.md`: current extractor/viewer/capture boundary decision.

## Related Documents

- `EXTRACTOR_README.md`: extractor usage details and JSON contract notes.
- `CAPTURE_README.md`: Mac browser-capture workflow for saving live ChatGPT tabs into `import/` and `import_json/`.
- `ARCHITECTURE_DECISION.md`: practical repo split between `ChatGPTDialogs`, `ContextBuilder`, and future `capture-browser`.
- `AGENTS.md`: contributor instructions for coding style, validation, and export handling.
