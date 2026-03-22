# Repository Guidelines

## Project Structure & Module Organization

This repository stores ChatGPTDialogs source material, extraction utilities, and exported conversation artifacts.

- `README.md`: project overview.
- `EXTRACTOR_README.md`: usage notes for the extraction scripts.
- `extract_chatgpt_html.py`: Python script that converts saved ChatGPT HTML pages into normalized JSON.
- `scripts/capture_chatgpt_tab.sh` and `scripts/browser_eval.js`: browser-capture workflow for the active ChatGPT tab.
- `viewer/server.py`: local viewer server for extracted dialogs.
- `tests/fixtures/`: checked-in public HTML/JSON regression corpus for the extractor.
- `import/` and `import_json/`: local runtime directories for captures and extracted JSON.
- `exports/`: optional checked-in conversation exports.
- `page_example/` and `pre_ideal_example_markdown/`: example reference material.

## Build, Test, and Development Commands

There is no package manager or compiled build step. Use the scripts directly:

- `make capture-browser`: captures the active ChatGPT browser tab into `import/`.
- `make capture-browser-extract`: captures the active browser tab and writes extracted JSON into `import_json/`.
- `make serve-viewer`: starts the local viewer for extracted dialogs.
- `make test`: runs the extractor regression suite against checked-in fixtures.
- `git status --short`: verify only the intended export or documentation files changed.

## Coding Style & Naming Conventions

- Use ASCII unless a file already contains Russian or other non-ASCII text.
- Python: 4-space indentation, small focused functions, standard library only when practical.
- JavaScript: prefer clear browser-automation-friendly code with explicit variable names.
- File naming for generated artifacts should follow the current title-derived slug format used in `import/` and `import_json/`.

## Testing Guidelines

Validate changes with the checked-in regression corpus:

- Run `make test`.
- If you change capture behavior, also run `make capture-browser-extract` against a known ChatGPT page.
- Confirm the output JSON parses and contains `title`, `source_file`, `message_count`, and `messages`.

## Commit & Pull Request Guidelines

Git history uses short, imperative commit messages such as `Add page example`. Keep commits focused and present tense.

For pull requests:

- Summarize what changed and why.
- Mention any updated export files or scripts.
- Include screenshots only if you changed rendered markdown or example content.

## Contributor Notes

Do not overwrite existing exported data unless that is the explicit goal. Keep local runtime output in `import/` and `import_json/`; add only stable public fixtures under `tests/fixtures/`.
