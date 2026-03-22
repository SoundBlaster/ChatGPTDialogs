import json, re
from pathlib import Path

INPUT = Path("conversations.json")            # put your export file path here
OUTPUT_DIR = Path("conversation_exports")
OUTPUT_DIR.mkdir(exist_ok=True)

def slugify(title: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", title).strip("_")[:120]

def reconstruct_active_thread(conv: dict):
    mapping = conv.get("mapping", {})
    current = conv.get("current_node")
    thread = []
    visited = set()

    # Walk backward from the active leaf
    while current and current not in visited:
        visited.add(current)
        node = mapping.get(current)
        if not node:
            break

        msg = node.get("message")
        if msg:
            author = (msg.get("author") or {}).get("role")
            parts = msg.get("content", {}).get("parts") or []
            text = "\n".join(str(p) for p in parts if p)
            thread.append({
                "role": author,
                "content": text,
                "message_id": msg.get("id"),
                "create_time": msg.get("create_time"),
            })

        current = node.get("parent")

    thread.reverse()  # oldest → newest
    return thread

data = json.loads(INPUT.read_text(encoding="utf-8"))

for conv in data:
    title = conv.get("title") or ""
    messages = reconstruct_active_thread(conv)
    messages = [m for m in messages if m["role"] in ("user", "assistant")]

    out = {
        "title": title,
        "conversation_id": conv.get("conversation_id"),
        "messages": messages,
    }

    output_path = OUTPUT_DIR / f"{slugify(title)}.json"
    output_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("exported", output_path)
