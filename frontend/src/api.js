const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

export async function analyzeText(senderId, receiverId, text) {
  const res = await fetch(`${API_BASE}/analyze/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sender_id: senderId,
      receiver_id: receiverId,
      text,
    }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function analyzeImage(senderId, receiverId, file) {
  const formData = new FormData();
  formData.append("sender_id", senderId);
  formData.append("receiver_id", receiverId);
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/analyze/image`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function sendReply(senderId, receiverId) {
  const res = await fetch(`${API_BASE}/reply`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sender_id: senderId,
      receiver_id: receiverId,
    }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function resetTracking(senderId, receiverId) {
  const res = await fetch(`${API_BASE}/reset`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sender_id: senderId,
      receiver_id: receiverId,
    }),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}
