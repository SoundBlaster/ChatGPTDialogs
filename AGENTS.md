# Repository Guidelines

## Project Structure & Module Organization

This repository stores ChatGPTDialogs source material, extraction utilities, and exported conversation artifacts.

- `README.md`: project overview.
- `EXTRACTOR_README.md`: usage notes for the extraction scripts.
- `conversation_extractor.py`: Python script that reads `conversations.json` and writes normalized exports to `conversation_exports/`.
- `exporter.js`, `active_thread_exporter.js`, `complete_exporter.js`: browser-side extraction scripts.
- `exports/`: checked-in conversation exports and status documents, such as `MANIFEST.json`, `EXTRACTION_STATUS.md`, and per-conversation `.json` files.
- `page_example/` and `pre_ideal_example_markdown/`: example reference material.

## Build, Test, and Development Commands

There is no package manager or compiled build step. Use the scripts directly:

- `python conversation_extractor.py`: converts a ChatGPT export file named `conversations.json` into `conversation_exports/`.
- Paste `complete_exporter.js` into the browser console on ChatGPT to generate conversation JSON files.
- `git status --short`: verify only the intended export or documentation files changed.

## Coding Style & Naming Conventions

- Use ASCII unless a file already contains Russian or other non-ASCII text.
- Python: 4-space indentation, small focused functions, standard library only when practical.
- JavaScript: prefer clear, browser-console-friendly code with explicit variable names.
- File naming for exports should follow `slugified_title.json` or `{slug}_{conversation_id}.json`, matching the existing `exports/` contents.

## Testing Guidelines

No automated test suite is defined. Validate changes manually:

- Run the extractor against a known `conversations.json`.
- Confirm the output JSON parses and contains `title`, `conversation_id`, and `messages`.
- Spot-check the `exports/` status files if you update extraction progress.

## Commit & Pull Request Guidelines

Git history uses short, imperative commit messages such as `Add page example`. Keep commits focused and present tense.

For pull requests:

- Summarize what changed and why.
- Mention any updated export files or scripts.
- Include screenshots only if you changed rendered markdown or example content.

## Contributor Notes

Do not overwrite existing exported data unless that is the explicit goal. When adding new exports, keep the manifest and status documents in sync with the new files.
