/**
 * Complete ChatGPTDialogs Conversation Exporter
 * Extracts ALL messages (not just active thread) from ChatGPT conversations
 * Run in browser console on chatgpt.com
 */

(async () => {
  const authRaw = localStorage.getItem("auth");
  const accessToken = authRaw ? JSON.parse(authRaw)?.accessToken : null;
  if (!accessToken) throw new Error("Access token not found");

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

  /**
   * Extract ALL messages from conversation mapping (not just active thread)
   */
  const extractAllMessages = (conv) => {
    const mapping = conv.mapping || {};
    const messages = [];
    const seen = new Set();

    // Visit all nodes in mapping
    for (const [nodeId, node] of Object.entries(mapping)) {
      if (seen.has(nodeId) || !node?.message) continue;
      seen.add(nodeId);

      const msg = node.message;
      const role = msg.author?.role;
      const parts = msg.content?.parts || [];
      const text = parts.filter(Boolean).map(String).join("\n");

      if (role === "user" || role === "assistant") {
        messages.push({
          id: msg.id,
          role,
          content: text,
          create_time: msg.create_time,
          node_id: nodeId,
        });
      }
    }

    // Sort by creation time
    messages.sort((a, b) => new Date(a.create_time) - new Date(b.create_time));
    return messages;
  };

  // Fetch all conversations
  const limit = 100;
  let offset = 0;
  const all = [];

  console.log("Fetching all conversations...");
  while (true) {
    const res = await fetch(`/backend-api/conversations?offset=${offset}&limit=${limit}`, {
      headers,
      credentials: "include",
    });
    if (!res.ok) throw new Error(`Failed: ${res.status}`);
    const json = await res.json();
    const items = json.items || json.data || [];
    all.push(...items);
    if (!json.has_more) break;
    offset += limit;
  }

  const matches = all;
  console.log(`Found ${matches.length} conversations`);

  // Export each conversation
  for (const conv of matches) {
    console.log(`Fetching: ${conv.title}`);
    const res = await fetch(`/backend-api/conversation/${conv.id}`, {
      headers,
      credentials: "include",
    });
    if (!res.ok) {
      console.warn(`Skip ${conv.title}: ${res.status}`);
      continue;
    }

    const detail = await res.json();
    const messages = extractAllMessages(detail);

    const data = {
      title: conv.title,
      conversation_id: conv.id,
      message_count: messages.length,
      created_at: conv.create_time,
      messages,
    };

    download(`${slugify(conv.title)}_${conv.id}.json`, data);
    console.log(`✓ Exported: ${conv.title} (${messages.length} messages)`);
  }

  console.log("Export complete!");
})();
