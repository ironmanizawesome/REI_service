import { Sprout } from "lucide-react";
import { C } from "../theme";

export function Footer() {
  return (
    <div style={{ borderTop: `1px solid ${C.line}`, marginTop: 40 }}>
      <div className="container" style={{ paddingTop: 28, paddingBottom: 28, display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <div style={{ width: 28, height: 28, borderRadius: 8, background: C.green900, display: "grid", placeItems: "center" }}>
          <Sprout size={16} color={C.amber} />
        </div>
        <span style={{ fontWeight: 800, fontSize: 15 }}>안심 재출입</span>
        <span style={{ fontSize: 13, color: C.sub }}>한국형 REI 계산 서비스</span>
      </div>
    </div>
  );
}
