const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export async function fetchReiTable() {
  const res = await fetch(`${API_BASE_URL}/api/rei-table`);
  if (!res.ok) throw new Error(`REI 계산표를 불러오지 못했습니다 (${res.status})`);
  return res.json();
}

export async function fetchCompoundProducts() {
  const res = await fetch(`${API_BASE_URL}/api/compound-products`);
  if (!res.ok) throw new Error(`농약명 정보를 불러오지 못했습니다 (${res.status})`);
  return res.json();
}

export async function sendAlarm({ chatId, targetTime, compound, crop }) {
  const res = await fetch(`${API_BASE_URL}/api/alarm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, target_time: targetTime, compound, crop }),
  });
  if (!res.ok) throw new Error(`알림 설정에 실패했습니다 (${res.status})`);
  return res.json();
}

// 챗봇 AI 도우미 (단일 백엔드의 /ai 서브앱)
export async function sendChat(message, crop) {
  const res = await fetch(`${API_BASE_URL}/ai/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, crop }),
  });
  if (!res.ok) throw new Error(`챗봇 응답을 받지 못했습니다 (${res.status})`);
  return res.json(); // { answer, sources }
}

// 결과 화면 AI 안전 해석
export async function fetchExplanation(result) {
  const res = await fetch(`${API_BASE_URL}/ai/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(result),
  });
  if (!res.ok) throw new Error(`AI 해석을 받지 못했습니다 (${res.status})`);
  return res.json(); // { explanation }
}
