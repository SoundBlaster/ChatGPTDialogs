#!/usr/bin/env python3
"""Extract ChatGPT dialogs from a saved web HTML page."""

from __future__ import annotations

import argparse
import json
import re
from html import unescape
from pathlib import Path


TURN_START_RE = re.compile(r"<section\b(?=[^>]*data-testid=\"conversation-turn-\d+\")", re.IGNORECASE)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>", re.DOTALL)
BREAK_TAG_RE = re.compile(r"<(?:br|/p|/div|/li|/pre|/ol|/ul|/blockquote|/h[1-6])\b[^>]*>", re.IGNORECASE)
LIST_ITEM_RE = re.compile(r"<li\b[^>]*>", re.IGNORECASE)
CONTENT_BLOCK_TAG_RE = re.compile(r"<(div|pre)\b[^>]*>", re.IGNORECASE)


def get_attr(tag_html: str, name: str) -> str | None:
    pattern = re.compile(rf'{re.escape(name)}="([^"]*)"')
    match = pattern.search(tag_html)
    return match.group(1) if match else None


def clean_text(text: str) -> str:
    text = unescape(text)
    text = text.replace("\xa0", " ")
    text = text.replace("\u200b", "")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def strip_html(fragment: str) -> str:
    paragraph_marker = "___CHATGPT_PARA___"
    list_marker = "___CHATGPT_LIST___"
    fragment = re.sub(r"<(script|style|svg|button)\b.*?</\1>", "", fragment, flags=re.IGNORECASE | re.DOTALL)
    fragment = LIST_ITEM_RE.sub(f"{list_marker}", fragment)
    fragment = BREAK_TAG_RE.sub(f"{paragraph_marker}", fragment)
    fragment = TAG_RE.sub("", fragment)
    fragment = unescape(fragment)
    fragment = fragment.replace("\xa0", " ")
    fragment = fragment.replace("\u200b", "")
    fragment = re.sub(r"\s+", " ", fragment)
    fragment = fragment.replace(paragraph_marker, "\n\n")
    fragment = fragment.replace(list_marker, "\n- ")
    fragment = re.sub(r" *\n *", "\n", fragment)
    fragment = re.sub(r"\n{3,}", "\n\n", fragment)
    return fragment.strip()


def find_matching_section_end(html: str, start: int) -> int:
    pos = start
    depth = 0
    tag_re = re.compile(r"</?section\b[^>]*>", re.IGNORECASE)
    while True:
        match = tag_re.search(html, pos)
        if not match:
            return len(html)
        tag = match.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        else:
            depth += 1
        pos = match.end()


def find_matching_tag_end(html: str, start: int, tag_name: str) -> int:
    pos = start
    depth = 0
    tag_re = re.compile(rf"</?{re.escape(tag_name)}\b[^>]*>", re.IGNORECASE)
    while True:
        match = tag_re.search(html, pos)
        if not match:
            return len(html)

        tag = match.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return match.end()
        elif not tag.endswith("/>"):
            depth += 1

        pos = match.end()


def extract_message_html(block: str, role: str) -> tuple[str | None, str]:
    message_re = re.compile(
        rf"<div\b(?=[^>]*data-message-author-role=\"{re.escape(role)}\")[^>]*>",
        re.IGNORECASE,
    )
    message_match = message_re.search(block)
    if not message_match:
        return None, ""

    message_start = message_match.start()
    message_tag_end = message_match.end()
    message_id = get_attr(message_match.group(0), "data-message-id")

    depth = 1
    pos = message_tag_end
    div_tag_re = re.compile(r"</?div\b[^>]*>", re.IGNORECASE)
    while depth:
        match = div_tag_re.search(block, pos)
        if not match:
            pos = len(block)
            break
        if match.group(0).startswith("</"):
            depth -= 1
        else:
            depth += 1
        pos = match.end()

    return message_id, block[message_start:pos]


def collect_content_blocks(message_html: str, class_markers: tuple[str, ...]) -> list[str]:
    blocks: list[tuple[int, int, str]] = []

    for match in CONTENT_BLOCK_TAG_RE.finditer(message_html):
        tag_html = match.group(0)
        class_attr = get_attr(tag_html, "class") or ""
        if not any(marker in class_attr for marker in class_markers):
            continue

        start = match.start()
        end = find_matching_tag_end(message_html, start, match.group(1))
        if any(existing_start <= start and end <= existing_end for existing_start, existing_end, _ in blocks):
            continue

        blocks.append((start, end, message_html[start:end]))

    return [block_html for _, _, block_html in blocks]


def extract_content_fragments(message_html: str) -> list[str]:
    fragments: list[str] = []

    for block_html in collect_content_blocks(message_html, ("markdown", "whitespace-pre-wrap")):
        text = strip_html(block_html)
        if text:
            fragments.append(text)

    if fragments:
        return fragments

    for block_html in collect_content_blocks(message_html, ("cm-content",)):
        text = strip_html(block_html)
        if text:
            fragments.append(text)

    if fragments:
        return fragments

    fallback = strip_html(message_html)
    return [fallback] if fallback else []


def extract_html(input_path: Path) -> dict:
    html = input_path.read_text(encoding="utf-8", errors="ignore")
    title_match = TITLE_RE.search(html)
    title = clean_text(title_match.group(1)) if title_match else input_path.stem

    messages: list[dict] = []
    starts = [match.start() for match in TURN_START_RE.finditer(html)]
    for start in starts:
        tag_end = html.find(">", start)
        if tag_end == -1:
            continue
        opening_tag = html[start : tag_end + 1]
        role = get_attr(opening_tag, "data-turn")
        if role not in {"user", "assistant"}:
            continue

        end = find_matching_section_end(html, start)
        block = html[start:end]
        message_id, message_html = extract_message_html(block, role)
        fragments = extract_content_fragments(message_html)
        content = "\n\n".join(fragment for fragment in fragments if fragment)
        content = clean_text(content)
        if not content:
            continue

        messages.append(
            {
                "role": role,
                "turn_id": get_attr(opening_tag, "data-turn-id"),
                "message_id": message_id,
                "source": get_attr(opening_tag, "data-testid"),
                "content": content,
            }
        )

    return {
        "title": title,
        "source_file": str(input_path.resolve()),
        "message_count": len(messages),
        "messages": messages,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_html", type=Path, help="Path to saved ChatGPT HTML page")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output JSON path. Defaults to <input>.json next to the source file.",
    )
    args = parser.parse_args()

    output_path = args.output or args.input_html.with_suffix(".json")
    result = extract_html(args.input_html)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Extracted {result['message_count']} messages to {output_path}")


if __name__ == "__main__":
    main()
