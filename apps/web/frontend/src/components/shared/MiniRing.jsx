import { Sprout } from "lucide-react";

export function MiniRing({ hours, total, color }) {
  const R = 52, circ = 2 * Math.PI * R, off = circ * (1 - Math.min(hours / total, 1));
  return (
    <div style={{ position: "relative", width: 130, height: 130, flexShrink: 0 }}>
      <svg width="130" height="130" viewBox="0 0 130 130" style={{ transform: "rotate(-90deg)" }}>
        <circle cx="65" cy="65" r={R} fill="none" stroke="rgba(255,255,255,.15)" strokeWidth="11" />
        <circle cx="65" cy="65" r={R} fill="none" stroke={color} strokeWidth="11" strokeLinecap="round"
          strokeDasharray={circ} strokeDashoffset={off}
          style={{ "--circ": circ, "--off": off, animation: "fillRing 1.1s cubic-bezier(.4,0,.2,1) both" }} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "grid", placeItems: "center" }}>
        <Sprout size={34} color={color} />
      </div>
    </div>
  );
}
