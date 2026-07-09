import { C } from "../../theme";

export function StepCard({ n, title, desc }) {
  return (
    <div style={{ background: "#fff", border: `1px solid ${C.line}`, borderRadius: 18, padding: "24px" }}>
      <div style={{ fontSize: 15, fontWeight: 800, color: C.green500, letterSpacing: "0.05em", marginBottom: 12 }}>{n}</div>
      <div style={{ fontWeight: 800, fontSize: 17, marginBottom: 7 }}>{title}</div>
      <div style={{ fontSize: 14, color: C.sub, lineHeight: 1.6 }}>{desc}</div>
    </div>
  );
}
