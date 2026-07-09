import { Sprout, Bell, MessageCircle, Leaf, ShieldCheck, Info, ArrowRight, Check } from "lucide-react";
import { C } from "../theme";
import { MiniRing } from "./shared/MiniRing";
import { FeatureCardWeb } from "./shared/FeatureCardWeb";
import { StepCard } from "./shared/StepCard";

export function HomeWeb({ goCalc, setNav }) {
  return (
    <div className="scr">
      {/* 히어로 */}
      <div className="home-hero">
        <div>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 7, background: C.paper2, border: `1px solid ${C.line}`, padding: "7px 14px", borderRadius: 20, marginBottom: 24 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: C.green500 }} />
            <span style={{ fontSize: 13, fontWeight: 700, color: C.green700 }}>한국형 REI 계산 서비스</span>
          </div>
          <h1 className="home-h1" style={{ lineHeight: 1.18, fontWeight: 800, letterSpacing: "-0.035em" }}>
            농약 뿌린 뒤,<br />
            <span style={{ color: C.green700 }}>안전한 재출입 시각</span>을<br />
            바로 알려드려요
          </h1>
          <p style={{ fontSize: 17, lineHeight: 1.65, color: C.sub, marginTop: 22, maxWidth: 460 }}>
            작물과 작업, 살포 시각만 입력하면 우리 농장 기준의
            재출입 제한시간(REI)을 계산하고, AI가 쉽게 풀어 설명해 드립니다.
          </p>
          <div style={{ display: "flex", gap: 12, marginTop: 34, flexWrap: "wrap" }}>
            <button className="tap" onClick={goCalc} style={{
              background: C.green700, color: "#fff", fontWeight: 800, fontSize: 16, padding: "15px 28px",
              borderRadius: 14, display: "flex", alignItems: "center", gap: 8, boxShadow: "0 10px 24px rgba(45,106,79,.24)",
            }}>
              재출입 시각 계산하기 <ArrowRight size={19} />
            </button>
            <button className="tap" onClick={() => setNav("chat")} style={{
              background: "#fff", color: C.ink, fontWeight: 700, fontSize: 16, padding: "15px 24px",
              borderRadius: 14, border: `1.5px solid ${C.line}`, display: "flex", alignItems: "center", gap: 8,
            }}>
              <MessageCircle size={18} color={C.green700} /> 안전 도우미
            </button>
          </div>
        </div>

        {/* 히어로 비주얼: 게이지 미리보기 */}
        <div className="home-hero-visual" style={{
          background: `linear-gradient(165deg, ${C.green900}, ${C.green700})`, borderRadius: 28,
          padding: "40px", color: C.paper, position: "relative", overflow: "hidden",
          boxShadow: "0 24px 50px rgba(27,67,50,.22)",
        }}>
          <Leaf size={260} color="#fff" style={{ position: "absolute", right: -60, bottom: -50, opacity: 0.06, transform: "rotate(18deg)" }} />
          <div style={{ fontSize: 13.5, fontWeight: 600, color: "rgba(247,244,236,.72)", marginBottom: 6 }}>예시 · 사파이어 · 딸기 · 수확</div>
          <div style={{ display: "flex", alignItems: "center", gap: 28, marginTop: 20, flexWrap: "wrap" }}>
            <MiniRing hours={12} total={24} color={C.green500} />
            <div>
              <div style={{ fontSize: 13, color: "rgba(247,244,236,.7)", fontWeight: 600 }}>재출입 제한시간</div>
              <div style={{ fontSize: 44, fontWeight: 800, lineHeight: 1.1 }}>12<span style={{ fontSize: 18, marginLeft: 4 }}>시간</span></div>
              <div style={{ fontSize: 13, fontWeight: 700, color: C.green500, marginTop: 4 }}>낮음 · 비교적 짧은 편</div>
            </div>
          </div>
          <div style={{ marginTop: 26, background: "rgba(255,255,255,.10)", borderRadius: 14, padding: "14px 16px", display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{ width: 40, height: 40, borderRadius: 10, background: C.green500, display: "grid", placeItems: "center" }}>
              <Check size={22} color="#fff" strokeWidth={3} />
            </div>
            <div>
              <div style={{ fontSize: 12, color: "rgba(247,244,236,.7)" }}>안전 재출입 시각</div>
              <div style={{ fontSize: 17, fontWeight: 800 }}>7월 3일 21:00</div>
            </div>
          </div>
        </div>
      </div>

      {/* 특징 3단 */}
      <div style={{ paddingBottom: 24 }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: C.sub, marginBottom: 18 }}>이렇게 도와드려요</div>
        <div className="home-grid-3">
          <FeatureCardWeb icon={ShieldCheck} color={C.green500} title="독성 기준으로 계산"
            desc="유효성분의 안전기준(AOEL)과 식물체 잔류량을 바탕으로 재출입 시각을 산출합니다." />
          <FeatureCardWeb icon={Bell} color={C.amber} title="재출입 알림"
            desc="안전한 시각이 되면 잊지 않도록 알림으로 알려드려요." />
          <FeatureCardWeb icon={MessageCircle} color={C.green700} title="AI 안전 도우미"
            desc="농약 사용법·주의사항이 궁금하면 언제든 대화로 물어보세요." />
        </div>
      </div>

      {/* 작동 방식 3단계 */}
      <div style={{ padding: "44px 0 20px" }}>
        <div style={{ fontSize: 14, fontWeight: 700, color: C.sub, marginBottom: 22 }}>3단계로 끝나요</div>
        <div className="home-grid-3">
          <StepCard n="01" title="농약과 작업 입력" desc="상품명을 검색하고 작물·작업 유형과 살포 시각을 고르세요." />
          <StepCard n="02" title="재출입 시각 계산" desc="농장 조건에 맞춘 REI와 안전 재출입 시각을 바로 확인해요." />
          <StepCard n="03" title="알림으로 안심" desc="안전한 시각에 맞춰 알림을 받고 편하게 작업하세요." />
        </div>
      </div>

      {/* REI 설명 배너 */}
      <div style={{
        margin: "36px 0 60px", background: C.paper2, border: `1px solid ${C.line}`, borderRadius: 20,
        padding: "28px 32px", display: "flex", gap: 18, alignItems: "flex-start",
      }}>
        <div style={{ width: 46, height: 46, borderRadius: 12, background: C.green500 + "1A", display: "grid", placeItems: "center", flexShrink: 0 }}>
          <Info size={24} color={C.green700} />
        </div>
        <div>
          <div style={{ fontWeight: 800, fontSize: 17, marginBottom: 6 }}>REI(재출입 제한시간)란?</div>
          <p style={{ fontSize: 14.5, lineHeight: 1.7, color: C.sub, maxWidth: 720 }}>
            농약 살포 후 작업자가 농장에 안전하게 다시 들어갈 수 있을 때까지 기다려야 하는 시간이에요.
            우리나라는 아직 작업자 재출입 관리 제도가 부족한데, 이 서비스는 유효성분의 독성 기준과
            식물체 잔류 감소를 반영해 한국 시설재배 환경에 맞는 재출입 시각을 안내합니다.
          </p>
        </div>
      </div>
    </div>
  );
}
