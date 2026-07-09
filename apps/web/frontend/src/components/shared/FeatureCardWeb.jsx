import { C } from "../../theme";

export function FeatureCardWeb({ icon: Icon, color, title, desc }) {
  return (
    <div className="card" style={{ background: "#fff", border: `1px solid ${C.line}`, borderRadius: 18, padding: "24px" }}>
      <div style={{ width: 48, height: 48, borderRadius: 13, background: color + "1A", display: "grid", placeItems: "center", marginBottom: 16 }}>
        <Icon size={24} color={color} />
      </div>
      <div style={{ fontWeight: 800, fontSize: 17, marginBottom: 7 }}>{title}</div>
      <div style={{ fontSize: 14, color: C.sub, lineHeight: 1.6 }}>{desc}</div>
    </div>
  );
}
