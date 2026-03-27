#!/usr/bin/env python3
"""Detect shared message-ID prefixes across exported ChatGPT JSON files
and generate a ContextBuilder-compatible lineage manifest.

Usage:
    python scripts/detect_lineage.py [DIRECTORY]

DIRECTORY defaults to import_json/ relative to the repo root.

Output: writes lineage.json into DIRECTORY with detected relationships.
"""

import json
import os
import sys


def slug_from_filename(filename):
    """Derive a conversation_id slug from a JSON filename."""
    return os.path.splitext(os.path.basename(filename))[0]


def load_message_ids(directory):
    """Load message_id sequences from every JSON file in *directory*.

    Returns {basename: [message_id, ...]} for files that have at least one
    message with a message_id field.
    """
    index = {}
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        path = os.path.join(directory, name)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (json.JSONDecodeError, OSError):
            continue
        ids = [
            m["message_id"]
            for m in data.get("messages", [])
            if m.get("message_id")
        ]
        if ids:
            index[name] = ids
    return index


def shared_prefix_length(seq_a, seq_b):
    """Return the number of leading elements shared by two sequences."""
    length = 0
    for a, b in zip(seq_a, seq_b):
        if a == b:
            length += 1
        else:
            break
    return length


def detect_lineage(index):
    """Build lineage metadata from a message-ID index.

    For every file, the *parent* is the file with the longest message
    sequence that is a proper prefix of this file's sequence.  Files
    with no such parent are roots.

    Returns a list of conversation records suitable for lineage.json.
    """
    # Sort names by sequence length so shorter (potential parents) come first.
    names_by_length = sorted(index, key=lambda n: len(index[n]))

    # For each file find the longest proper-prefix file.
    parent_of = {}  # child_name -> (parent_name, branch_message_id)

    for i, child in enumerate(names_by_length):
        child_ids = index[child]
        best_parent = None
        best_len = 0
        for j in range(i - 1, -1, -1):
            candidate = names_by_length[j]
            cand_ids = index[candidate]
            cand_len = len(cand_ids)
            if cand_len <= best_len:
                continue  # can't beat current best
            if cand_len >= len(child_ids):
                continue  # not a *proper* prefix
            # Check if candidate is a prefix of child.
            if child_ids[:cand_len] == cand_ids:
                best_parent = candidate
                best_len = cand_len
        if best_parent is not None:
            branch_message_id = index[best_parent][-1]
            parent_of[child] = (best_parent, branch_message_id)

    # Build output records.
    conversations = []
    for name in sorted(index):
        slug = slug_from_filename(name)
        record = {
            "conversation_id": slug,
            "file": name,
            "message_count": len(index[name]),
        }
        if name in parent_of:
            pname, branch_mid = parent_of[name]
            record["lineage"] = {
                "parents": [
                    {
                        "conversation_id": slug_from_filename(pname),
                        "message_id": branch_mid,
                        "link_type": "branch",
                    }
                ]
            }
        conversations.append(record)
    return conversations


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    directory = sys.argv[1] if len(sys.argv) > 1 else os.path.join(repo_root, "import_json")

    if not os.path.isdir(directory):
        print(f"Error: directory not found: {directory}", file=sys.stderr)
        sys.exit(1)

    index = load_message_ids(directory)
    if not index:
        print("No JSON files with message_id fields found.", file=sys.stderr)
        sys.exit(0)

    conversations = detect_lineage(index)
    roots = [c for c in conversations if "lineage" not in c]
    branches = [c for c in conversations if "lineage" in c]

    output_path = os.path.join(directory, "lineage.json")
    manifest = {
        "generated_by": "detect_lineage.py",
        "file_count": len(conversations),
        "root_count": len(roots),
        "branch_count": len(branches),
        "conversations": conversations,
    }
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    print(f"Lineage manifest written to {output_path}")
    print(f"  {len(conversations)} conversations, {len(roots)} roots, {len(branches)} branches")


if __name__ == "__main__":
    main()
