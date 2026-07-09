import { useState, useEffect, useRef } from "react";
import { Sprout, Send, MessageCircle } from "lucide-react";
import { C } from "../theme";
import { sendChat } from "../api/reiApi";

const SAMPLE_QA = [
  { q: "재출입 제한시간이 뭐예요?", a: "재출입 제한시간(REI)은 농약을 뿌린 뒤 농장에 안전하게 다시 들어갈 수 있을 때까지 기다려야 하는 시간이에요. 이 시간 안에는 잎이나 열매에 남은 농약이 피부에 닿아 건강에 해로울 수 있어요." },
  { q: "장갑 끼면 더 빨리 들어가도 되나요?", a: "보호장비(긴소매·장갑·마스크)를 착용하면 노출을 줄일 수 있지만 완전히 막아주진 못해요. 되도록 계산된 재출입 시각을 지키시고, 부득이할 때만 보호장비를 착용한 채 짧게 작업하세요." },
  { q: "비가 오면 시간이 줄어드나요?", a: "비가 오면 잎에 남은 농약이 씻겨 내려가 잔류량이 빨리 줄어들 수 있어요. 다만 정확한 감소량은 농약 종류와 강우량에 따라 달라지니, 안전을 위해 계산된 시각을 기준으로 삼는 걸 권해요." },
  { q: "딸기 수확 전에 주의할 점이 있나요?", a: "수확은 열매와 잎에 직접 닿는 작업이라 노출이 많은 편이에요. 재출입 제한시간을 꼭 지키고, 안전사용기준(수확 며칠 전까지 사용)도 함께 확인하세요." },
];

export function ChatWeb() {
  const [msgs, setMsgs] = useState([{ role: "bot", text: "안녕하세요! 농약 안전 도우미예요. 재출입 시간이나 농약 사용법이 궁금하면 편하게 물어보세요. 🌱" }]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);
  useEffect(() => { scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" }); }, [msgs]);

  const send = async (text) => {
    if (!text.trim() || busy) return;
    setMsgs(m => [...m, { role: "user", text }]); setInput(""); setBusy(true);
    try {
      const { answer, sources } = await sendChat(text);
      setMsgs(m => [...m, { role: "bot", text: answer, sources, typing: true }]);
    } catch (e) {
      // 백엔드 연결 실패 시: 준비된 예시 답변이 있으면 그걸로, 없으면 안내 문구
      const found = SAMPLE_QA.find(x => x.q === text);
      const fallback = found ? found.a : "죄송해요, 지금 답변을 가져오지 못했어요. 잠시 후 다시 시도해 주세요.";
      setMsgs(m => [...m, { role: "bot", text: fallback, typing: true }]);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="scr" style={{ padding: "44px 0 60px" }}>
      <div style={{ marginBottom: 8, fontSize: 14, fontWeight: 700, color: C.green700 }}>안전 도우미</div>
      <h1 style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 28 }}>농약 안전, 무엇이든 물어보세요</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 24, alignItems: "start" }}>
        {/* 채팅 영역 */}
        <div style={{ background: "#fff", border: `1px solid ${C.line}`, borderRadius: 22, overflow: "hidden", display: "flex", flexDirection: "column", height: 560 }}>
          <div style={{ padding: "16px 22px", borderBottom: `1px solid ${C.line}`, display: "flex", alignItems: "center", gap: 11, background: C.paper }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: C.green900, display: "grid", placeItems: "center" }}>
              <Sprout size={20} color={C.amber} />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: 15 }}>농약 안전 도우미</div>
              <div style={{ fontSize: 12, color: C.green500, fontWeight: 600, display: "flex", alignItems: "center", gap: 5 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: C.green500 }} /> 온라인
              </div>
            </div>
            <span style={{ marginLeft: "auto", fontSize: 11.5, color: C.sub, fontWeight: 600, background: C.paper2, padding: "4px 10px", borderRadius: 10 }}>데모</span>
          </div>

          <div ref={scrollRef} style={{ flex: 1, overflowY: "auto", padding: "20px 22px" }}>
            {msgs.map((m, i) => <BubbleWeb key={i} m={m} />)}
          </div>

          <div style={{ padding: "14px 18px", borderTop: `1px solid ${C.line}` }}>
            <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
              <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === "Enter" && send(input)}
                placeholder="궁금한 점을 입력하세요"
                style={{ flex: 1, border: `1.5px solid ${C.line}`, borderRadius: 24, padding: "13px 20px", fontSize: 15, outline: "none", background: C.paper }} />
              <button className="tap" onClick={() => send(input)} style={{ width: 50, height: 50, borderRadius: "50%", background: C.green700, display: "grid", placeItems: "center", flexShrink: 0 }}>
                <Send size={20} color="#fff" />
              </button>
            </div>
          </div>
        </div>

        {/* 추천 질문 사이드 */}
        <div style={{ position: "sticky", top: 92 }}>
          <div style={{ fontSize: 13, fontWeight: 800, color: C.sub, marginBottom: 12 }}>추천 질문</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 9 }}>
            {SAMPLE_QA.map(x => (
              <button key={x.q} className="tap card" onClick={() => send(x.q)}
                style={{ textAlign: "left", background: "#fff", border: `1px solid ${C.line}`, borderRadius: 14, padding: "14px 16px", fontSize: 13.5, fontWeight: 600, color: C.ink, display: "flex", alignItems: "center", gap: 10, lineHeight: 1.4 }}>
                <MessageCircle size={16} color={C.green500} style={{ flexShrink: 0 }} />
                {x.q}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function BubbleWeb({ m }) {
  const bot = m.role === "bot";
  const [shown, setShown] = useState(m.typing ? "" : m.text);
  useEffect(() => {
    if (!m.typing) return;
    let i = 0; const id = setInterval(() => { i += 2; setShown(m.text.slice(0, i)); if (i >= m.text.length) clearInterval(id); }, 14);
    return () => clearInterval(id);
  }, []);
  return (
    <div style={{ display: "flex", justifyContent: bot ? "flex-start" : "flex-end", marginBottom: 14 }}>
      {bot && <div style={{ width: 34, height: 34, borderRadius: 10, background: C.green900, display: "grid", placeItems: "center", marginRight: 10, flexShrink: 0, alignSelf: "flex-end" }}><Sprout size={19} color={C.amber} /></div>}
      <div style={{ maxWidth: "72%", padding: "13px 18px", borderRadius: 18, background: bot ? C.paper : C.green700, color: bot ? C.ink : "#fff", border: bot ? `1px solid ${C.line}` : "none", borderBottomLeftRadius: bot ? 4 : 18, borderBottomRightRadius: bot ? 18 : 4, fontSize: 15, lineHeight: 1.65, fontWeight: bot ? 500 : 600 }}>
        {shown}
        {bot && m.sources?.length > 0 && (
          <div style={{ marginTop: 8, fontSize: 11.5, color: C.sub, fontWeight: 600 }}>
            출처: {m.sources.join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}
