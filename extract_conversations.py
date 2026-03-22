#!/usr/bin/env python3
"""
Complete ChatGPTDialogs Conversation Extractor
Parses raw ChatGPT conversations and structures them as JSON
"""

import json
import re
from pathlib import Path
from datetime import datetime


def parse_conversation_text(text: str, title: str) -> list:
    """Parse raw ChatGPT conversation text into structured messages."""
    messages = []

    # Split by "Вы сказали:" and "ChatGPT сказал:"
    # Pattern: "Вы сказали:CONTENT" or "ChatGPT сказал:CONTENT"

    pattern = r'(Вы сказали:|ChatGPT сказал:)'
    parts = re.split(pattern, text)

    i = 0
    while i < len(parts):
        if i + 1 < len(parts):
            speaker_text = parts[i].strip()
            content = parts[i + 1].strip() if i + 1 < len(parts) else ""

            if speaker_text == "Вы сказали:":
                role = "user"
            elif speaker_text == "ChatGPT сказал:":
                role = "assistant"
            else:
                i += 2
                continue

            # Clean up content - remove trailing metadata
            content = re.sub(r'(ИсточникиWindow\.__oai.*$)', '', content, flags=re.DOTALL)
            content = re.sub(r'(Источники.*$)', '', content, flags=re.DOTALL)
            content = re.sub(r'(ChatGPT может допускать.*$)', '', content, flags=re.DOTALL)
            content = content.strip()

            if content:
                messages.append({
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                })

        i += 2

    return messages


def extract_from_raw_text(text_content: str, title: str, conv_id: str) -> dict:
    """Extract conversation from raw page text."""
    messages = parse_conversation_text(text_content, title)

    return {
        "title": title,
        "conversation_id": conv_id,
        "extracted_at": datetime.now().isoformat(),
        "message_count": len(messages),
        "messages": messages
    }


def main():
    """Main extraction pipeline."""
    # This would be called with raw text from browser
    # For now, it's a template
    print("Converter ready. Use with ChatGPT conversation text.")


if __name__ == "__main__":
    main()
