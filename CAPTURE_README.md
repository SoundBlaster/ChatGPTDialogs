# Browser Capture Manual

This document describes the Mac-side capture workflow for saving the current ChatGPT browser tab into `import/` and optionally converting it into JSON in `import_json/`.

The extracted JSON is intended to be consumed by the separate `ContextBuilder` viewer repository or by any other tool that follows the same dialog JSON contract.

## What These Scripts Do

- `scripts/capture_chatgpt_tab.sh`
  - detects the front browser or picks a running supported browser
  - brings that browser to the front
  - waits briefly for focus to settle
  - runs JavaScript in the active tab through browser automation
  - auto-scrolls the page to load more conversation content
  - saves the current page HTML into `import/`
  - optionally runs `extract_chatgpt_html.py`
  - sends a macOS notification when capture finishes

- `scripts/browser_eval.js`
  - JXA browser bridge used by the shell script
  - evaluates JavaScript in the active tab of a supported browser

- `Makefile`
  - provides the entry points:
    - `make capture-browser`
    - `make capture-browser-extract`
    - `make test`

## Supported Browsers

- `Safari`
- `Google Chrome`
- `Brave Browser`
- `Chromium`

The script prefers the frontmost supported browser. If Terminal or another app is frontmost, it will try to find a running supported browser automatically. If several supported browsers are running, it may ask you to choose one.

## Quick Start

1. Open the target ChatGPT conversation in one of the supported browsers.
2. Run:

```bash
cd /Users/username/Development/GitHub/ChatGPTDialogs
make capture-browser
```

If Terminal is frontmost, the script will try to use a running supported browser automatically. If several supported browsers are running, it may ask you to choose one.

This saves a new `.html` file into:

```text
/Users/username/Development/GitHub/ChatGPTDialogs/import
```

If you also want JSON immediately:

```bash
make capture-browser-extract
```

This saves:

- HTML to `import/`
- JSON to `import_json/`

These are local runtime directories. Checked-in public regression fixtures live under `tests/fixtures/`.

At the end of the run, the script also emits:

- a terminal bell
- a macOS notification

## Output Naming

The HTML filename is derived from the browser tab title.

Unicode letters are preserved, so Cyrillic titles remain readable instead of collapsing into short ASCII fragments.

Example:

```text
Агентная_Операционная_Система_-_Риски_для_PRD_рынка.html
```

If a file with the same name already exists, the script appends a timestamp.

## How The Capture Works

The shell script performs these steps:

1. Detect the frontmost application.
2. If needed, select a running supported browser.
3. Activate that browser.
4. Wait briefly so the browser window becomes the active target.
5. Execute JavaScript in the active tab to scroll to the bottom repeatedly.
6. Stop scrolling when the page height stops growing.
7. Read:
   - `document.title`
   - `location.href`
   - `document.documentElement.outerHTML`
8. Save the HTML into `import/`.
9. If `AUTO_EXTRACT=1`, run the Python extractor and write JSON into `import_json/`.

## Environment Variables

You can tune behavior without editing the script.

### `BROWSER`

Force the target browser instead of using automatic selection.

Example:

```bash
BROWSER="Safari" make capture-browser
```

### `AUTO_EXTRACT`

Used internally by `make capture-browser-extract`, but can also be set directly.

Example:

```bash
AUTO_EXTRACT=1 bash scripts/capture_chatgpt_tab.sh
```

### `SCROLL_PAUSE`

Seconds to wait between scroll attempts.

Example:

```bash
SCROLL_PAUSE=2 make capture-browser
```

### `ACTIVATION_DELAY`

Seconds to wait after switching focus to the chosen browser.

Example:

```bash
ACTIVATION_DELAY=1.5 make capture-browser
```

### `MAX_SCROLLS`

Maximum number of scroll iterations before capture completes.

Example:

```bash
MAX_SCROLLS=30 make capture-browser
```

### `NOTIFY`

Enable or disable the completion notification.

Example:

```bash
NOTIFY=0 make capture-browser
```

Default:

```text
NOTIFY=1
```

## Permissions On macOS

The first time you run the capture flow, macOS may ask for permission to control the browser.

Typical requirement:

- allow Terminal, iTerm, or Codex to control the target browser through Automation

If capture fails because of permissions:

1. Open `System Settings`
2. Go to `Privacy & Security`
3. Check `Automation`
4. Ensure your terminal app is allowed to control the browser

## Safari-Specific Requirement

If you use `Safari`, one extra setting is required.

Safari must allow JavaScript execution from automation events.

If this is not enabled, capture will fail with an error similar to:

```text
Safari JavaScript evaluation failed: You must enable 'Allow JavaScript from Apple Events' in the Developer section of Safari Settings to use 'do JavaScript'.
```

Enable it like this:

1. Open `Safari`
2. Open `Safari > Settings`
3. Open the `Developer` tab
4. Enable `Allow JavaScript from Apple Events`

If you do not see the `Developer` tab, enable Safari developer tools first and then return to Settings.

## Troubleshooting

### Browser is not detected

Symptom:

```text
Unsupported or non-browser front app: ...
```

Fix:

- start a supported browser with the target ChatGPT tab open
- or run with `BROWSER="Safari"` or another supported browser
- or let the script show a browser picker if several browsers are open

### Not all messages are captured

Cause:

- ChatGPT had not rendered the full conversation yet

Fix:

- increase scrolling:

```bash
MAX_SCROLLS=40 SCROLL_PAUSE=2 make capture-browser
```

### HTML captured but JSON missing

Cause:

- you ran `make capture-browser`, not the extract variant

Fix:

```bash
make capture-browser-extract
```

or later:

```bash
make extract-all
```

### Browser automation fails

Possible causes:

- macOS Automation permission denied
- browser has no front window
- browser focus changed too slowly
- browser scripting behavior differs between versions
- Safari does not allow JavaScript from Apple Events

Start with:

```bash
make capture-browser
```

If the shell prints a browser-control error, fix permissions first.

If the wrong app stays active, try:

```bash
ACTIVATION_DELAY=2 make capture-browser
```

If Safari reports:

```text
You must enable 'Allow JavaScript from Apple Events'
```

enable that Safari setting and retry, or use another supported browser such as `Google Chrome` or `Brave Browser`.

## Semi-Automatic Option: Automator Quick Action

If you want a keyboard-triggered capture on your Mac, create an Automator Quick Action that runs:

```bash
cd /Users/username/Development/GitHub/ChatGPTDialogs
make capture-browser-extract
```

Suggested setup:

1. Open `Automator`
2. Create `Quick Action`
3. Set `Workflow receives` to `no input`
4. Add `Run Shell Script`
5. Paste the command above
6. Save as something like `Capture ChatGPT To ChatGPTDialogs`

Then assign a keyboard shortcut in:

- `System Settings`
- `Keyboard`
- `Keyboard Shortcuts`
- `Services`

## Related Commands

After capture and extraction:

```bash
cd /path/to/ContextBuilder
make serve DIALOG_DIR=/Users/username/Development/GitHub/ChatGPTDialogs/import_json PORT=9000
```

Then open:

```text
http://localhost:9000/viewer/index.html
```

This lets you browse the JSON files in `import_json/`, branch dialogs, edit them, and save new files through the separate viewer repository.

To verify extractor behavior against the checked-in public corpus:

```bash
make test
```
