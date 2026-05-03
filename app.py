"""
ResearchMind AI — Streamlit frontend
Zero external dependencies beyond streamlit itself.
All pipeline/UI bugs fixed.
"""

import re
import html as _html_mod
import streamlit as st

st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── THEME DEFINITIONS ──────────────────────────────────────────────────────────
THEMES = {
    "Cosmic Violet": {
        "a": "#7c5cbf", "a_l": "#a07de8", "a_d": "#5a3fa0",
        "b": "#3d8ef0", "b_l": "#6ab4ff",
        "c": "#22d3ee", "c_d": "#0891b2",
        "acc": "#e879f9",
        "g1": "rgba(124,92,191,0.25)", "g2": "rgba(61,142,240,0.2)",
        "g3": "rgba(20,184,166,0.18)", "g4": "rgba(232,121,249,0.15)",
        "m1": "rgba(124,92,191,0.18)", "m2": "rgba(61,142,240,0.14)",
        "m3": "rgba(20,184,166,0.12)", "m4": "rgba(232,121,249,0.1)",
        "tg": "#a07de8 0%, #6ab4ff 40%, #22d3ee 65%, #e879f9 100%",
        "swatch": "#7c5cbf",
    },
    "Golden Hour": {
        "a": "#d4821a", "a_l": "#f5a63c", "a_d": "#a05c0a",
        "b": "#e8c040", "b_l": "#ffd966",
        "c": "#f07040", "c_d": "#c04820",
        "acc": "#ff6b6b",
        "g1": "rgba(212,130,26,0.28)", "g2": "rgba(232,192,64,0.2)",
        "g3": "rgba(240,112,64,0.18)", "g4": "rgba(255,107,107,0.15)",
        "m1": "rgba(212,130,26,0.2)",  "m2": "rgba(232,192,64,0.14)",
        "m3": "rgba(240,112,64,0.12)", "m4": "rgba(255,107,107,0.1)",
        "tg": "#f5a63c 0%, #ffd966 40%, #f07040 70%, #ff6b6b 100%",
        "swatch": "#d4821a",
    },
    "Arctic Teal": {
        "a": "#0e9e8e", "a_l": "#14c4b0", "a_d": "#087060",
        "b": "#0ea5c9", "b_l": "#38bdf8",
        "c": "#60efbc", "c_d": "#10b981",
        "acc": "#a78bfa",
        "g1": "rgba(14,158,142,0.25)", "g2": "rgba(14,165,201,0.2)",
        "g3": "rgba(96,239,188,0.18)", "g4": "rgba(167,139,250,0.15)",
        "m1": "rgba(14,158,142,0.18)", "m2": "rgba(14,165,201,0.14)",
        "m3": "rgba(96,239,188,0.12)", "m4": "rgba(167,139,250,0.1)",
        "tg": "#14c4b0 0%, #38bdf8 40%, #60efbc 65%, #a78bfa 100%",
        "swatch": "#0e9e8e",
    },
    "Rose Neon": {
        "a": "#e0306a", "a_l": "#ff6699", "a_d": "#a01848",
        "b": "#c050e8", "b_l": "#e080ff",
        "c": "#ff8c42", "c_d": "#d05010",
        "acc": "#ffd166",
        "g1": "rgba(224,48,106,0.25)", "g2": "rgba(192,80,232,0.2)",
        "g3": "rgba(255,140,66,0.18)", "g4": "rgba(255,209,102,0.15)",
        "m1": "rgba(224,48,106,0.18)", "m2": "rgba(192,80,232,0.14)",
        "m3": "rgba(255,140,66,0.12)", "m4": "rgba(255,209,102,0.1)",
        "tg": "#ff6699 0%, #e080ff 40%, #ff8c42 65%, #ffd166 100%",
        "swatch": "#e0306a",
    },
    "Midnight Blue": {
        "a": "#2563eb", "a_l": "#5b8df5", "a_d": "#1040b0",
        "b": "#7c3aed", "b_l": "#a78bfa",
        "c": "#06b6d4", "c_d": "#0284c7",
        "acc": "#34d399",
        "g1": "rgba(37,99,235,0.25)",  "g2": "rgba(124,58,237,0.2)",
        "g3": "rgba(6,182,212,0.18)",  "g4": "rgba(52,211,153,0.15)",
        "m1": "rgba(37,99,235,0.18)",  "m2": "rgba(124,58,237,0.14)",
        "m3": "rgba(6,182,212,0.12)",  "m4": "rgba(52,211,153,0.1)",
        "tg": "#5b8df5 0%, #a78bfa 40%, #06b6d4 65%, #34d399 100%",
        "swatch": "#2563eb",
    },
}

# ── SESSION STATE ──────────────────────────────────────────────────────────────
_defaults = {
    "result": None,
    "completed_steps": [],
    "durations": {},
    "topic_done": "",
    "_pipeline_running": False,
    "theme": "Cosmic Violet",
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v

T = THEMES[st.session_state.theme]


# ── PURE-STDLIB MARKDOWN RENDERER ─────────────────────────────────────────────
def _inline(s: str) -> str:
    """Apply inline markdown formatting to an already-HTML-escaped string."""
    # Inline code  `…`  (do first so inner chars aren't re-processed)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    # Bold **…** or __…__
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"__(.+?)__",     r"<strong>\1</strong>", s)
    # Italic *…* or _…_  (single, not double)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)",       r"<em>\1</em>", s)
    # Links [text](url)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank">\1</a>', s)
    return s


def _md_to_html(text: str) -> str:
    """Lightweight stdlib-only markdown → HTML converter."""
    lines     = text.split("\n")
    out: list = []
    in_ul     = False
    in_ol     = False
    in_pre    = False
    in_bq     = False
    bq_buf: list = []

    def flush_list():
        nonlocal in_ul, in_ol
        if in_ul:  out.append("</ul>");  in_ul = False
        if in_ol:  out.append("</ol>");  in_ol = False

    def flush_bq():
        nonlocal in_bq, bq_buf
        if in_bq:
            out.append("<blockquote>" + " ".join(bq_buf) + "</blockquote>")
            bq_buf = []; in_bq = False

    for raw in lines:
        stripped = raw.strip()

        # Fenced code block ```
        if stripped.startswith("```"):
            flush_list(); flush_bq()
            if not in_pre:
                lang = stripped[3:].strip()
                out.append(f'<pre><code class="language-{lang}">' if lang else "<pre><code>")
                in_pre = True
            else:
                out.append("</code></pre>")
                in_pre = False
            continue

        if in_pre:
            out.append(_html_mod.escape(raw))
            continue

        # Blank line
        if not stripped:
            flush_list(); flush_bq()
            continue

        # ATX Headings  # … ######
        m = re.match(r"^(#{1,6})\s+(.*)", stripped)
        if m:
            flush_list(); flush_bq()
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{_inline(_html_mod.escape(m.group(2)))}</h{lvl}>")
            continue

        # Horizontal rule  --- / *** / ___
        if re.match(r"^[-*_]{3,}$", stripped):
            flush_list(); flush_bq()
            out.append("<hr>")
            continue

        # Blockquote  > …
        if stripped.startswith("> "):
            flush_list()
            content = _inline(_html_mod.escape(stripped[2:]))
            if not in_bq:
                in_bq = True; bq_buf = [content]
            else:
                bq_buf.append(content)
            continue
        else:
            flush_bq()

        # Unordered list  - / * / +
        m_ul = re.match(r"^[-*+]\s+(.*)", stripped)
        if m_ul:
            flush_bq()
            if in_ol: out.append("</ol>"); in_ol = False
            if not in_ul: out.append("<ul>"); in_ul = True
            out.append(f"<li>{_inline(_html_mod.escape(m_ul.group(1)))}</li>")
            continue

        # Ordered list  1. …
        m_ol = re.match(r"^\d+\.\s+(.*)", stripped)
        if m_ol:
            flush_bq()
            if in_ul: out.append("</ul>"); in_ul = False
            if not in_ol: out.append("<ol>"); in_ol = True
            out.append(f"<li>{_inline(_html_mod.escape(m_ol.group(1)))}</li>")
            continue

        # Normal paragraph
        flush_list()
        out.append(f"<p>{_inline(_html_mod.escape(stripped))}</p>")

    flush_list(); flush_bq()
    if in_pre:
        out.append("</code></pre>")

    return "\n".join(out)


def render_md(text: str, css_class: str) -> str:
    """Convert markdown to a styled HTML div. Never throws."""
    if not text or not text.strip():
        return (
            f'<div class="{css_class}">'
            '<p style="color:var(--faint);font-style:italic;">No content available.</p>'
            '</div>'
        )
    try:
        body = _md_to_html(text)
    except Exception:
        body = "<p>" + _html_mod.escape(text).replace("\n", "<br>") + "</p>"
    return f'<div class="{css_class}">{body}</div>'


# ── SCORE HELPERS ──────────────────────────────────────────────────────────────
def parse_score(feedback: str):
    """
    Extract numeric score from critic output.
    Matches: Score: 8/10 | **Score**: 7.5/10 | Score: 9 | SCORE: 8.5 / 10
    Returns (display_str, pct, num, denom) or None.
    """
    if not feedback:
        return None
    m = re.search(
        r"(?i)\*{0,2}score\*{0,2}\s*[:\-]?\s*\*{0,2}"
        r"\s*([0-9]+(?:\.[0-9]+)?)"
        r"(?:\s*/\s*([0-9]+(?:\.[0-9]+)?))?",
        feedback,
    )
    if not m:
        return None
    try:
        num   = float(m.group(1))
        denom = float(m.group(2)) if m.group(2) else 10.0
        pct   = min(100.0, (num / denom) * 100)
        disp  = f"{num:g}/{denom:.0f}"
        return disp, pct, num, denom
    except Exception:
        return None


def strip_score_line(feedback: str) -> str:
    """Remove the score line from feedback body text."""
    if not feedback:
        return ""
    cleaned = re.sub(
        r"(?im)^\*{0,2}score\*{0,2}\s*[:\-]?\s*\*{0,2}"
        r"\s*[0-9]+(?:\.[0-9]+)?(?:\s*/\s*[0-9]+(?:\.[0-9]+)?)?\s*$",
        "",
        feedback,
    )
    return cleaned.strip()


def bar_color(val: float) -> str:
    if val >= 8: return "linear-gradient(90deg,var(--gd),var(--green))"
    if val >= 6: return "linear-gradient(90deg,var(--a),var(--b_l))"
    return "linear-gradient(90deg,var(--a_d),var(--a_l))"


# ── CSS ────────────────────────────────────────────────────────────────────────
def inject_css(T: dict) -> None:
    a=T["a"]; a_l=T["a_l"]; a_d=T["a_d"]
    b=T["b"]; b_l=T["b_l"]
    c=T["c"]; c_d=T["c_d"]
    acc=T["acc"]
    g1=T["g1"]; g2=T["g2"]; g3=T["g3"]; g4=T["g4"]
    m1=T["m1"]; m2=T["m2"]; m3=T["m3"]; m4=T["m4"]
    tg=T["tg"]

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Mono:wght@400;700&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0;}}

:root{{
  --a:{a};--a_l:{a_l};--a_d:{a_d};
  --b:{b};--b_l:{b_l};
  --c:{c};--c_d:{c_d};
  --acc:{acc};
  --bg:#07080f;--bg2:#0b0d1a;
  --surf:#0f1224;--surf2:#141828;
  --brd:#1a2038;--brd2:#242e50;
  --green:#34d399;--gd:#059669;
  --red:#f87171;
  --text:#c4d0ec;--dim:#5a6a90;
  --faint:#252f4a;--white:#edf2ff;
}}

html,body{{height:100%;}}

[data-testid="stAppViewContainer"]{{
  background:var(--bg)!important;
  font-family:'Outfit',sans-serif;
  color:var(--text);min-height:100vh;overflow-x:hidden;position:relative;
}}
[data-testid="stAppViewContainer"]::before{{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background:
    radial-gradient(ellipse 55% 55% at 10% 15%,{m1} 0%,transparent 65%),
    radial-gradient(ellipse 50% 50% at 90% 10%,{m2} 0%,transparent 65%),
    radial-gradient(ellipse 45% 60% at 80% 85%,{m3} 0%,transparent 65%),
    radial-gradient(ellipse 40% 40% at 20% 80%,{m4} 0%,transparent 65%);
  animation:mesh-drift 18s ease-in-out infinite alternate;
}}
@keyframes mesh-drift{{
  0%{{filter:hue-rotate(0deg);opacity:1;}}
  50%{{filter:hue-rotate(12deg);opacity:.85;}}
  100%{{filter:hue-rotate(-8deg);opacity:.92;}}
}}
[data-testid="stAppViewContainer"]::after{{
  content:'';position:fixed;inset:0;z-index:0;pointer-events:none;
  background-image:radial-gradient(circle,{m2} 1px,transparent 0);
  background-size:44px 44px;opacity:.28;
}}

/* Hide chrome */
#MainMenu,footer,header,
[data-testid="stDecoration"],
[data-testid="stToolbar"],
[data-testid="collapsedControl"]{{display:none!important;}}
[data-testid="stMain"]{{padding-top:0!important;}}
[data-testid="block-container"]{{
  padding:0 2.5rem 5rem!important;
  max-width:1500px!important;position:relative;z-index:1;
}}
[data-testid="column"]{{position:relative;z-index:1;}}

::-webkit-scrollbar{{width:4px;}}
::-webkit-scrollbar-track{{background:var(--bg2);}}
::-webkit-scrollbar-thumb{{background:linear-gradient(180deg,{a},{c});border-radius:4px;}}

/* ── THEME STRIP ── */
.theme-strip{{
  display:flex;align-items:center;gap:1rem;
  padding:.55rem 1.4rem;background:var(--surf);
  border-bottom:1px solid var(--brd);position:relative;z-index:10;
}}
.theme-strip-label{{
  font-family:'Space Mono',monospace;font-size:.55rem;
  letter-spacing:.24em;text-transform:uppercase;color:var(--dim);white-space:nowrap;
}}
.t-swatches{{display:flex;gap:.45rem;align-items:center;}}
.t-sw{{
  width:14px;height:14px;border-radius:50%;
  border:2px solid transparent;transition:transform .2s;cursor:pointer;
}}
.t-sw.on{{border-color:white;transform:scale(1.28);}}
.t-sw:not(.on):hover{{transform:scale(1.15);}}
.t-name{{
  margin-left:auto;font-family:'Space Mono',monospace;
  font-size:.54rem;letter-spacing:.18em;text-transform:uppercase;color:var(--dim);
}}

/* ── HERO ── */
.hero-banner{{
  position:relative;overflow:hidden;border-radius:0 0 20px 20px;
  padding:3.4rem 3rem 3rem;margin-bottom:2.2rem;
  background:linear-gradient(135deg,{g1} 0%,{g2} 35%,{g3} 70%,{g4} 100%);
  border-bottom:1px solid {a}40;text-align:center;
}}
.hero-banner::before{{
  content:'';position:absolute;inset:0;
  background:
    radial-gradient(ellipse 80% 70% at 50% 0%,{g1} 0%,transparent 60%),
    radial-gradient(ellipse 50% 50% at 15% 100%,{g2} 0%,transparent 60%),
    radial-gradient(ellipse 50% 50% at 85% 100%,{g3} 0%,transparent 60%);
  animation:banner-pulse 8s ease-in-out infinite alternate;
}}
@keyframes banner-pulse{{0%{{opacity:.7;}}50%{{opacity:1;}}100%{{opacity:.75;}}}}
.orb{{position:absolute;border-radius:50%;filter:blur(36px);animation:orb-float 12s ease-in-out infinite alternate;}}
.orb-1{{width:200px;height:200px;background:{g1};top:-50px;left:3%;animation-delay:0s;}}
.orb-2{{width:160px;height:160px;background:{g2};top:-30px;right:5%;animation-delay:-4s;}}
.orb-3{{width:130px;height:130px;background:{g3};bottom:-30px;left:28%;animation-delay:-7s;}}
.orb-4{{width:110px;height:110px;background:{g4};bottom:-20px;right:22%;animation-delay:-10s;}}
@keyframes orb-float{{
  0%{{transform:translate(0,0) scale(1);}}
  50%{{transform:translate(18px,-22px) scale(1.1);}}
  100%{{transform:translate(-12px,12px) scale(.93);}}
}}
.hero-badge{{
  display:inline-flex;align-items:center;gap:.4rem;
  font-family:'Space Mono',monospace;font-size:.55rem;
  letter-spacing:.22em;text-transform:uppercase;
  color:{a_l};background:{a}18;border:1px solid {a}40;
  border-radius:999px;padding:.3rem .9rem;margin-bottom:1rem;
  position:relative;z-index:1;
}}
.hero-title{{
  font-family:'Outfit',sans-serif;font-size:3.1rem;font-weight:800;
  letter-spacing:-.04em;line-height:1;position:relative;z-index:1;
  background:linear-gradient(135deg,{tg});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  background-size:200% 200%;animation:tshimmer 5s ease-in-out infinite alternate;
}}
@keyframes tshimmer{{0%{{background-position:0% 50%;}}100%{{background-position:100% 50%;}}}}
.hero-sub{{
  font-family:'Space Mono',monospace;font-size:.65rem;letter-spacing:.18em;
  text-transform:uppercase;color:var(--dim);margin-top:.9rem;
  position:relative;z-index:1;
}}
.hero-pills{{
  display:flex;gap:.55rem;justify-content:center;
  margin-top:1.3rem;flex-wrap:wrap;position:relative;z-index:1;
}}
.hero-pill{{
  font-family:'Space Mono',monospace;font-size:.58rem;letter-spacing:.08em;
  padding:.28rem .8rem;border-radius:999px;
  border:1px solid {a}45;color:{a_l};background:{a}14;
}}

/* ── SECTION LABEL ── */
.rm-label{{
  font-family:'Space Mono',monospace;font-size:.58rem;font-weight:700;
  letter-spacing:.26em;text-transform:uppercase;margin-bottom:.9rem;
  display:flex;align-items:center;gap:.6rem;
  background:linear-gradient(90deg,{b_l},{c});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.rm-label::before{{
  content:'';display:inline-block;width:18px;height:2px;border-radius:1px;
  background:linear-gradient(90deg,{a},{c});flex-shrink:0;
  -webkit-text-fill-color:unset;
}}

/* ── INPUT ── */
[data-testid="stTextInput"]>label{{display:none!important;}}
[data-testid="stTextInput"] input{{
  background:var(--surf)!important;border:1px solid var(--brd2)!important;
  border-radius:10px!important;color:var(--white)!important;
  font-family:'Outfit',sans-serif!important;font-size:.95rem!important;
  padding:.85rem 1.05rem!important;
  transition:border-color .3s,box-shadow .3s!important;
  caret-color:{a_l}!important;
}}
[data-testid="stTextInput"] input::placeholder{{color:var(--faint)!important;}}
[data-testid="stTextInput"] input:focus{{
  border-color:{a}!important;outline:none!important;
  box-shadow:0 0 0 3px {a}28!important;
}}

/* ── BUTTON ── */
[data-testid="stButton"]>button{{
  border:none!important;border-radius:10px!important;
  color:#fff!important;font-family:'Outfit',sans-serif!important;
  font-size:.82rem!important;font-weight:700!important;
  letter-spacing:.14em!important;text-transform:uppercase!important;
  padding:.85rem 1.4rem!important;width:100%!important;
  background:linear-gradient(135deg,{a} 0%,{b} 55%,{c_d} 100%)!important;
  background-size:200% 200%!important;
  animation:btn-flow 4s ease-in-out infinite alternate!important;
  transition:transform .2s,box-shadow .2s!important;cursor:pointer!important;
}}
@keyframes btn-flow{{0%{{background-position:0% 50%;}}100%{{background-position:100% 50%;}}}}
[data-testid="stButton"]>button:hover{{
  transform:translateY(-2px)!important;box-shadow:0 10px 32px {a}55!important;
}}
[data-testid="stButton"]>button:active{{transform:translateY(0)!important;}}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"]>label{{display:none!important;}}
[data-testid="stSelectbox"]>div>div{{
  background:var(--surf)!important;border:1px solid var(--brd2)!important;
  border-radius:8px!important;color:var(--text)!important;
  font-family:'Space Mono',monospace!important;font-size:.7rem!important;
}}

/* ── DOWNLOAD BUTTON ── */
[data-testid="stDownloadButton"]>button{{
  background:transparent!important;border:1px solid var(--brd2)!important;
  border-radius:8px!important;color:var(--dim)!important;
  font-family:'Space Mono',monospace!important;font-size:.62rem!important;
  letter-spacing:.14em!important;text-transform:uppercase!important;
  padding:.65rem 1.2rem!important;width:100%!important;transition:all .25s!important;
}}
[data-testid="stDownloadButton"]>button:hover{{
  border-color:{c}!important;color:{c}!important;
  background:{c}12!important;box-shadow:0 0 14px {c}22!important;
}}

/* ── PIPELINE CARD ── */
.pipeline-card{{
  background:var(--surf);border:1px solid var(--brd);
  border-radius:14px;padding:1.5rem;position:relative;overflow:hidden;
}}
.pipeline-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,{a},{b},{c},{acc});
  background-size:300% 100%;animation:shimbar 4s linear infinite;
}}
@keyframes shimbar{{0%{{background-position:300% 0;}}100%{{background-position:-300% 0;}}}}
.step-list{{position:relative;padding-left:0;}}
.step-rail{{
  position:absolute;left:19px;top:28px;bottom:28px;
  width:2px;background:var(--brd);border-radius:1px;overflow:hidden;
}}
.step-rail-fill{{
  position:absolute;left:0;top:0;width:100%;
  background:linear-gradient(180deg,{a},{b},{c});
  transition:height 1.2s cubic-bezier(.22,1,.36,1);border-radius:1px;
}}
.step-row{{
  display:flex;align-items:center;gap:.9rem;padding:.7rem 0;
  position:relative;z-index:1;
}}
.step-dot{{
  width:40px;height:40px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;flex-shrink:0;
  font-family:'Space Mono',monospace;font-size:.58rem;font-weight:700;
  border:2px solid var(--brd);background:var(--bg2);color:var(--faint);
  transition:all .4s cubic-bezier(.22,1,.36,1);position:relative;
}}
.step-dot.active{{
  border-color:{a_l};background:{a}20;color:{a_l};
  box-shadow:0 0 0 5px {a}18,0 0 18px {a}30;
}}
.step-dot.active::after{{
  content:'';position:absolute;inset:-6px;border-radius:50%;
  border:1.5px solid {a}44;animation:pring 1.6s ease-out infinite;
}}
@keyframes pring{{0%{{transform:scale(1);opacity:.8;}}100%{{transform:scale(1.8);opacity:0;}}}}
.step-dot.done{{
  border-color:var(--green);background:rgba(52,211,153,.12);color:var(--green);
  box-shadow:0 0 10px rgba(52,211,153,.22);
}}
.step-info{{flex:1;min-width:0;}}
.step-name{{
  font-family:'Outfit',sans-serif;font-size:.82rem;font-weight:500;
  color:var(--faint);transition:color .4s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
}}
.step-name.active{{color:var(--white);}}
.step-name.done{{color:var(--dim);}}
.step-tag{{
  font-family:'Space Mono',monospace;font-size:.52rem;
  color:var(--faint);margin-top:.1rem;letter-spacing:.06em;
}}
.step-tag.active{{color:{a_l};}}
.step-tag.done{{color:var(--gd);}}
.step-time{{
  font-family:'Space Mono',monospace;font-size:.58rem;color:var(--green);
  margin-left:auto;flex-shrink:0;opacity:0;transition:opacity .5s .3s;text-align:right;
}}
.step-time.show{{opacity:1;}}
.stats-row{{display:flex;gap:.5rem;margin-top:1.3rem;}}
.stat-chip{{
  flex:1;font-family:'Space Mono',monospace;font-size:.57rem;
  letter-spacing:.1em;text-transform:uppercase;padding:.42rem .5rem;
  border-radius:6px;border:1px solid;text-align:center;
}}
.stat-chip.done{{border-color:rgba(52,211,153,.3);color:var(--green);background:rgba(52,211,153,.07);}}
.stat-chip.agents{{border-color:{a}55;color:{a_l};background:{a}10;}}
.stat-chip.time{{border-color:{c}55;color:{c};background:{c}10;}}

/* ── H-STEPS ── */
.h-steps-wrap{{
  display:flex;align-items:stretch;background:var(--bg2);
  border:1px solid var(--brd);border-radius:10px;padding:.9rem 1.4rem;
  margin-bottom:1.6rem;position:relative;overflow:hidden;
}}
.h-steps-wrap::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,{a},{b},{c});
  background-size:200% 100%;animation:shimbar 3s linear infinite;
}}
.h-step{{flex:1;display:flex;align-items:center;gap:.6rem;position:relative;}}
.h-step:not(:last-child)::after{{
  content:'›';position:absolute;right:-.3rem;top:50%;transform:translateY(-50%);
  color:var(--brd2);font-size:1.1rem;z-index:1;transition:color .4s;
}}
.h-step.done:not(:last-child)::after{{color:var(--green);}}
.h-dot{{
  width:30px;height:30px;border-radius:50%;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;
  font-family:'Space Mono',monospace;font-size:.55rem;font-weight:700;
  border:1.5px solid var(--brd2);background:var(--bg2);color:var(--faint);transition:all .4s;
}}
.h-dot.active{{border-color:{a_l};background:{a}20;color:{a_l};}}
.h-dot.done{{border-color:var(--green);background:rgba(52,211,153,.12);color:var(--green);}}
.h-step-lbl{{font-family:'Outfit',sans-serif;font-size:.75rem;font-weight:500;color:var(--faint);transition:color .4s;}}
.h-step-lbl.active{{color:{a_l};}}
.h-step-lbl.done{{color:var(--green);}}
.h-step-sub{{font-family:'Space Mono',monospace;font-size:.52rem;color:var(--faint);}}
.h-step-sub.done{{color:var(--gd);}}

/* ── CONTENT CARD ── */
.content-card{{
  background:var(--surf);border:1px solid var(--brd);
  border-radius:14px;padding:1.9rem;margin-bottom:1rem;
  position:relative;overflow:hidden;animation:fade-up .4s ease both;
}}
.content-card::before{{
  content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,{a},{b_l} 40%,{c} 70%,transparent);opacity:.65;
}}

/* ── REPORT MARKDOWN ── */
.report-scroll{{max-height:520px;overflow-y:auto;padding-right:.5rem;}}
.report-md{{
  font-family:'Lora',Georgia,serif;
  font-size:.91rem;line-height:1.95;color:var(--text);word-break:break-word;
}}
.report-md h1{{
  font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:700;
  margin:0 0 1rem;letter-spacing:-.02em;
  background:linear-gradient(90deg,{a_l},{b_l});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
}}
.report-md h2{{
  font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:600;
  color:{a_l};margin:1.6rem 0 .5rem;letter-spacing:-.01em;
  padding-bottom:.3rem;border-bottom:1px solid var(--brd);
}}
.report-md h3{{
  font-family:'Outfit',sans-serif;font-size:.92rem;font-weight:600;
  color:{b_l};margin:1.1rem 0 .4rem;
}}
.report-md h4,.report-md h5,.report-md h6{{
  font-family:'Outfit',sans-serif;font-size:.85rem;font-weight:600;
  color:var(--text);margin:.9rem 0 .3rem;
}}
.report-md p{{margin-bottom:.85rem;}}
.report-md strong,.report-md b{{color:var(--white);font-weight:600;}}
.report-md em,.report-md i{{color:{c};font-style:italic;}}
.report-md ul,.report-md ol{{margin:.5rem 0 .8rem 1.4rem;}}
.report-md li{{margin-bottom:.35rem;line-height:1.75;}}
.report-md a{{color:{b_l};text-decoration:none;border-bottom:1px solid {b}40;transition:border-color .2s;}}
.report-md a:hover{{border-color:{b_l};}}
.report-md blockquote{{
  border-left:3px solid {a};margin:.8rem 0;
  padding:.5rem 1rem;background:{a}0f;
  border-radius:0 6px 6px 0;color:var(--dim);font-style:italic;
}}
.report-md code{{
  font-family:'Space Mono',monospace;font-size:.78rem;
  background:var(--brd);color:{c};padding:.1rem .4rem;border-radius:3px;
}}
.report-md pre{{
  background:var(--bg2);border:1px solid var(--brd);
  border-radius:6px;padding:.8rem 1rem;overflow-x:auto;margin:.8rem 0;white-space:pre;
}}
.report-md pre code{{background:none;padding:0;color:{c};}}
.report-md hr{{border:none;border-top:1px solid var(--brd2);margin:1.2rem 0;}}

/* ── SCORE PANEL ── */
.score-panel{{
  display:flex;align-items:center;gap:1.6rem;padding:1.3rem 1.5rem;
  background:{a}0d;border:1px solid {a}30;
  border-radius:10px;margin-bottom:1.5rem;position:relative;overflow:hidden;
}}
.score-panel::before{{
  content:'';position:absolute;inset:0;
  background:linear-gradient(135deg,{a}0e,{b}07,transparent);pointer-events:none;
}}
.score-ring-wrap{{position:relative;width:80px;height:80px;flex-shrink:0;}}
.score-ring-wrap svg{{transform:rotate(-90deg);}}
.score-ring-bg{{fill:none;stroke:var(--brd2);stroke-width:5;}}
.score-ring-fill{{fill:none;stroke-width:5;stroke-linecap:round;}}
.score-center{{
  position:absolute;inset:0;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
}}
.score-num{{font-family:'Outfit',sans-serif;font-size:1.4rem;font-weight:800;color:var(--white);line-height:1;letter-spacing:-.04em;}}
.score-denom{{font-family:'Space Mono',monospace;font-size:.5rem;color:var(--dim);}}
.score-meta{{flex:1;}}
.score-title{{font-family:'Outfit',sans-serif;font-size:1rem;font-weight:600;color:var(--white);margin-bottom:.65rem;}}
.score-bars{{display:flex;flex-direction:column;gap:.42rem;}}
.score-bar-row{{display:flex;align-items:center;gap:.6rem;}}
.score-bar-lbl{{
  font-family:'Space Mono',monospace;font-size:.54rem;color:var(--dim);
  width:60px;text-transform:uppercase;letter-spacing:.08em;flex-shrink:0;
}}
.score-bar-track{{flex:1;height:3px;background:var(--brd);border-radius:2px;overflow:hidden;}}
.score-bar-fill{{height:100%;border-radius:2px;}}
.score-bar-val{{font-family:'Space Mono',monospace;font-size:.56rem;color:var(--dim);width:24px;text-align:right;flex-shrink:0;}}

/* ── FEEDBACK MARKDOWN ── */
.feedback-md{{
  font-family:'Space Mono',monospace;font-size:.68rem;
  line-height:1.95;color:var(--dim);letter-spacing:.02em;
}}
.feedback-md strong,.feedback-md b{{color:var(--text);}}
.feedback-md h1,.feedback-md h2,.feedback-md h3,.feedback-md h4{{
  font-family:'Outfit',sans-serif;color:{a_l};font-size:.8rem;
  margin:.8rem 0 .3rem;font-weight:600;
}}
.feedback-md ul,.feedback-md ol{{margin:.4rem 0 .6rem 1.2rem;}}
.feedback-md li{{margin-bottom:.3rem;}}
.feedback-md p{{margin-bottom:.5rem;}}
.feedback-md code{{
  font-size:.7rem;background:var(--brd);color:{c};
  padding:.1rem .35rem;border-radius:3px;
}}

/* ── NO SCORE ── */
.no-score{{
  font-family:'Space Mono',monospace;font-size:.6rem;
  color:var(--faint);font-style:italic;margin-bottom:1rem;
}}

/* ── WARN BOX ── */
.warn-box{{
  background:rgba(248,113,113,.07);border:1px solid rgba(248,113,113,.25);
  border-radius:8px;padding:.75rem 1rem;margin-bottom:.8rem;
  font-family:'Space Mono',monospace;font-size:.65rem;
  color:var(--red);letter-spacing:.04em;line-height:1.7;
}}

/* ── EMPTY STATE ── */
.empty-card{{
  background:var(--surf);border:1px solid var(--brd);border-radius:14px;
  min-height:440px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;
  gap:1.2rem;text-align:center;position:relative;overflow:hidden;padding:2rem;
}}
.empty-card::before{{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse 60% 60% at 50% 50%,{a}0c 0%,transparent 70%);
  animation:epulse 5s ease-in-out infinite alternate;
}}
@keyframes epulse{{0%{{opacity:.4;}}100%{{opacity:1;}}}}
.empty-glyph{{
  font-size:3.5rem;line-height:1;
  background:linear-gradient(135deg,{a},{b},{c});
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  animation:gfloat 4s ease-in-out infinite alternate;position:relative;
}}
@keyframes gfloat{{0%{{opacity:.12;transform:translateY(0);}}100%{{opacity:.28;transform:translateY(-10px);}}}}
.empty-title{{
  font-family:'Space Mono',monospace;font-size:.62rem;
  letter-spacing:.22em;text-transform:uppercase;color:var(--faint);position:relative;
}}
.empty-body{{
  font-family:'Outfit',sans-serif;font-size:.8rem;font-weight:300;
  color:var(--faint);line-height:1.85;max-width:260px;position:relative;
}}
.empty-steps{{
  display:flex;gap:.5rem;margin-top:.4rem;flex-wrap:wrap;
  justify-content:center;position:relative;
}}
.empty-step{{
  font-family:'Space Mono',monospace;font-size:.54rem;
  letter-spacing:.08em;padding:.22rem .65rem;border-radius:999px;
  border:1px solid {a}35;color:{a_l};background:{a}0e;
}}

/* ── STATUS WIDGET ── */
[data-testid="stStatus"]{{
  background:var(--surf2)!important;
  border:1px solid {a}44!important;border-radius:10px!important;
}}
[data-testid="stStatusLabel"]{{
  font-family:'Space Mono',monospace!important;
  font-size:.66rem!important;color:{a_l}!important;letter-spacing:.08em!important;
}}

@keyframes fade-up{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}
</style>
""", unsafe_allow_html=True)


inject_css(T)

# ── THEME BAR ──────────────────────────────────────────────────────────────────
_sw_html = (
    '<div class="theme-strip">'
    '<span class="theme-strip-label">Theme</span>'
    '<div class="t-swatches">'
)
for _n, _th in THEMES.items():
    _on = "on" if _n == st.session_state.theme else ""
    _sw_html += f'<div class="t-sw {_on}" style="background:{_th["swatch"]}" title="{_n}"></div>'
_sw_html += f'</div><span class="t-name">{st.session_state.theme}</span></div>'
st.markdown(_sw_html, unsafe_allow_html=True)

_pc, _ = st.columns([1, 5])
with _pc:
    _chosen = st.selectbox(
        "Theme",
        list(THEMES.keys()),
        index=list(THEMES.keys()).index(st.session_state.theme),
        label_visibility="collapsed",
        key="theme_picker",
    )
if _chosen != st.session_state.theme:
    st.session_state.theme = _chosen
    st.rerun()

# ── HERO ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
  <div class="orb orb-1"></div><div class="orb orb-2"></div>
  <div class="orb orb-3"></div><div class="orb orb-4"></div>
  <div class="hero-badge">&#9672; Multi-Agent Research Pipeline</div>
  <div class="hero-title">ResearchMind AI</div>
  <div class="hero-sub">Search &nbsp;&middot;&nbsp; Scrape &nbsp;&middot;&nbsp; Write &nbsp;&middot;&nbsp; Critique</div>
  <div class="hero-pills">
    <span class="hero-pill">AI breakthroughs</span>
    <span class="hero-pill">Quantum computing</span>
    <span class="hero-pill">Climate solutions</span>
    <span class="hero-pill">Space discoveries</span>
    <span class="hero-pill">Biotech frontiers</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STEP DEFINITIONS ───────────────────────────────────────────────────────────
STEPS = [
    ("01", "Web Search Agent", "Search", "Fetching web results"),
    ("02", "Content Scraper",  "Scrape", "Reading source pages"),
    ("03", "Report Writer",    "Write",  "Drafting the report"),
    ("04", "Critic & Scorer",  "Review", "Evaluating quality"),
]

# ── COLUMNS ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 2.1], gap="large")

_completed       = st.session_state.completed_steps
_pipeline_running = st.session_state["_pipeline_running"]
_fill_pct        = (len(_completed) / 4) * 100

# ── LEFT PANEL ─────────────────────────────────────────────────────────────────
with col_left:
    st.markdown('<div class="rm-label">Research Topic</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "topic",
        placeholder="e.g. The future of nuclear fusion energy...",
        label_visibility="collapsed",
        key="topic_input",
    )
    st.markdown("<div style='height:.4rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Launch Research", use_container_width=True)
    st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)

    st.markdown('<div class="pipeline-card">', unsafe_allow_html=True)
    st.markdown('<div class="rm-label" style="margin-bottom:1.2rem">Pipeline Status</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="step-list">
      <div class="step-rail">
        <div class="step-rail-fill" style="height:{_fill_pct}%"></div>
      </div>
    """, unsafe_allow_html=True)

    for _i, (_num, _lbl, _short, _sublbl) in enumerate(STEPS, 1):
        _done   = _i in _completed
        _active = (not _done) and (_i == len(_completed) + 1) and _pipeline_running
        _dc     = "done" if _done else ("active" if _active else "")
        _nc     = "done" if _done else ("active" if _active else "")
        _dur    = st.session_state.durations.get(_i, "")
        _tc     = "show" if _dur else ""
        _sym    = "&#10003;" if _done else _num
        _subc   = "done" if _done else ("active" if _active else "")
        _subt   = _dur if _done else ("Running..." if _active else _sublbl)
        st.markdown(f"""
        <div class="step-row">
          <div class="step-dot {_dc}">{_sym}</div>
          <div class="step-info">
            <div class="step-name {_nc}">{_lbl}</div>
            <div class="step-tag {_subc}">{_subt}</div>
          </div>
          <div class="step-time {_tc}">{_dur}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if len(_completed) == 4:
        _total = sum(
            float(v.replace("s", ""))
            for v in st.session_state.durations.values() if v
        )
        st.markdown(f"""
        <div class="stats-row">
          <div class="stat-chip done">&#10003; Done</div>
          <div class="stat-chip agents">4 Agents</div>
          <div class="stat-chip time">{_total:.0f}s</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ── RIGHT PANEL ────────────────────────────────────────────────────────────────
with col_right:

    if run_btn:
        if not topic or not topic.strip():
            st.markdown(
                '<div class="warn-box">&#9888; Please enter a research topic to continue.</div>',
                unsafe_allow_html=True,
            )
        else:
            import time as _time

            st.session_state.result           = None
            st.session_state.completed_steps  = []
            st.session_state.durations        = {}
            st.session_state.topic_done       = topic.strip()
            st.session_state["_pipeline_running"] = True

            try:
                from agents import (
                    build_search_agent, build_reader_agent,
                    writer_chain, critic_chain,
                )
            except ImportError as _ie:
                st.markdown(
                    f'<div class="warn-box">&#9888; Cannot import agents.py: '
                    f'{_html_mod.escape(str(_ie))}</div>',
                    unsafe_allow_html=True,
                )
                st.session_state["_pipeline_running"] = False
                st.stop()

            _state = {}
            _ok    = True

            with st.status("Initialising pipeline...", expanded=True) as _status:

                # Step 1
                if _ok:
                    try:
                        _t = _time.time()
                        _status.update(label="Step 1 — Web Search Agent running...")
                        _r = build_search_agent().invoke({
                            "messages": [("user",
                                f"Find recent, reliable and detailed information about: {topic}"
                            )]
                        })
                        _state["search_results"] = _r["messages"][-1].content
                        _d = _time.time() - _t
                        st.session_state.completed_steps.append(1)
                        st.session_state.durations[1] = f"{_d:.1f}s"
                        _status.write(f"Web search complete — {_d:.1f}s")
                    except Exception as _e:
                        _ok = False
                        _status.update(label="Stopped at Step 1.", state="error", expanded=False)
                        _err_msg = _html_mod.escape(str(_e))

                # Step 2
                if _ok:
                    try:
                        _t = _time.time()
                        _status.update(label="Step 2 — Scraper reading sources...")
                        _r2 = build_reader_agent().invoke({
                            "messages": [("user",
                                f"Based on these search results about '{topic}', "
                                f"scrape the most relevant URLs for deeper content.\n\n"
                                f"Search Results:\n{_state['search_results'][:1200]}"
                            )]
                        })
                        _state["scraped_content"] = _r2["messages"][-1].content
                        _d = _time.time() - _t
                        st.session_state.completed_steps.append(2)
                        st.session_state.durations[2] = f"{_d:.1f}s"
                        _status.write(f"Scraping complete — {_d:.1f}s")
                    except Exception as _e:
                        _ok = False
                        _status.update(label="Stopped at Step 2.", state="error", expanded=False)
                        _err_msg = _html_mod.escape(str(_e))

                # Step 3
                if _ok:
                    try:
                        _t = _time.time()
                        _status.update(label="Step 3 — Writer drafting report...")
                        _combined = (
                            f"SEARCH RESULTS:\n{_state['search_results']}\n\n"
                            f"SCRAPED CONTENT:\n{_state['scraped_content']}"
                        )
                        _state["report"] = writer_chain.invoke({
                            "topic": topic, "research": _combined
                        })
                        _d = _time.time() - _t
                        st.session_state.completed_steps.append(3)
                        st.session_state.durations[3] = f"{_d:.1f}s"
                        _status.write(f"Report drafted — {_d:.1f}s")
                    except Exception as _e:
                        _ok = False
                        _status.update(label="Stopped at Step 3.", state="error", expanded=False)
                        _err_msg = _html_mod.escape(str(_e))

                # Step 4
                if _ok:
                    try:
                        _t = _time.time()
                        _status.update(label="Step 4 — Critic reviewing quality...")
                        _state["feedback"] = critic_chain.invoke({"report": _state["report"]})
                        _d = _time.time() - _t
                        st.session_state.completed_steps.append(4)
                        st.session_state.durations[4] = f"{_d:.1f}s"
                        _status.write(f"Review complete — {_d:.1f}s")
                    except Exception as _e:
                        _ok = False
                        _status.update(label="Stopped at Step 4.", state="error", expanded=False)
                        _err_msg = _html_mod.escape(str(_e))

                if _ok:
                    _status.update(label="Pipeline complete.", state="complete", expanded=False)

            st.session_state["_pipeline_running"] = False

            if _ok:
                st.session_state.result = _state
                st.rerun()
            else:
                st.markdown(
                    f'<div class="warn-box">&#9888; Pipeline error: {_err_msg}</div>',
                    unsafe_allow_html=True,
                )

    # ── RESULTS ───────────────────────────────────────────────────────────────
    if st.session_state.result:
        _res      = st.session_state.result
        _compl    = st.session_state.completed_steps
        _running  = st.session_state["_pipeline_running"]

        # Horizontal tracker
        _parts = []
        for _i, (_num, _lbl, _short, _sub) in enumerate(STEPS, 1):
            _done   = _i in _compl
            _active = (not _done) and (_i == len(_compl) + 1) and _running
            _dc     = "done" if _done else ("active" if _active else "")
            _lc     = "done" if _done else ("active" if _active else "")
            _sc     = "done" if _done else ""
            _sym    = "&#10003;" if _done else _num
            _subt   = "Completed" if _done else ("Running..." if _active else "Pending")
            _cls    = "h-step done" if _done else ("h-step active" if _active else "h-step")
            _parts.append(
                f'<div class="{_cls}">'
                f'<div class="h-dot {_dc}">{_sym}</div>'
                f'<div>'
                f'<div class="h-step-lbl {_lc}">{_short}</div>'
                f'<div class="h-step-sub {_sc}">{_subt}</div>'
                f'</div></div>'
            )
        st.markdown(
            '<div class="h-steps-wrap">' + "".join(_parts) + "</div>",
            unsafe_allow_html=True,
        )

        # Report card
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="rm-label">Research Report</div>', unsafe_allow_html=True)
        _report_text = _res.get("report") or ""
        st.markdown(
            f'<div class="report-scroll">{render_md(_report_text, "report-md")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        if _report_text:
            st.download_button(
                label="Download Report (.md)",
                data=_report_text,
                file_name="research_report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        st.markdown("<div style='height:.8rem'></div>", unsafe_allow_html=True)

        # Quality card
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.markdown('<div class="rm-label">Report Quality</div>', unsafe_allow_html=True)

        _feedback   = _res.get("feedback") or ""
        _score_data = parse_score(_feedback)
        _body_text  = strip_score_line(_feedback)

        if _score_data:
            _disp, _pct, _nv, _denom = _score_data
            _circ  = 2 * 3.14159265 * 30
            _df    = _circ * (_pct / 100)
            _de    = _circ - _df

            _rel = min(10.0, _nv + 0.2)
            _acc = _nv
            _dep = max(0.0, _nv - 0.2)
            _src = min(10.0, _nv + 0.1)
            _dn  = _disp.split("/")[0]

            st.markdown(f"""
            <div class="score-panel">
              <div class="score-ring-wrap">
                <svg width="80" height="80" viewBox="0 0 80 80">
                  <defs>
                    <linearGradient id="sg" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%"   stop-color="{T['a']}"/>
                      <stop offset="50%"  stop-color="{T['b']}"/>
                      <stop offset="100%" stop-color="{T['c']}"/>
                    </linearGradient>
                  </defs>
                  <circle class="score-ring-bg"   cx="40" cy="40" r="30"/>
                  <circle class="score-ring-fill" cx="40" cy="40" r="30"
                    stroke="url(#sg)"
                    stroke-dasharray="{_df:.2f} {_de:.2f}"
                    stroke-dashoffset="0"/>
                </svg>
                <div class="score-center">
                  <div class="score-num">{_dn}</div>
                  <div class="score-denom">/ {_denom:.0f}</div>
                </div>
              </div>
              <div class="score-meta">
                <div class="score-title">Quality Score</div>
                <div class="score-bars">
                  <div class="score-bar-row">
                    <div class="score-bar-lbl">Relevance</div>
                    <div class="score-bar-track"><div class="score-bar-fill" style="width:{min(100,_rel*10):.0f}%;background:{bar_color(_rel)}"></div></div>
                    <div class="score-bar-val">{_rel:.1f}</div>
                  </div>
                  <div class="score-bar-row">
                    <div class="score-bar-lbl">Accuracy</div>
                    <div class="score-bar-track"><div class="score-bar-fill" style="width:{min(100,_acc*10):.0f}%;background:{bar_color(_acc)}"></div></div>
                    <div class="score-bar-val">{_acc:.1f}</div>
                  </div>
                  <div class="score-bar-row">
                    <div class="score-bar-lbl">Depth</div>
                    <div class="score-bar-track"><div class="score-bar-fill" style="width:{min(100,_dep*10):.0f}%;background:{bar_color(_dep)}"></div></div>
                    <div class="score-bar-val">{_dep:.1f}</div>
                  </div>
                  <div class="score-bar-row">
                    <div class="score-bar-lbl">Sources</div>
                    <div class="score-bar-track"><div class="score-bar-fill" style="width:{min(100,_src*10):.0f}%;background:{bar_color(_src)}"></div></div>
                    <div class="score-bar-val">{_src:.1f}</div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(
                '<div class="no-score">No numeric score found in critic output.</div>',
                unsafe_allow_html=True,
            )

        if _body_text:
            st.markdown(render_md(_body_text, "feedback-md"), unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    elif not run_btn:
        st.markdown("""
        <div class="empty-card">
          <div class="empty-glyph">&#9672;</div>
          <div class="empty-title">Awaiting Research Topic</div>
          <div class="empty-body">
            Enter a topic on the left and launch the pipeline.
            Four specialised AI agents will search the web, scrape sources,
            write a structured report, and critique its quality.
          </div>
          <div class="empty-steps">
            <span class="empty-step">01 Search</span>
            <span class="empty-step">02 Scrape</span>
            <span class="empty-step">03 Write</span>
            <span class="empty-step">04 Review</span>
          </div>
        </div>
        """, unsafe_allow_html=True)