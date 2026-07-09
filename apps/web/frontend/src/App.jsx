import { useState } from "react";
import { C, font } from "./theme";
import { NavBar } from "./components/NavBar";
import { Footer } from "./components/Footer";
import { HomeWeb } from "./components/HomeWeb";
import { ResultWeb } from "./components/ResultWeb";
import { ChatWeb } from "./components/ChatWeb";

export default function App() {
  const [nav, setNav] = useState("home"); // home | calc | chat
  const [alarmOn, setAlarmOn] = useState(false);

  const goCalc = () => setNav("calc");

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", background: C.paper, color: C.ink, fontFamily: font, WebkitFontSmoothing: "antialiased" }}>
      <style>{`
        @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        button { font-family: inherit; cursor: pointer; border: none; background: none; }
        input, select { font-family: inherit; }
        @keyframes fadeUp { from { opacity: 0; transform: translateY(14px);} to {opacity:1; transform: none;} }
        @keyframes fillRing { from { stroke-dashoffset: var(--circ);} to { stroke-dashoffset: var(--off);} }
        @keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:.5;} }
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (prefers-reduced-motion: reduce){ *{animation:none!important; transition:none!important;} }
        .scr { animation: fadeUp .45s ease both; }
        .tap { transition: transform .12s ease, box-shadow .15s ease, background .15s ease, border-color .15s ease, color .15s ease; }
        .tap:active { transform: scale(.99); }
        .card { transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease; }
        .card:hover { transform: translateY(-3px); box-shadow: 0 14px 30px rgba(27,67,50,.10); }
        .navlink:hover { color: ${C.ink} !important; }
        ::-webkit-scrollbar { width: 10px; height: 10px; }
        ::-webkit-scrollbar-thumb { background: ${C.line}; border-radius: 8px; }

        .container { max-width: 1180px; margin: 0 auto; padding: 0 32px; }
        @media (max-width: 860px) { .container { padding: 0 24px; } }
        @media (max-width: 560px) { .container { padding: 0 16px; } }

        .nav-links { display: flex; gap: 30px; margin-left: 8px; }
        @media (max-width: 720px) { .nav-links { gap: 16px; margin-left: 0; } }
        @media (max-width: 560px) {
          .nav-brand-label { display: none; }
          .nav-cta-label { display: none; }
        }

        .home-hero { display: grid; grid-template-columns: 1.1fr .9fr; gap: 40px; align-items: center; padding: 64px 0 56px; }
        @media (max-width: 900px) {
          .home-hero { grid-template-columns: 1fr; padding: 40px 0 36px; }
          .home-hero-visual { order: -1; }
        }
        .home-h1 { font-size: 52px; }
        @media (max-width: 900px) { .home-h1 { font-size: 40px; } }
        @media (max-width: 560px) { .home-h1 { font-size: 32px; } }

        .home-grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }
        @media (max-width: 860px) { .home-grid-3 { grid-template-columns: repeat(2, 1fr); } }
        @media (max-width: 560px) { .home-grid-3 { grid-template-columns: 1fr; } }

        .rei-controls-grid { display: grid; grid-template-columns: 1.3fr 1fr 1.4fr 1.4fr; gap: 20px; }
        @media (max-width: 900px) { .rei-controls-grid { grid-template-columns: 1fr 1fr; } }
        @media (max-width: 520px) { .rei-controls-grid { grid-template-columns: 1fr; } }

        .rei-main-grid { display: grid; grid-template-columns: 420px 1fr; gap: 28px; align-items: start; }
        @media (max-width: 900px) { .rei-main-grid { grid-template-columns: 1fr; } }
      `}</style>

      <NavBar nav={nav} setNav={setNav} goCalc={goCalc} />

      <div className="container" style={{ flex: 1 }}>
        {nav === "home" && <HomeWeb goCalc={goCalc} setNav={setNav} />}
        {nav === "calc" && <ResultWeb alarmOn={alarmOn} setAlarmOn={setAlarmOn} />}
        {nav === "chat" && <ChatWeb />}
      </div>

      <Footer />
    </div>
  );
}
