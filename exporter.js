async function getAccessToken() {
  // NextAuth endpoint
  try {
    const res = await fetch("/api/auth/session", { credentials: "include" });
    if (res.ok) {
      const session = await res.json();
      if (session?.accessToken) return session.accessToken;
    }
  } catch (e) {
    console.warn("api/auth/session failed", e);
  }

  // Fallback: check multiple storage candidates
  const candidates = ["auth", "authTokens", "accessToken", "token"];
  for (const key of candidates) {
    const raw = localStorage.getItem(key) || sessionStorage.getItem(key);
    if (!raw) continue;
    try {
      const parsed = JSON.parse(raw);
      if (parsed?.accessToken) return parsed.accessToken;
      if (parsed?.token) return parsed.token;
    } catch {
      // not JSON
      if (raw.length > 20) return raw;
    }
  }

  throw new Error("Access token not found");
}

const accessToken = await getAccessToken();

(async () => {
  const authRaw = localStorage.getItem("auth");
  const accessToken = authRaw ? JSON.parse(authRaw)?.accessToken : null;
  if (!accessToken) throw new Error("Access token not found in localStorage");

  const headers = {
    "content-type": "application/json",
    authorization: `Bearer ${accessToken}`,
  };

  const download = (filename, obj) => {
    const blob = new Blob([JSON.stringify(obj, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const slugify = (s) => s.replace(/[^a-z0-9._-]+/gi, "_").replace(/^_+|_+$/g, "").slice(0, 120);

  const reconstruct = (conv) => {
    const mapping = conv.mapping || {};
    let nodeId = conv.current_node;
    const thread = [];
    const seen = new Set();

    while (nodeId && !seen.has(nodeId)) {
      seen.add(nodeId);
      const node = mapping[nodeId];
      if (!node) break;

      const msg = node.message;
      if (msg) {
        const role = msg.author?.role;
        const parts = msg.content?.parts || [];
        const text = parts.filter(Boolean).map(String).join("\n");

        thread.push({
          role,
          content: text,
          message_id: msg.id,
          create_time: msg.create_time,
        });
      }

      nodeId = node.parent;
    }

    thread.reverse();
    return thread;
  };

  const limit = 100;
  let offset = 0;
  const all = [];

  while (true) {
    const res = await fetch(`/backend-api/conversations?offset=${offset}&limit=${limit}`, {
      headers,
      credentials: "include",
    });
    if (!res.ok) throw new Error(`List failed: ${res.status}`);
    const json = await res.json();

    const items = json.items || json.data || [];
    all.push(...items);

    if (!json.has_more) break;
    offset += limit;
  }

  const matches = all;
  console.log("Conversations to export:", matches.map((c) => `${c.title} (${c.id})`));

  for (const conv of matches) {
    const res = await fetch(`/backend-api/conversation/${conv.id}`, {
      headers,
      credentials: "include",
    });
    if (!res.ok) {
      console.warn("Skip", conv.id, res.status);
      continue;
    }

    const detail = await res.json();
    const msgs = reconstruct(detail).filter((m) => m.role === "user" || m.role === "assistant");

    download(`${slugify(conv.title || conv.id)}_${conv.id}.json`, {
      title: conv.title,
      conversation_id: conv.id,
      messages: msgs,
    });
  }
})();
