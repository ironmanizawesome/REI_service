import { useState, useEffect } from "react";
import { Sprout, Check, Bell } from "lucide-react";
import { C } from "../theme";
import { fetchReiTable, fetchCompoundProducts, sendAlarm } from "../api/reiApi";
import { ParamRow } from "./shared/ParamRow";

const TASK_OPTIONS = [
  { key: "수확", desc: "열매 따기 · 접촉 많음" },
  { key: "예찰", desc: "병해충 살펴보기" },
];

const PPE_OPTIONS = ["없음", "작업복만", "작업복+장갑"];

const RING_MAX_HOURS = 96; // 게이지가 꽉 차는 기준(4일). 이보다 길면 숫자로만 표시.

function fmtDateTime(d) {
  return `${d.getMonth() + 1}월 ${d.getDate()}일 ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

function toDatetimeLocalValue(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

function levelOf(reiHours) {
  if (reiHours <= 0) return { key: "none", c: C.green500, t: "즉시", label: "지금 바로 재출입 가능" };
  if (reiHours <= 12) return { key: "low", c: C.green500, t: "낮음", label: "비교적 짧은 편" };
  if (reiHours <= 24) return { key: "mid", c: C.amber, t: "보통", label: "평균 수준" };
  return { key: "high", c: C.clay, t: "긴 편", label: "충분히 기다려야 함" };
}

function makeResultId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function ResultWeb({ alarmOn, setAlarmOn }) {
  const [table, setTable] = useState(null);
  const [products, setProducts] = useState({});
  const [error, setError] = useState(null);
  const [compound, setCompound] = useState(null);
  const [taskType, setTaskType] = useState("수확");
  const [hours, setHours] = useState(1);
  const [ppe, setPpe] = useState("없음");
  const [sprayAt, setSprayAt] = useState(() => toDatetimeLocalValue(new Date()));
  const [result, setResult] = useState(null);
  const [chatId, setChatId] = useState("");
  const [alarmStatus, setAlarmStatus] = useState("idle"); // idle | loading | error
  const [alarmError, setAlarmError] = useState(null);

  useEffect(() => {
    let alive = true;
    fetchReiTable()
      .then(data => {
        if (!alive) return;
        setTable(data);
        const firstCompound = Object.keys(data)[0];
        setCompound(firstCompound);
        const firstHour = Object.keys(data[firstCompound]["수확"])[0];
        setHours(Number(firstHour));
      })
      .catch(e => alive && setError(e.message));
    fetchCompoundProducts()
      .then(data => { if (alive) setProducts(data); })
      .catch(() => {});
    return () => { alive = false; };
  }, []);

  const ready = !!(table && compound);
  const hourOptions = ready ? Object.keys(table[compound][taskType]).map(Number).sort((a, b) => a - b) : [];
  const safeHours = ready && hourOptions.includes(hours) ? hours : hourOptions[0];
  const R = 100, circ = 2 * Math.PI * R;

  const changeTask = (t) => {
    setTaskType(t);
    const opts = Object.keys(table[compound][t]).map(Number).sort((a, b) => a - b);
    if (!opts.includes(safeHours)) setHours(opts[0]);
  };

  const handleCheckResult = () => {
    setResult({ id: makeResultId(), compound, taskType, safeHours, ppe, sprayAt });
    setChatId("");
    setAlarmOn(false);
    setAlarmStatus("idle");
    setAlarmError(null);
  };

  if (error) {
    return (
      <div className="scr" style={{ padding: "100px 0", textAlign: "center" }}>
        <div style={{ fontSize: 16, fontWeight: 700, color: C.clay }}>계산표를 불러오지 못했어요.</div>
        <div style={{ fontSize: 13.5, color: C.sub, marginTop: 8 }}>{error}</div>
      </div>
    );
  }

  if (!ready) {
    return (
      <div className="scr" style={{ padding: "140px 0", textAlign: "center" }}>
        <div style={{
          width: 40, height: 40, margin: "0 auto 16px", borderRadius: "50%",
          border: `4px solid ${C.line}`, borderTopColor: C.green500,
          animation: "spin .8s linear infinite",
        }} />
        <div style={{ fontSize: 14.5, color: C.sub, fontWeight: 600 }}>계산표를 불러오는 중이에요…</div>
      </div>
    );
  }

  const maxHour = hourOptions[hourOptions.length - 1];

  const resultData = result ? (() => {
    const rHours = table[result.compound][result.taskType][String(result.safeHours)][result.ppe];
    const rSprayAtDate = new Date(result.sprayAt);
    const rSafeAt = new Date(rSprayAtDate.getTime() + rHours * 3600 * 1000);
    const rLv = levelOf(rHours);
    const rOff = circ * (1 - Math.min(rHours / RING_MAX_HOURS, 1));
    const rAiText = rHours <= 0
      ? `${result.compound} 성분은 이번 ${result.taskType} 작업(${result.safeHours}시간, 보호장비: ${result.ppe}) 기준으로 노출량이 안전 허용 기준(AOEL) 이내예요. 지금 바로 재출입해도 괜찮아요. 다만 처음 들어가실 땐 짧게라도 보호장비를 착용하시길 권해요.`
      : `${result.compound} 성분은 이번 ${result.taskType} 작업(${result.safeHours}시간, 보호장비: ${result.ppe}) 기준 재출입 제한시간이 약 ${rHours.toFixed(1)}시간으로 계산됐어요. `
        + `${rLv.key === "high" ? "접촉이 많고 노출 시간이 길어 잔류 농약 위험이 상대적으로 높으니, 계산된 시각 이후에 들어가시는 걸 권해요. " : rLv.key === "mid" ? "일반적인 수준의 대기시간이에요. 되도록 계산된 시각 이후에 작업을 시작하세요. " : "대기시간이 짧은 편이지만, 안전을 위해 계산된 시각은 지켜 주세요. "}`
        + `${result.ppe !== "작업복+장갑" ? "보호장비를 더 강화하면(작업복+장갑 착용) 대기시간을 줄일 수 있어요." : "이미 가장 강한 보호장비를 착용한 조건이에요."}`;
    return { reiHours: rHours, sprayAtDate: rSprayAtDate, safeAt: rSafeAt, lv: rLv, off: rOff, aiText: rAiText };
  })() : null;

  const handleSetAlarm = async () => {
    if (!chatId.trim() || !result || !resultData) return;
    setAlarmStatus("loading");
    setAlarmError(null);
    try {
      const targetDate = resultData.reiHours <= 0 ? resultData.sprayAtDate : resultData.safeAt;
      await sendAlarm({ chatId: chatId.trim(), targetTime: targetDate.toISOString(), compound: result.compound, crop: "딸기밭" });
      setAlarmStatus("idle");
      setAlarmOn(true);
    } catch (e) {
      setAlarmStatus("error");
      setAlarmError(e.message);
    }
  };

  return (
    <div className="scr" style={{ padding: "44px 0 80px" }}>
      <style>{`
        .rei-hour-slider { -webkit-appearance: none; appearance: none; width: 100%; height: 6px; border-radius: 999px; background: ${C.line}; outline: none; margin: 6px 0; }
        .rei-hour-slider::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; border-radius: 50%; background: ${C.green500}; border: 3px solid #fff; box-shadow: 0 2px 6px rgba(27,67,50,.28); cursor: pointer; }
        .rei-hour-slider::-moz-range-thumb { width: 20px; height: 20px; border-radius: 50%; background: ${C.green500}; border: 3px solid #fff; box-shadow: 0 2px 6px rgba(27,67,50,.28); cursor: pointer; }
        .rei-hour-slider::-moz-range-track { height: 6px; border-radius: 999px; background: ${C.line}; }
      `}</style>
      <div style={{ marginBottom: 8, fontSize: 14, fontWeight: 700, color: C.green700 }}>재출입 계산</div>
      <h1 style={{ fontSize: 34, fontWeight: 800, letterSpacing: "-0.03em", marginBottom: 32 }}>조건을 선택하면 바로 계산돼요</h1>

      {/* 계산 조건 컨트롤 */}
      <div style={{ background: "#fff", border: `1px solid ${C.line}`, borderRadius: 20, padding: "24px", marginBottom: 22 }}>
        <div style={{ fontSize: 16, fontWeight: 800, marginBottom: 18 }}>계산 조건</div>
        <div style={{ marginBottom: 20 }}>
          <div style={{ fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 8 }}>살포 일시</div>
          <input type="datetime-local" value={sprayAt} onChange={e => setSprayAt(e.target.value)}
            style={{ width: "100%", maxWidth: 280, padding: "12px 14px", borderRadius: 12, border: `1.5px solid ${C.line}`, fontSize: 14, fontWeight: 700, background: "#fff", color: C.ink }} />
        </div>

        <div className="rei-controls-grid">
          <div>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 8 }}>농약 (성분)</div>
            <select value={compound} onChange={e => setCompound(e.target.value)}
              style={{ width: "100%", padding: "12px 14px", borderRadius: 12, border: `1.5px solid ${C.line}`, fontSize: 14.5, fontWeight: 700, background: "#fff", color: C.ink }}>
              {Object.keys(table).map(c => (
                <option key={c} value={c}>{products[c] ? `${products[c]} (${c})` : c}</option>
              ))}
            </select>
          </div>

          <div>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 8 }}>작업 유형</div>
            <div style={{ display: "flex", gap: 8 }}>
              {TASK_OPTIONS.map(t => {
                const on = taskType === t.key;
                return (
                  <button key={t.key} className="tap" onClick={() => changeTask(t.key)}
                    style={{ flex: 1, padding: "11px 0", borderRadius: 12, fontWeight: 800, fontSize: 14, background: on ? C.green700 : "#fff", color: on ? "#fff" : C.ink, border: `1.5px solid ${on ? C.green700 : C.line}` }}>
                    {t.key}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 8, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span>작업 시간</span>
              <span style={{ color: C.green700, fontWeight: 800, fontSize: 13 }}>{safeHours}시간</span>
            </div>
            <input type="range" className="rei-hour-slider" min={1} max={maxHour} step={1}
              value={safeHours} onChange={e => setHours(Number(e.target.value))} />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: C.sub, marginTop: 2 }}>
              <span>1시간</span>
              <span>{maxHour}시간</span>
            </div>
          </div>

          <div>
            <div style={{ fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 8 }}>보호장비</div>
            <div style={{ display: "flex", gap: 6 }}>
              {PPE_OPTIONS.map(p => {
                const on = ppe === p;
                return (
                  <button key={p} className="tap" onClick={() => setPpe(p)}
                    style={{ flex: 1, padding: "9px 4px", borderRadius: 10, fontWeight: 700, fontSize: 12, background: on ? C.green900 : "#fff", color: on ? "#fff" : C.ink, border: `1.5px solid ${on ? C.green900 : C.line}` }}>
                    {p}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        <button className="tap" onClick={handleCheckResult} style={{
          width: "100%", marginTop: 22, padding: "15px 0", borderRadius: 14, fontWeight: 800, fontSize: 15.5,
          background: C.green700, color: "#fff",
        }}>
          계산 결과 확인
        </button>
      </div>

      {!result || !resultData ? (
        <div style={{ textAlign: "center", padding: "70px 0", color: C.sub, fontSize: 14.5, fontWeight: 600 }}>
          조건을 선택한 뒤 "계산 결과 확인"을 눌러주세요.
        </div>
      ) : (
        <div className="rei-main-grid">
          {/* 좌측: 게이지 카드 */}
          <div style={{ background: `linear-gradient(165deg, ${C.green900}, ${C.green700})`, borderRadius: 24, padding: "150px 30px", color: C.paper, textAlign: "center" }}>
            <div style={{ fontSize: 13.5, color: "rgba(247,244,236,.75)", fontWeight: 600, marginBottom: 22 }}>{result.compound} · {result.taskType} · {result.safeHours}시간 · {result.ppe}</div>
            <div style={{ position: "relative", width: 240, height: 240, margin: "0 auto" }}>
              <svg width="240" height="240" viewBox="0 0 240 240" style={{ transform: "rotate(-90deg)" }}>
                <circle cx="120" cy="120" r={R} fill="none" stroke="rgba(255,255,255,.14)" strokeWidth="15" />
                <circle cx="120" cy="120" r={R} fill="none" stroke={resultData.lv.c} strokeWidth="15" strokeLinecap="round"
                  strokeDasharray={circ} strokeDashoffset={resultData.off} style={{ "--circ": circ, "--off": resultData.off, animation: "fillRing 1.1s cubic-bezier(.4,0,.2,1) both" }} />
              </svg>
              <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                {resultData.reiHours <= 0 ? (
                  <>
                    <Check size={40} color={resultData.lv.c} strokeWidth={3} />
                    <div style={{ fontSize: 19, fontWeight: 800, marginTop: 10 }}>즉시 재출입 가능</div>
                  </>
                ) : (
                  <>
                    <div style={{ fontSize: 13.5, color: "rgba(247,244,236,.7)", fontWeight: 600 }}>재출입 제한시간</div>
                    <div style={{ fontSize: 54, fontWeight: 800, lineHeight: 1.05, letterSpacing: "-0.03em" }}>{resultData.reiHours.toFixed(1)}</div>
                    <div style={{ fontSize: 16, color: "rgba(247,244,236,.85)", fontWeight: 700, marginTop: -2 }}>시간</div>
                  </>
                )}
                <div style={{ marginTop: 10, fontSize: 12.5, fontWeight: 700, color: resultData.lv.c, background: "rgba(255,255,255,.12)", padding: "5px 14px", borderRadius: 20 }}>{resultData.lv.t} · {resultData.lv.label}</div>
              </div>
            </div>
            <div style={{ marginTop: 26, background: "rgba(255,255,255,.10)", borderRadius: 16, padding: "18px", display: "flex", alignItems: "center", gap: 14, textAlign: "left" }}>
              <div style={{ width: 46, height: 46, borderRadius: 12, background: resultData.lv.c, display: "grid", placeItems: "center", flexShrink: 0 }}>
                <Check size={26} color="#fff" strokeWidth={3} />
              </div>
              <div>
                <div style={{ fontSize: 12.5, color: "rgba(247,244,236,.72)", fontWeight: 600 }}>{resultData.reiHours <= 0 ? "지금 바로 안전하게 들어갈 수 있어요" : "이때부터 안전하게 들어갈 수 있어요"}</div>
                <div style={{ fontSize: 21, fontWeight: 800, marginTop: 2 }}>{fmtDateTime(resultData.reiHours <= 0 ? resultData.sprayAtDate : resultData.safeAt)}</div>
              </div>
            </div>
          </div>

          {/* 우측: AI 해석 + 파라미터 + 알림 */}
          <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
            <div style={{ background: "#fff", border: `1px solid ${C.line}`, borderRadius: 20, padding: "24px" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 9, marginBottom: 14 }}>
                <div style={{ width: 30, height: 30, borderRadius: 9, background: C.green500 + "1A", display: "grid", placeItems: "center" }}>
                  <Sprout size={18} color={C.green700} />
                </div>
                <span style={{ fontSize: 16, fontWeight: 800 }}>안전 해석</span>
                <span style={{ fontSize: 11.5, color: C.sub, fontWeight: 600, background: C.paper2, padding: "3px 9px", borderRadius: 10 }}>데모</span>
              </div>
              <p style={{ fontSize: 15, lineHeight: 1.8, color: C.ink, minHeight: 84 }}>
                {resultData.aiText}
              </p>
            </div>

            <div style={{ background: C.paper2, border: `1px solid ${C.line}`, borderRadius: 20, padding: "24px" }}>
              <div style={{ fontSize: 13.5, fontWeight: 800, color: C.sub, marginBottom: 14 }}>계산에 사용된 값</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0 32px" }}>
                <ParamRow label="살포 일시" value={fmtDateTime(resultData.sprayAtDate)} />
                <ParamRow label="유효성분" value={result.compound} />
                <ParamRow label="작업 유형" value={result.taskType} />
                <ParamRow label="작업 시간" value={`${result.safeHours}시간`} />
                <ParamRow label="보호장비" value={result.ppe} />
              </div>
              <div style={{ marginTop: 10, fontSize: 12, color: C.sub }}>* 작업자 안전기준(AOEL)과 식물체 잔류 감소 곡선을 반영해 계산했어요.</div>
            </div>

            <div style={{
              background: alarmOn ? C.green500 + "14" : "#fff", border: `1.5px solid ${alarmOn ? C.green500 : C.line}`,
              borderRadius: 20, padding: "22px 24px",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ width: 50, height: 50, borderRadius: 13, background: alarmOn ? C.green500 : C.amber + "1A", display: "grid", placeItems: "center", flexShrink: 0 }}>
                  <Bell size={26} color={alarmOn ? "#fff" : C.amber} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 800, fontSize: 16.5 }}>{alarmOn ? "재출입 알림이 설정됐어요" : "재출입 알림 설정하기"}</div>
                  <div style={{ fontSize: 13.5, color: C.sub, marginTop: 3 }}>
                    {fmtDateTime(resultData.reiHours <= 0 ? resultData.sprayAtDate : resultData.safeAt)}에 {alarmOn ? "텔레그램으로 알림을 보내드릴게요" : "알림을 보내드릴게요"}
                  </div>
                </div>
                {alarmOn && <Check size={24} color={C.green700} strokeWidth={3} />}
              </div>

              {!alarmOn && (
                <div style={{ marginTop: 18 }}>
                  <div style={{ fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 6 }}>텔레그램 Chat ID</div>
                  <div style={{ fontSize: 12, color: C.sub, marginBottom: 8, lineHeight: 1.5 }}>
                    텔레그램에서 만든 봇을 검색해 /start를 보내면 Chat ID를 알려드려요. 받은 숫자를 아래에 입력하세요.
                  </div>
                  <input value={chatId} onChange={e => setChatId(e.target.value)} placeholder="예: 123456789"
                    style={{ width: "100%", padding: "12px 14px", borderRadius: 12, border: `1.5px solid ${C.line}`, fontSize: 14, fontWeight: 600, background: "#fff", color: C.ink, marginBottom: 10 }} />
                  {alarmStatus === "error" && (
                    <div style={{ fontSize: 12.5, color: C.clay, marginBottom: 8 }}>{alarmError}</div>
                  )}
                  <button className="tap" onClick={handleSetAlarm} disabled={!chatId.trim() || alarmStatus === "loading"}
                    style={{
                      width: "100%", padding: "13px 0", borderRadius: 12, fontWeight: 800, fontSize: 14.5,
                      background: C.green700, color: "#fff",
                      opacity: (!chatId.trim() || alarmStatus === "loading") ? 0.5 : 1,
                    }}>
                    {alarmStatus === "loading" ? "설정 중…" : "알림 설정하기"}
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
