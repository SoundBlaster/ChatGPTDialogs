# Architecture Decision: Split Extractor, Viewer, and Capture Boundaries

## Status

Accepted for the current repository split.

## Context

The original repository mixed three different concerns:

- browser capture on macOS
- HTML-to-dialog extraction
- local viewer API and viewer web UI

Those parts change for different reasons and should not be treated as one product surface.

The practical problem is not scale. It is boundary drift:

- browser automation gets coupled to viewer behavior
- extractor changes get hidden inside UI repos
- the JSON contract becomes implicit instead of explicit
- a viewer repo starts inheriting platform-specific capture code it does not need

## Decision

Split by function and by rate of change:

1. `ChatGPTDialogs` is the extractor repository.
   It owns `extract-html`, the dialog JSON contract, regression fixtures, and minimal local import workflows.

2. `ContextBuilder` is the viewer repository.
   It owns `viewer-web` and `viewer-api` for already extracted JSON dialogs.

3. `capture-browser` is a separate concern.
   Do not move browser-capture code into `ContextBuilder`.
   It may remain temporarily in `ChatGPTDialogs` history or be extracted later into a separate private repository or module.

## Why This Boundary Is Correct

- extractor logic changes when the ChatGPT DOM changes
- viewer logic changes when editing UX changes
- browser capture changes when browsers, permissions, or automation APIs change
- the dialog JSON contract should change the least

That means:

- `ChatGPTDialogs` should stay extractor-first
- `ContextBuilder` should stay viewer-first
- browser capture should not leak into the viewer repo

## Functional Module Mapping

The conceptual modules still matter, but they map to repositories differently:

### `dialog-domain`

Purpose:

- define the stable dialog JSON contract shared between repos

Lives primarily in:

- `ChatGPTDialogs` documentation and extractor output

### `extract-html`

Purpose:

- transform saved ChatGPT HTML into normalized dialog JSON

Lives in:

- `ChatGPTDialogs`

### `viewer-api`

Purpose:

- expose list/read/write/delete operations for dialog JSON files

Lives in:

- `ContextBuilder`

### `viewer-web`

Purpose:

- browse and edit extracted dialogs through a local UI

Lives in:

- `ContextBuilder`

### `capture-browser`

Purpose:

- capture raw HTML from a live browser tab

Lives in:

- outside `ContextBuilder`
- temporarily in `ChatGPTDialogs` only until it gets its own home

## Interface Contract To Freeze Early

`ContextBuilder` should read any directory containing JSON files with this minimum shape:

### `Dialog`

- `title`
- `source_file`
- `message_count`
- `messages[]`

### `Message`

- `role`
- `content`
- optional `message_id`
- optional `turn_id`
- optional `source`

This file-level contract is the integration point between the two repositories.

## Practical Repo Split

### Keep in `ChatGPTDialogs`

- `extract_chatgpt_html.py`
- `tests/fixtures/`
- `tests/test_extract_chatgpt_html.py`
- documentation about the HTML-to-JSON extraction flow
- minimal local import workflow around `import/` and `import_json/`

### Move to `ContextBuilder`

- `viewer/server.py`
- `viewer/index.html`
- viewer usage documentation
- local viewer-oriented `Makefile` or CLI entrypoints

### Do Not Move to `ContextBuilder`

- `scripts/capture_chatgpt_tab.sh`
- `scripts/browser_eval.js`
- browser-automation-specific docs and assumptions

## Current File Mapping

- `extract_chatgpt_html.py`
  - stays in `ChatGPTDialogs`
  - remains the main extractor entry point

- `tests/fixtures/` and `tests/test_extract_chatgpt_html.py`
  - stay in `ChatGPTDialogs`
  - remain the regression corpus and extractor test suite

- `viewer/server.py`
  - moves to `ContextBuilder`
  - represents `viewer-api`

- `viewer/index.html`
  - moves to `ContextBuilder`
  - represents `viewer-web`

- `scripts/capture_chatgpt_tab.sh` and `scripts/browser_eval.js`
  - stay out of `ContextBuilder`
  - belong to a later `capture-browser` extraction path

## Operational Contract Between Repositories

- `ChatGPTDialogs` produces JSON files in `import_json/` or another chosen output directory
- `ContextBuilder` reads JSON files from an explicitly configured directory
- the default collaboration path can be `ChatGPTDialogs/import_json/`, but the viewer must not hardcode that repository

## What Not To Do

- do not put browser capture into `ContextBuilder`
- do not make the viewer depend on raw HTML parsing
- do not make extractor tests depend on viewer code
- do not duplicate the dialog contract informally across repos without documenting it
