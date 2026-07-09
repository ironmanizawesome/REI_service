import { C } from "../../theme";

export function ParamRow({ label, value }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: `1px solid ${C.line}` }}>
      <span style={{ fontSize: 13.5, color: C.sub }}>{label}</span>
      <span style={{ fontSize: 13.5, fontWeight: 700 }}>{value}</span>
    </div>
  );
}
