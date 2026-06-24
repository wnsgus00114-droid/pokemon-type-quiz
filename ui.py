"""Visual components for the Kwangwoon type-matchup gym."""

from __future__ import annotations

import html

import streamlit as st


TYPE_COLORS = {
    "노말": "#a8a77a", "불꽃": "#ee8130", "물": "#6390f0", "전기": "#f7d02c",
    "풀": "#7ac74c", "얼음": "#96d9d6", "격투": "#c22e28", "독": "#a33ea1",
    "땅": "#e2bf65", "비행": "#a98ff3", "에스퍼": "#f95587", "벌레": "#a6b91a",
    "바위": "#b6a136", "고스트": "#735797", "드래곤": "#6f35fc", "악": "#705746",
    "강철": "#b7b7ce", "페어리": "#d685ad",
}


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --navy:#101d42; --navy2:#071126; --red:#e63946; --gold:#ffd166; --cream:#fff8df; }
        .stApp {
            background:
              radial-gradient(circle at 15% 10%, rgba(53,109,196,.22), transparent 32%),
              radial-gradient(circle at 88% 85%, rgba(230,57,70,.16), transparent 35%),
              linear-gradient(160deg, #071126 0%, #10234d 55%, #08132c 100%);
            color: var(--cream);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
        [data-testid="stAudio"] { height: 0; overflow: hidden; opacity: 0; position: absolute; }
        .block-container { max-width: 1080px; padding-top: 2rem; padding-bottom: 3rem; }
        h1,h2,h3,p,label,[data-testid="stMarkdownContainer"] { color: var(--cream); }
        h1,h2,h3 { letter-spacing: -.025em; }
        .student-ribbon { display:flex; align-items:center; justify-content:center; gap:.7rem; margin:.2rem 0 1.4rem; }
        .student-ribbon span { background:#fff; color:#17213d; border:3px solid #17213d; border-radius:999px; padding:.45rem 1rem; font-weight:800; box-shadow:0 4px 0 #ffd166; }
        .hero { text-align:center; padding:2rem 1rem 1.2rem; }
        .hero-kicker { display:inline-block; color:#ffd166; font-weight:900; font-size:.82rem; letter-spacing:.18em; }
        .hero h1 { font-size:clamp(2.2rem,6vw,4.5rem); margin:.25rem 0 .4rem; text-shadow:0 4px 0 #9f1725, 0 8px 22px rgba(0,0,0,.5); }
        .hero p { max-width:650px; margin:auto; color:#cfdbf5; font-size:1.05rem; }
        .game-card { background:linear-gradient(145deg,rgba(255,255,255,.12),rgba(255,255,255,.055)); border:1px solid rgba(255,255,255,.22); border-radius:24px; padding:1.3rem 1.5rem; box-shadow:0 18px 45px rgba(0,0,0,.26); backdrop-filter:blur(10px); }
        .dialogue { background:#fffdf1; color:#152043; border:5px solid #1b2b55; border-radius:18px 18px 18px 4px; padding:1.2rem 1.35rem; font-size:1.14rem; font-weight:800; line-height:1.8; box-shadow:inset 0 0 0 3px #91b7ef, 0 8px 0 rgba(0,0,0,.2); }
        .dialogue * { color:#152043; }
        .mini-label { color:#ffd166; text-transform:uppercase; letter-spacing:.12em; font-size:.75rem; font-weight:900; }
        .stat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:.7rem; margin:1rem 0; }
        .stat { background:rgba(0,0,0,.2); border:1px solid rgba(255,255,255,.15); border-radius:16px; padding:.9rem; text-align:center; }
        .stat b { display:block; font-size:1.7rem; color:#ffd166; }
        .stat small { color:#b9c8e8; }
        .battle-stage { position:relative; min-height:350px; border-radius:28px; overflow:hidden; border:4px solid rgba(255,255,255,.85); background:linear-gradient(#79c7f2 0 50%,#8fd082 50% 73%,#417f52 73%); box-shadow:0 20px 50px rgba(0,0,0,.35); margin:.7rem 0 1.2rem; }
        .battle-stage:before { content:""; position:absolute; inset:45% -10% auto; height:80px; background:radial-gradient(ellipse,#d9efb3 0 45%,transparent 47%); opacity:.8; }
        .monster-img { position:absolute; width:min(45%,400px); right:2%; bottom:4%; filter:drop-shadow(0 16px 7px rgba(0,0,0,.28)); animation:bob 2.4s ease-in-out infinite; }
        .partner-img { position:absolute; z-index:2; width:min(31%,275px); left:5%; bottom:2%; filter:drop-shadow(0 14px 6px rgba(0,0,0,.26)); animation:bob 2.1s ease-in-out infinite reverse; }
        .monster-img.took-hit,.partner-img.took-hit { animation:damageFlash .55s ease-in-out 2; }
        .trainer-orb { position:absolute; left:7%; bottom:10%; width:125px; height:125px; border-radius:50%; background:linear-gradient(#e63946 0 46%,#17213d 47% 55%,#f7fbff 56%); box-shadow:0 12px 0 rgba(0,0,0,.16), inset 0 0 0 7px #fff; }
        .trainer-orb:after { content:""; position:absolute; width:36px; height:36px; background:#fff; border:8px solid #17213d; border-radius:50%; left:36px; top:36px; }
        .trainer-name { position:absolute; z-index:4; left:5%; bottom:3%; background:#122044; color:white; border:3px solid white; border-radius:999px; padding:.35rem .9rem; font-weight:900; }
        .hp-panel { position:absolute; z-index:3; top:6%; width:44%; background:#fffdf1; color:#132043; border:4px solid #17213d; border-radius:12px 20px 12px 12px; padding:.65rem .85rem; box-shadow:5px 6px 0 rgba(0,0,0,.2); }
        .hp-panel.enemy { left:4%; } .hp-panel.player { right:4%; top:70%; }
        .hp-title { display:flex; justify-content:space-between; color:#132043; font-weight:900; }
        .hp-track { height:13px; background:#ced5c4; border:2px solid #27324c; border-radius:999px; overflow:hidden; margin-top:.35rem; }
        .hp-fill { height:100%; transition:width .5s ease; }
        .hp-value { color:#394565; font-size:.72rem; text-align:right; font-weight:800; }
        .question-head { display:flex; gap:.7rem; align-items:center; flex-wrap:wrap; margin-bottom:.55rem; }
        .question-no { color:#ffd166; font-weight:900; letter-spacing:.08em; }
        .difficulty { border:1px solid #ffcf5b; border-radius:999px; padding:.18rem .55rem; color:#ffdd8a; font-size:.72rem; font-weight:900; }
        .type-chip { display:inline-block; border-radius:999px; padding:.22rem .6rem; color:white; font-size:.76rem; font-weight:900; text-shadow:0 1px 2px #0008; }
        .feedback-ok,.feedback-no { border-radius:16px; padding:1rem 1.1rem; margin:.8rem 0; font-weight:800; }
        .feedback-ok { background:#dff7e3; color:#14532d; border:3px solid #36a852; }
        .feedback-no { background:#ffe4e6; color:#8c1724; border:3px solid #ef5b68; }
        .badge-glow { filter:drop-shadow(0 0 15px #ffd166) drop-shadow(0 0 35px #ff8c42); animation:badge 1.8s ease-in-out infinite; }
        .locked-badge { filter:grayscale(1); opacity:.25; }
        .badge-glow img,.locked-badge img { display:block; width:100%; height:auto; }
        .badge-label { margin:.65rem -.5rem 0; text-align:center; font-size:clamp(.72rem,1.15vw,.95rem); font-weight:900; white-space:nowrap; }
        .partner-card { text-align:center; padding:.7rem; border-radius:20px; background:linear-gradient(145deg,rgba(36,105,205,.35),rgba(255,209,102,.14)); border:1px solid rgba(255,255,255,.2); }
        .partner-card img { width:100%; display:block; filter:drop-shadow(0 8px 8px #0005); }
        .partner-card b,.partner-card small { display:block; } .partner-card b { color:#ffd166; font-size:1.15rem; } .partner-card small { color:#d7e4ff; }
        .partner-reveal,.partner-mystery { border-radius:28px; padding:1rem; background:radial-gradient(circle,#326bcc55,transparent 65%); }
        .partner-reveal img,.partner-mystery img { display:block; width:100%; height:auto; }
        .partner-reveal img { filter:drop-shadow(0 0 22px #75d8ff); animation:partnerEnter 1s ease-out both; }
        .partner-mystery img { filter:brightness(0) drop-shadow(0 0 18px #72bcff); opacity:.72; }
        .perfect { text-align:center; font-size:clamp(2rem,5vw,3.6rem); color:#ffd166; text-shadow:0 3px 0 #a21826; }
        div[data-testid="stForm"], div[data-testid="stVerticalBlockBorderWrapper"] { border-radius:20px; }
        div[role="radiogroup"] label { background:rgba(255,255,255,.09); border:1px solid rgba(255,255,255,.15); border-radius:12px; padding:.55rem .75rem; margin:.15rem 0; transition:.2s; }
        div[role="radiogroup"] label:hover { background:rgba(255,209,102,.15); transform:translateX(3px); }
        .stButton > button, .stFormSubmitButton > button { width:100%; min-height:3rem; border:none; border-radius:14px; background:linear-gradient(#ffd95e,#f3ae25); color:#17213d; font-weight:950; box-shadow:0 5px 0 #a96114; transition:.12s; }
        .stButton > button:hover, .stFormSubmitButton > button:hover { color:#17213d; transform:translateY(-2px); box-shadow:0 7px 0 #a96114; }
        .stTextInput input { border:2px solid #9eb4dd; border-radius:12px; background:#f8fbff; color:#14213d; }
        [data-baseweb="tab-list"] { gap:.4rem; } [data-baseweb="tab"] { border-radius:12px; color:#dbe7ff; }
        @keyframes bob { 50% { transform:translateY(-9px); } }
        @keyframes badge { 50% { transform:scale(1.035); } }
        @keyframes damageFlash { 0%,100%{opacity:1;transform:translateX(0)} 25%{opacity:.2;transform:translateX(-12px)} 50%{opacity:1;filter:brightness(2) drop-shadow(0 0 15px white)} 75%{opacity:.25;transform:translateX(12px)} }
        @keyframes partnerEnter { from{opacity:0;transform:scale(.25) rotate(-16deg)} to{opacity:1;transform:scale(1) rotate(0)} }
        @media (max-width:700px) { .block-container{padding:1rem .8rem 2rem}.battle-stage{min-height:290px}.hp-panel{width:58%}.hp-panel.player{top:72%}.monster-img{width:53%;right:-5%}.partner-img{width:37%;left:1%}.trainer-orb{width:90px;height:90px}.trainer-orb:after{width:26px;height:26px;left:25px;top:25px}.stat-grid{grid-template-columns:1fr 1fr 1fr}.game-card{padding:1rem} }
        </style>
        """,
        unsafe_allow_html=True,
    )


def student_ribbon() -> None:
    st.markdown(
        '<div class="student-ribbon"><span>학번 2022508121</span><span>제작자 백준현</span></div>',
        unsafe_allow_html=True,
    )


def type_chips(types: list[str]) -> str:
    return " ".join(
        f'<span class="type-chip" style="background:{TYPE_COLORS.get(t, "#667")}">{html.escape(t)}</span>'
        for t in types
    )


def hp_panel(name: str, hp: int, side: str, level: int = 50) -> str:
    color = "#42bd64" if hp > 50 else "#f0b429" if hp > 20 else "#e63946"
    return f"""
    <div class="hp-panel {side}">
      <div class="hp-title"><span>{html.escape(name)}</span><span>Lv.{level}</span></div>
      <div class="hp-track"><div class="hp-fill" style="width:{hp}%;background:{color}"></div></div>
      <div class="hp-value">HP {hp} / 100</div>
    </div>"""
