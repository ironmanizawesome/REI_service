import { Sprout, ArrowRight } from "lucide-react";
import { C } from "../theme";

export function NavBar({ nav, setNav, goCalc }) {
  const links = [
    { key: "home", label: "홈" },
    { key: "calc", label: "재출입 계산" },
    { key: "chat", label: "안전 도우미" },
  ];
  return (
    <div style={{
      position: "sticky", top: 0, zIndex: 50, background: "rgba(247,244,236,.88)",
      backdropFilter: "blur(14px)", borderBottom: `1px solid ${C.line}`,
    }}>
      <div className="container" style={{ height: 68, display: "flex", alignItems: "center", gap: 40, flexWrap: "nowrap" }}>
        <button className="tap" onClick={() => setNav("home")} style={{ display: "flex", alignItems: "center", gap: 10, flexShrink: 0 }}>
          <div style={{ width: 34, height: 34, borderRadius: 10, background: C.green900, display: "grid", placeItems: "center", flexShrink: 0 }}>
            <Sprout size={20} color={C.amber} />
          </div>
          <span className="nav-brand-label" style={{ fontWeight: 800, fontSize: 18, letterSpacing: "-0.02em" }}>안심 재출입</span>
        </button>

        <div className="nav-links">
          {links.map(l => (
            <button key={l.key} className="navlink tap" onClick={() => l.key === "calc" ? goCalc() : setNav(l.key)}
              style={{
                fontSize: 15, fontWeight: nav === l.key ? 800 : 600,
                color: nav === l.key ? C.ink : C.sub, position: "relative", padding: "4px 0", whiteSpace: "nowrap",
              }}>
              {l.label}
              {nav === l.key && <div style={{ position: "absolute", bottom: -22, left: 0, right: 0, height: 3, background: C.green500, borderRadius: 3 }} />}
            </button>
          ))}
        </div>

        <button className="tap" onClick={goCalc} style={{
          marginLeft: "auto", background: C.green700, color: "#fff", fontWeight: 700, fontSize: 14.5,
          padding: "10px 20px", borderRadius: 12, display: "flex", alignItems: "center", gap: 7, flexShrink: 0,
        }}>
          <span className="nav-cta-label">계산 시작</span> <ArrowRight size={17} />
        </button>
      </div>
    </div>
  );
}
