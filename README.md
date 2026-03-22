# ChatGPTDialogs

ChatGPTDialogs stores source material, extraction utilities, and exported conversation artifacts for the ChatGPTDialogs project.

## Repository Layout

- `conversation_extractor.py`: Reads a ChatGPT `conversations.json` export and reconstructs the active conversation thread into normalized JSON files.
- `extract_chatgpt_html.py`: Converts saved ChatGPT web HTML pages into normalized JSON dialog files.
- `complete_exporter.js`: Recommended browser-console exporter. Fetches conversations from ChatGPT and exports all user/assistant messages, not just the active branch.
- `active_thread_exporter.js`: Older browser-console exporter that reconstructs only the active branch.
- `exporter.js`: Earlier exporter variant kept for reference.
- `scripts/capture_chatgpt_tab.sh`: Mac capture helper that saves the current browser conversation HTML into `import/`.
- `viewer/`: Local folder-based viewer/editor for dialogs in `import_json/`.
- `exports/`: Checked-in conversation exports plus status and manifest files.
- `import/`: Saved ChatGPT HTML pages captured from the browser.
- `import_json/`: JSON files generated from `import/`.
- `page_example/`: Example HTML reference material.
- `pre_ideal_example_markdown/`: Draft/reference markdown content.
- `EXTRACTOR_README.md`: Detailed notes for the extraction scripts.
- `CAPTURE_README.md`: Browser-capture manual for the Mac automation flow.

## Main Workflows

### 1. Browser export from ChatGPT

Use this when you want per-conversation JSON files directly from ChatGPT:

1. Open the target ChatGPT project page.
2. Open DevTools and switch to the Console tab.
3. Paste the contents of `complete_exporter.js`.
4. Wait for the downloads to finish.
5. Move the downloaded JSON files into `exports/` if they should be checked in.

`complete_exporter.js` is the preferred option because it exports all mapped messages and includes metadata such as `conversation_id`, `message_count`, and timestamps.

### 2. Capture the current browser tab into `import/`

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

### 3. Post-process a full ChatGPT export

Use this when you already have a `conversations.json` export:

```bash
python conversation_extractor.py
```

This writes normalized files into `conversation_exports/`. The script reconstructs only the active thread of each conversation.

## Expected Data Shape

Exported conversation files are expected to contain:

```json
{
  "title": "Conversation Title",
  "conversation_id": "uuid",
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

Some browser-exported files also include fields such as `message_count`, `created_at`, `node_id`, or `url`.

Saved-HTML-derived files typically include:

```json
{
  "title": "Conversation Title",
  "source_file": "/absolute/path/to/file.html",
  "message_count": 42,
  "messages": [
    {
      "role": "user",
      "content": "..."
    }
  ]
}
```

## Working Conventions

- There is no package manager, build step, or automated test suite.
- Prefer ASCII unless the file already contains non-ASCII text.
- Do not overwrite checked-in exports unless that is the explicit goal.
- When adding exports to `exports/`, keep `exports/MANIFEST.json` and `exports/EXTRACTION_STATUS.md` in sync.
- Before finishing work, verify the worktree with:

```bash
git status --short
```

## Current Caveats

- The repo has multiple extraction paths: browser API export, full-export post-processing, and older manual extraction notes. Check which one matches your task before editing scripts or metadata.
- `conversation_extractor.py` writes to `conversation_exports/`, while checked-in artifacts live in `exports/`.
- Browser capture on macOS depends on Automation permissions for the terminal app controlling the browser.
- Some checked-in status files may drift from the actual exported filenames or counts, so verify the contents of `exports/` instead of trusting a single status document blindly.

## Related Documents

- `EXTRACTOR_README.md`: script usage details and historical notes.
- `CAPTURE_README.md`: Mac browser-capture workflow for saving live ChatGPT tabs into `import/` and `import_json/`.
- `ARCHITECTURE_DECISION.md`: functional module boundaries and recommended future repo split.
- `AGENTS.md`: contributor instructions for coding style, validation, and export handling.
- `exports/README.md`: summary of extracted conversations and pending work.
