import json
import queue
import re
import threading
from html import escape
from pathlib import Path

import streamlit as st
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from tavily import TavilyClient

st.set_page_config(page_title="Pathfinder AI", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------
# Bright premium UI
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');
:root { --ink:#332b2a; --soft-ink:#655856; --muted:#8f7f7a; --paper:#f8f3ef; --panel:#fffaf7; --line:rgba(91,61,55,.13); --rose:#e88ca4; --coral:#f3ad9c; --lilac:#b2a2d8; --plum:#71546e; }
#MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"], [data-testid="stStatusWidget"] { display:none !important; visibility:hidden !important; }
[data-testid="stHeader"], .stApp > footer, footer { display:none !important; height:0 !important; }
[data-testid="stAppViewContainer"] { padding-top:0 !important; }
/* Remove Streamlit's generic bottom shell/footer while preserving the custom chat dock. */
section[data-testid="stBottomBlockContainer"], div[data-testid="stBottomBlockContainer"], [data-testid="stBottomBlockContainer"] { background:transparent !important; border:0 !important; box-shadow:none !important; padding:0 !important; min-height:0 !important; }
section[data-testid="stBottomBlockContainer"] > div, div[data-testid="stBottomBlockContainer"] > div { background:transparent !important; border:0 !important; box-shadow:none !important; padding:0 !important; }
section[data-testid="stBottomBlockContainer"]::before, section[data-testid="stBottomBlockContainer"]::after, [data-testid="stBottomBlockContainer"]::before, [data-testid="stBottomBlockContainer"]::after { display:none !important; content:none !important; }
.stApp > footer, .stApp footer, footer, [data-testid="stFooter"], [data-testid="stBottomBlockContainer"] footer { display:none !important; visibility:hidden !important; height:0 !important; min-height:0 !important; margin:0 !important; padding:0 !important; }
[data-testid="stBottomBlockContainer"] { pointer-events:none !important; }
[data-testid="stBottomBlockContainer"] [data-testid="stChatInput"] { pointer-events:auto !important; }
.stApp { min-height:100vh; color:var(--ink); background:radial-gradient(circle at 4% 4%,rgba(244,188,203,.30),transparent 25%),radial-gradient(circle at 95% 2%,rgba(215,199,233,.33),transparent 28%),linear-gradient(180deg,#fbf7f4 0%,#f6efeb 72%,#f3e9e4 100%); font-family:'Manrope',sans-serif; }
.stApp:before { content:""; position:fixed; inset:0; pointer-events:none; opacity:.18; background-image:radial-gradient(rgba(90,57,51,.12) .55px,transparent .55px); background-size:7px 7px; mask-image:linear-gradient(to bottom,black,transparent 80%); }
.block-container { max-width:1190px; padding:24px 46px 185px; }
.nav { position:sticky; top:14px; z-index:100; display:flex; align-items:center; justify-content:space-between; gap:18px; padding:13px 2px; margin-bottom:28px; background:rgba(250,245,241,.76); backdrop-filter:blur(20px); }
.brand { display:flex; align-items:center; font-size:13px; font-weight:800; letter-spacing:.3px; color:#3e3030; text-transform:uppercase; }.brand-mark { display:inline-flex; align-items:center; justify-content:center; width:30px; height:30px; border-radius:50%; margin-right:9px; color:#fffaf7; background:linear-gradient(145deg,#4b3e42,#a67187); box-shadow:0 7px 20px rgba(115,73,90,.22); }.nav-copy { color:#9a8883; font-size:10px; font-weight:800; letter-spacing:1.1px; text-transform:uppercase; }
.hero { position:relative; overflow:hidden; padding:48px 42px 46px; margin-bottom:28px; min-height:238px; border:1px solid rgba(154,91,103,.11); border-radius:25px; background:linear-gradient(112deg,#efb3c1 0%,#f4c2b1 48%,#f6ddd0 100%); box-shadow:0 24px 55px rgba(141,96,88,.13); }.hero:before { content:""; position:absolute; width:390px; height:260px; right:-100px; top:-85px; border-radius:50%; background:radial-gradient(circle,rgba(255,249,241,.55),rgba(255,249,241,0) 68%); }.hero:after { content:""; position:absolute; width:230px; height:230px; right:13%; bottom:-155px; border-radius:50%; background:rgba(190,155,203,.27); filter:blur(12px); }.eyebrow { position:relative; z-index:1; display:inline-flex; align-items:center; gap:8px; padding:7px 10px; border-radius:4px; background:rgba(255,250,247,.28); border:1px solid rgba(98,58,64,.15); color:#735157; font-family:'DM Mono',monospace; font-size:9px; font-weight:500; letter-spacing:1px; }.hero h1 { position:relative; z-index:1; max-width:630px; font-family:'Playfair Display',serif; font-size:clamp(46px,6vw,76px)!important; line-height:.98!important; letter-spacing:-3px!important; margin:22px 0 14px!important; color:#382b2a!important; }.gradient { background:linear-gradient(90deg,#9d526e,#725871 52%,#9e749b); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }.subtitle { position:relative; z-index:1; max-width:620px; color:#755d5d; font-size:15px; line-height:1.7; }
.section-title { display:flex; align-items:center; gap:12px; margin:31px 0 12px; font-size:10px; font-weight:800; color:#735f5c; letter-spacing:1.2px; text-transform:uppercase; }.section-title:after { content:""; height:1px; flex:1; background:linear-gradient(90deg,rgba(115,84,78,.20),transparent); }.muted { color:var(--soft-ink); line-height:1.7; }.small { color:#9b8782; font-family:'DM Mono',monospace; font-size:9px; letter-spacing:.25px; text-transform:uppercase; }.card { border:1px solid var(--line); border-radius:17px; padding:22px 24px; margin:12px 0; background:rgba(255,251,248,.78); box-shadow:0 13px 35px rgba(110,75,65,.07); }.card h2,.card h3 { color:#423333; margin-top:0; letter-spacing:-.5px; }.card h3 { font-size:18px; }.card b { color:#594242; }
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:11px; margin:16px 0 22px; }.stat { position:relative; overflow:hidden; padding:16px 17px; border:1px solid rgba(116,80,76,.12); border-radius:15px; background:rgba(255,250,247,.68); box-shadow:0 8px 24px rgba(110,75,65,.04); transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }.stat:before { content:""; position:absolute; width:90px; height:90px; right:-34px; top:-38px; border-radius:50%; background:radial-gradient(circle,rgba(214,142,164,.30),transparent 68%); animation:metricGlow 2.8s ease-in-out infinite; }.stat:after { content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(115deg,transparent 28%,rgba(255,255,255,.56) 48%,transparent 68%); transform:translateX(-125%); animation:metricSweep 3.8s ease-in-out infinite; }.stat:hover { transform:translateY(-4px); border-color:rgba(193,116,142,.38); box-shadow:0 15px 32px rgba(169,94,119,.16); }.stat-value { position:relative; z-index:1; color:#634753; font-size:24px; font-weight:800; letter-spacing:-1px; animation:metricCount .75s cubic-bezier(.2,.8,.2,1) both; }.stat-label { position:relative; z-index:1; color:#9b8580; font-family:'DM Mono',monospace; font-size:8px; letter-spacing:.8px; margin-top:4px; text-transform:uppercase; }.stat-trend { position:relative; z-index:1; display:inline-flex; align-items:center; gap:4px; margin-top:10px; color:#936078; font-family:'DM Mono',monospace; font-size:8px; letter-spacing:.5px; text-transform:uppercase; }.stat-trend:before { content:""; width:5px; height:5px; border-radius:50%; background:#ca7893; box-shadow:0 0 0 4px rgba(202,120,147,.13),0 0 13px rgba(202,120,147,.75); animation:trendPulse 1.8s ease-in-out infinite; } @keyframes metricCount { from { opacity:0; transform:translateY(8px) scale(.82); filter:blur(3px); } to { opacity:1; transform:translateY(0) scale(1); filter:blur(0); } } @keyframes metricGlow { 0%,100% { opacity:.45; transform:scale(.9); } 50% { opacity:.9; transform:scale(1.16); } } @keyframes metricSweep { 0%,35% { transform:translateX(-125%); } 70%,100% { transform:translateX(125%); } } @keyframes trendPulse { 0%,100% { opacity:.58; transform:scale(.85); } 50% { opacity:1; transform:scale(1.2); } }
.source { display:block; padding:15px 17px; margin:9px 0; border-radius:13px; background:rgba(255,251,248,.78); border:1px solid rgba(116,80,76,.13); color:#986077!important; text-decoration:none!important; box-shadow:0 8px 24px rgba(110,75,65,.05); transition:.2s; }.source:hover { transform:translateY(-2px); border-color:rgba(196,115,139,.38); box-shadow:0 13px 30px rgba(169,94,119,.12); }
.activity { position:relative; overflow:hidden; padding:16px 18px 16px 21px; border-radius:13px; background:linear-gradient(105deg,rgba(255,251,248,.94),rgba(250,237,233,.78)); border:1px solid rgba(145,94,100,.16); margin:10px 0; box-shadow:0 8px 22px rgba(110,75,65,.07); animation:activityIn .55s cubic-bezier(.2,.8,.2,1) both; transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }
.activity:hover { transform:translateY(-3px) translateX(2px); border-color:rgba(193,116,142,.38); box-shadow:0 15px 30px rgba(169,94,119,.14); }
.activity:before { content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(110deg,transparent 20%,rgba(255,255,255,.44) 45%,transparent 70%); transform:translateX(-120%); animation:activityShimmer 2.4s ease-out .55s 1 both; }
.activity:after { content:""; position:absolute; left:7px; top:38px; bottom:-16px; width:1px; background:linear-gradient(#d795a5,transparent); opacity:.48; transform-origin:top; animation:connectorIn .55s ease-out .18s both; }.activity:last-child:after { display:none; }
.activity-row { position:relative; z-index:1; display:flex; align-items:center; gap:11px; color:#59403f; font-size:13px; transition:color .2s ease; }.activity:hover .activity-row { color:#7c4f63; }.activity .small { position:relative; z-index:1; }.stream-feed { margin:12px 0 4px; padding:4px 0; }.stream-event { animation:activityIn .35s cubic-bezier(.2,.8,.2,1) both; }.stream-event .event-icon { display:inline-flex; align-items:center; justify-content:center; width:19px; height:19px; border-radius:50%; background:rgba(193,116,142,.12); color:#a55d78; font-family:'DM Mono',monospace; font-size:9px; }.stream-event.live .event-icon { background:rgba(142,115,157,.15); color:#765984; box-shadow:0 0 0 5px rgba(142,115,157,.07); animation:dotBreath 1.8s ease-in-out infinite; }
.dot { width:8px; height:8px; border-radius:50%; background:#d18b9f; box-shadow:0 0 0 5px rgba(209,139,159,.13); flex:none; animation:dotBreath 2.2s ease-in-out infinite; }.dot.done { background:#8f739d; box-shadow:0 0 0 5px rgba(143,115,157,.12); animation:dotDone .7s ease-out both; }.spinner { width:14px; height:14px; border-radius:50%; border:2px solid rgba(190,127,145,.22); border-top-color:#b5657f; animation:spin .8s linear infinite,spinnerGlow 1.8s ease-in-out infinite; flex:none; }
@keyframes spin { to { transform:rotate(360deg); } } @keyframes activityIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } } @keyframes activityShimmer { to { transform:translateX(120%); } } @keyframes connectorIn { from { transform:scaleY(0); opacity:0; } to { transform:scaleY(1); opacity:.48; } } @keyframes dotBreath { 0%,100% { box-shadow:0 0 0 5px rgba(209,139,159,.13); } 50% { box-shadow:0 0 0 8px rgba(209,139,159,.03); } } @keyframes dotDone { from { transform:scale(.4); opacity:.2; } 70% { transform:scale(1.25); } to { transform:scale(1); opacity:1; } } @keyframes spinnerGlow { 50% { filter:drop-shadow(0 0 4px rgba(181,101,127,.45)); } }
div[data-testid="stTextInput"] input { border-radius:12px!important; border:1px solid rgba(112,77,73,.18)!important; background:rgba(255,252,249,.92)!important; color:#493635!important; -webkit-text-fill-color:#493635!important; padding:15px 16px!important; box-shadow:0 9px 24px rgba(110,75,65,.06)!important; } div[data-testid="stTextInput"] input::placeholder { color:#aa9791!important; -webkit-text-fill-color:#aa9791!important; opacity:1!important; }
button[kind="primary"] { border:0!important; border-radius:10px!important; background:linear-gradient(135deg,#9e637d,#71566f)!important; color:#fffaf7!important; font-weight:800!important; box-shadow:0 10px 23px rgba(126,79,105,.22)!important; padding:10px 20px!important; }
.stTabs { margin:18px 0 26px; padding:17px 17px 22px; border:1px solid rgba(71,49,55,.20); border-radius:22px; background:linear-gradient(145deg,rgba(66,48,57,.98),rgba(48,39,52,.98)); box-shadow:0 22px 50px rgba(77,49,61,.22),inset 0 1px 0 rgba(255,255,255,.08); }.stTabs [data-baseweb="tab-list"] { gap:5px; background:rgba(28,23,32,.55); padding:5px; border-radius:13px; border:1px solid rgba(255,236,236,.10); }.stTabs [data-baseweb="tab"],.stTabs [role="tab"] { border-radius:9px!important; color:#c9b6bd!important; background:transparent!important; font-weight:700!important; opacity:1!important; }.stTabs [data-baseweb="tab"] *,.stTabs [role="tab"] * { color:#c9b6bd!important; opacity:1!important; -webkit-text-fill-color:#c9b6bd!important; }.stTabs [aria-selected="true"],.stTabs [role="tab"][aria-selected="true"] { background:linear-gradient(135deg,rgba(236,157,177,.26),rgba(178,156,202,.22))!important; color:#fff7f6!important; box-shadow:inset 0 0 0 1px rgba(255,224,228,.18),0 5px 16px rgba(0,0,0,.18); }.stTabs [aria-selected="true"] *,.stTabs [role="tab"][aria-selected="true"] * { color:#fff7f6!important; -webkit-text-fill-color:#fff7f6!important; }.stTabs [data-baseweb="tab-highlight"] { background:#efa4b8!important; height:2px!important; border-radius:999px!important; }.stTabs .card { border-color:rgba(255,236,236,.13); background:linear-gradient(145deg,rgba(80,59,70,.92),rgba(55,45,58,.92)); box-shadow:0 14px 32px rgba(0,0,0,.18); }.stTabs .card h2,.stTabs .card h3,.stTabs .card b { color:#fff4f1!important; }.stTabs .card p,.stTabs .card li,.stTabs .card span,.stTabs .card strong,.stTabs .card label { color:#ead9dc!important; -webkit-text-fill-color:#ead9dc!important; }.stTabs .card .muted { color:#ddcbd0!important; -webkit-text-fill-color:#ddcbd0!important; }.stTabs .card .small { color:#f0c8d0!important; -webkit-text-fill-color:#f0c8d0!important; }.stTabs .small { color:#c6aeb7; }.stTabs .source { color:#f1afc2!important; background:rgba(72,52,65,.90); border-color:rgba(255,225,231,.15); box-shadow:0 10px 24px rgba(0,0,0,.16); }.stTabs .source:hover { border-color:rgba(242,169,189,.55); box-shadow:0 14px 30px rgba(241,157,183,.16); }.stTabs [data-testid="stCheckbox"] label { color:#f1dfe2!important; }.stTabs [data-testid="stProgressBar"] { background:rgba(255,235,237,.16)!important; }
[data-testid="stCheckbox"] label { color:#765d5a!important; } [data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#d693a5,#8a7092)!important; } [data-testid="stProgressBar"] { background:rgba(214,185,184,.34)!important; }
[data-testid="stStatusWidget"] { background:rgba(255,250,247,.98)!important; color:#4b3837!important; border:1px solid rgba(116,80,76,.16)!important; box-shadow:0 18px 45px rgba(110,75,65,.14)!important; }
div[data-testid="stChatInput"] { position:fixed!important; pointer-events:auto!important; bottom:22px!important; left:50%!important; transform:translateX(-50%); width:min(860px,calc(100% - 34px))!important; z-index:999!important; padding:0!important; background:transparent!important; } div[data-testid="stChatInput"] > div { border-radius:17px!important; background:rgba(255,251,248,.96)!important; backdrop-filter:blur(24px)!important; border:1px solid rgba(116,80,76,.18)!important; box-shadow:0 18px 55px rgba(110,75,65,.18)!important; } div[data-testid="stChatInput"] textarea { color:#493635!important; -webkit-text-fill-color:#493635!important; } div[data-testid="stChatInput"] textarea::placeholder { color:#aa9791!important; -webkit-text-fill-color:#aa9791!important; opacity:1!important; } div[data-testid="stChatInput"] button { background:linear-gradient(135deg,#9e637d,#71566f)!important; color:#fffaf7!important; border-radius:10px!important; }
[data-testid="stExpander"] { border:1px solid rgba(116,80,76,.14)!important; border-radius:15px!important; background:rgba(255,250,247,.54)!important; box-shadow:0 9px 25px rgba(110,75,65,.05)!important; } [data-testid="stExpander"] summary { color:#765d5a!important; font-weight:800!important; letter-spacing:.2px; } [data-testid="stExpander"] [data-testid="stMarkdownContainer"] p { color:#765d5a!important; } .progress-summary { padding:16px 19px; margin:9px 0; background:linear-gradient(110deg,rgba(85,62,75,.92),rgba(58,47,61,.92)); border-color:rgba(255,236,236,.13); box-shadow:0 10px 24px rgba(0,0,0,.15); }.progress-summary b { color:#fff4f1!important; }.progress-summary .small { color:#f0c8d0!important; }
[data-testid="stChatMessage"] { background:rgba(255,250,247,.90); border:1px solid rgba(116,80,76,.17); border-radius:14px; padding:7px 13px; margin:10px 0; box-shadow:0 8px 22px rgba(110,75,65,.07); } [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"], [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p, [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span { color:#513b3a!important; -webkit-text-fill-color:#513b3a!important; } [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] { background:#e98fa2!important; } [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] { background:#9b7a9c!important; }
@media (max-width:760px) { .block-container{padding:18px 16px 170px}.nav-copy{display:none}.hero{padding:38px 27px;min-height:0}.hero h1{letter-spacing:-2px!important}.stat-grid{grid-template-columns:repeat(2,1fr)} }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Secrets
# -----------------------------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")
TAVILY_API_KEY = st.secrets.get("TAVILY_API_KEY")
MODEL = st.secrets.get("GEMINI_MODEL", "gemini-3.5-flash-lite")
MAX_SEARCH_RESULTS = int(st.secrets.get("MAX_SEARCH_RESULTS", 6))

if not GEMINI_API_KEY or not TAVILY_API_KEY:
    st.error("Add GEMINI_API_KEY and TAVILY_API_KEY to Streamlit Secrets.")
    st.stop()

# -----------------------------
# Persistent learner profile
# -----------------------------
PROFILE_PATH = Path.cwd() / ".pathfinder_profile.json"
PROFILE_DEFAULTS = {
    "experience_level": "Intermediate",
    "weekly_hours": 5,
    "learning_style": "Project-first",
    "preferred_resources": ["YouTube", "Official documentation"],
    "target_role": "",
    "current_focus": "",
}

def load_profile():
    try:
        if PROFILE_PATH.exists():
            saved = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
            return {**PROFILE_DEFAULTS, **saved}
    except (OSError, ValueError, TypeError):
        pass
    return PROFILE_DEFAULTS.copy()

def save_profile(profile):
    try:
        PROFILE_PATH.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError:
        pass

# -----------------------------
# Session state
# -----------------------------
for key, value in {
    "plan": None,
    "goal": "",
    "messages": [],
    "progress": {},
    "profile": load_profile(),
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

tavily = TavilyClient(api_key=TAVILY_API_KEY)

# IMPORTANT: CrewAI's @tool decorator requires a docstring.
@tool("Web Research")
def web_search(query: str) -> str:
    """Search the live web for current, reliable information relevant to the user's goal."""
    result = tavily.search(
        query=query,
        search_depth="advanced",
        max_results=MAX_SEARCH_RESULTS,
        include_answer=False,
        include_raw_content=True,
    )
    items = []
    for item in result.get("results", []):
        items.append(
            f"TITLE: {item.get('title', 'Untitled')}\n"
            f"URL: {item.get('url', '')}\n"
            f"CONTENT: {(item.get('raw_content') or item.get('content') or '')[:6000]}"
        )
    return "\n\n--- SOURCE ---\n\n".join(items)


def make_agent(event_queue=None):
    llm = LLM(
        model=f"gemini/{MODEL}",
        api_key=GEMINI_API_KEY,
        temperature=0.2,
        use_native=False,
    )
    agent_kwargs = dict(
        role="Learning Path Architect",
        goal="Research a goal and turn it into a practical, progressive, evidence-backed plan.",
        backstory=(
            "You are an expert learning strategist and technical researcher. "
            "You research current information, prefer official and primary sources, "
            "never invent URLs, and turn vague goals into concrete milestones and practice."
        ),
        tools=[web_search],
        llm=llm,
        allow_delegation=False,
        verbose=False,
        max_iter=10,
    )
    if event_queue is not None:
        def step_callback(step_output):
            raw_step = (getattr(step_output, "raw", None) or getattr(step_output, "output", None) or getattr(step_output, "result", None) or str(step_output))
            message = re.sub(r"\s+", " ", str(raw_step)).strip()
            if message:
                event_queue.put(("agent", message[:260]))
        agent_kwargs["step_callback"] = step_callback
    try:
        return Agent(**agent_kwargs)
    except TypeError:
        if event_queue is not None:
            event_queue.put(("system", "Live step callbacks are unavailable in this CrewAI runtime."))
        agent_kwargs.pop("step_callback", None)
        return Agent(**agent_kwargs)


def run_agent(instruction: str, expected_output: str, event_queue=None) -> str:
    agent = make_agent(event_queue)
    task = Task(description=instruction, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return getattr(result, "raw", str(result))


def run_agent_live(instruction: str, expected_output: str) -> str:
    """Run CrewAI off the UI thread and stream step events over Streamlit's WebSocket."""
    events = queue.Queue()
    result = {"raw": None, "error": None}

    def worker():
        try:
            result["raw"] = run_agent(instruction, expected_output, events)
        except Exception as exc:
            result["error"] = exc
        finally:
            events.put(("complete", "Agent run finished"))

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    timeline = [("connected", "Live channel connected"), ("system", "Agent is preparing the next reasoning step")]
    feed = st.empty()

    def render():
        rows = []
        for kind, message in timeline[-8:]:
            icon = "↗" if kind == "connected" else ("•" if kind == "agent" else "✓")
            state = " live" if kind == "agent" else ""
            rows.append(f'<div class="activity stream-event{state}"><div class="activity-row"><span class="event-icon">{icon}</span><b>{escape(str(message))}</b></div><div class="small">LIVE AGENT EVENT</div></div>')
        feed.markdown('<div class="stream-feed">' + "".join(rows) + '</div>', unsafe_allow_html=True)

    render()
    while thread.is_alive() or not events.empty():
        try:
            kind, message = events.get(timeout=0.12)
            timeline.append((kind, message))
            render()
        except queue.Empty:
            pass
    thread.join(timeout=0.2)
    if result["error"] is not None:
        raise result["error"]
    return result["raw"]


def parse_json(raw: str):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    return json.loads(match.group(0) if match else cleaned)


def context_text():
    recent = st.session_state.messages[-24:]
    if not recent:
        return ""
    return (
        "CONVERSATION MEMORY / PREFERENCE SIGNALS:\n"
        "Use this history to maintain continuity. Treat explicit requests as reliable preferences "
        "and infer recurring preferences cautiously; never invent personal facts.\n\n"
        + "\n\n".join(
            f"{m['role'].upper()}: {m['content']}" for m in recent
        )
    )


def profile_context():
    return json.dumps(st.session_state.get("profile", PROFILE_DEFAULTS), ensure_ascii=False)

# -----------------------------
# Navigation
# -----------------------------
st.markdown(
    '<div class="nav"><div class="brand"><span class="brand-mark">✦</span>Pathfinder AI</div>'
    '<div class="nav-copy">Created for focused progress&nbsp;&nbsp; / &nbsp;&nbsp;AI learning studio</div></div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    '<div class="hero">'
    '<div class="eyebrow"><span>✦</span> LEARNING PATH STUDIO <span style="opacity:.45">//</span> RESEARCH-LED</div>'
    '<h1>Write your next <span class="gradient">chapter.</span></h1>'
    '<div class="subtitle">Turn an ambitious idea into a clear, research-backed path. Pathfinder brings the right context, resources, practice and momentum into one calm workspace.</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Create your path</div>', unsafe_allow_html=True)
goal = st.text_input(
    "Goal",
    value=st.session_state.goal,
    placeholder="e.g. I want to learn LangGraph from beginner to building production-style AI agents.",
    label_visibility="collapsed",
)

with st.expander("Learner profile / personalize every path", expanded=False):
    profile = st.session_state.profile
    profile_cols = st.columns([1, 1, 1])
    with profile_cols[0]:
        experience_level = st.selectbox(
            "Experience level",
            ["Beginner", "Intermediate", "Advanced"],
            index=["Beginner", "Intermediate", "Advanced"].index(profile.get("experience_level", "Intermediate")),
            key="profile_experience_level",
        )
        weekly_hours = st.number_input(
            "Hours available / week", min_value=1, max_value=60,
            value=int(profile.get("weekly_hours", 5)), step=1, key="profile_weekly_hours"
        )
    with profile_cols[1]:
        learning_style = st.selectbox(
            "Learning style",
            ["Project-first", "Video-first", "Theory-first", "Balanced"],
            index=["Project-first", "Video-first", "Theory-first", "Balanced"].index(profile.get("learning_style", "Project-first")),
            key="profile_learning_style",
        )
        preferred_resources = st.multiselect(
            "Preferred resources",
            ["YouTube", "Official documentation", "Interactive courses", "Books", "Articles"],
            default=[x for x in profile.get("preferred_resources", []) if x in ["YouTube", "Official documentation", "Interactive courses", "Books", "Articles"]],
            key="profile_preferred_resources",
        )
    with profile_cols[2]:
        target_role = st.text_input("Target role", value=profile.get("target_role", ""), placeholder="e.g. AI engineer", key="profile_target_role")
        current_focus = st.text_input("Current focus", value=profile.get("current_focus", ""), placeholder="e.g. Python + agents", key="profile_current_focus")
    if st.button("Save learner profile", key="save_learner_profile"):
        st.session_state.profile = {
            "experience_level": experience_level,
            "weekly_hours": weekly_hours,
            "learning_style": learning_style,
            "preferred_resources": preferred_resources,
            "target_role": target_role.strip(),
            "current_focus": current_focus.strip(),
        }
        save_profile(st.session_state.profile)
        st.success("Your learner profile is saved for future paths.")

if st.button("Build my path  →", type="primary", use_container_width=False) and goal.strip():
    st.session_state.goal = goal.strip()
    with st.status("Building your personalized path…", expanded=True) as status:
        st.markdown('<div class="activity"><div class="activity-row"><span class="dot done"></span><b>Understanding your goal</b></div><div class="small">Identifying prerequisites, scope and the destination.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="activity"><div class="activity-row"><span class="spinner"></span><b>Searching the web</b></div><div class="small">Finding current documentation, courses and high-quality resources.</div></div>', unsafe_allow_html=True)
        raw = run_agent_live(
            f"""
USER GOAL:
{goal.strip()}

PREVIOUS SESSION CONTEXT:
{context_text() or 'No previous conversation.'}

LEARNER PROFILE:
{profile_context()}

Use the Web Research tool before answering.
Return ONLY valid JSON with these keys:
title, summary, prerequisites, roadmap, resources, projects, first_7_days, sources.

Use the previous session context as continuity memory. Identify explicit and recurring preferences
about resource format, platform, pacing, depth, teaching style, and project style. If the user has
previously asked for YouTube videos, for example, prefer relevant YouTube resources again when they
fit the new goal. Carry preferences into related courses and recommendations, but do not force an
old preference when the user asks for something different.

roadmap: list of objects with phase,title,objective,topics,estimated_time,deliverable.
resources: list of title,type,url,why.
projects: list of title,difficulty,goal,skills,milestones.
first_7_days: list of day,task,outcome.
sources: list of title,url.

Every URL must come from your research results. Prefer official documentation and primary sources.
Make the plan progressive, realistic and practical rather than generic.
""",
            "Valid JSON matching the requested plan schema.",
        )
        st.markdown('<div class="activity"><div class="activity-row"><span class="spinner"></span><b>Designing your roadmap</b></div><div class="small">Turning the research into phases, practice and measurable outcomes.</div></div>', unsafe_allow_html=True)
        st.session_state.plan = parse_json(raw)
        st.session_state.progress = {}
        st.session_state.messages.append({"role": "user", "content": goal.strip()})
        st.session_state.messages.append({"role": "assistant", "content": "Created a research-backed path for this goal."})
        status.update(label="Your path is ready", state="complete", expanded=False)
    st.rerun()

# -----------------------------
# Plan display
# -----------------------------
if st.session_state.plan:
    plan = st.session_state.plan
    st.markdown(
        f'<div class="card"><div class="small">YOUR PERSONALIZED PATH / READY TO EXPLORE</div>'
        f'<h2>{escape(str(plan.get("title", "Your Path")))}</h2>'
        f'<p class="muted">{escape(str(plan.get("summary", "")))}</p></div>'
        f'<div class="stat-grid">'
        f'<div class="stat"><div class="stat-value">{len(plan.get("roadmap", []))}</div><div class="stat-label">Roadmap phases</div><div class="stat-trend">Live plan</div></div>'
        f'<div class="stat"><div class="stat-value">{len(plan.get("resources", []))}</div><div class="stat-label">Curated resources</div><div class="stat-trend">Fresh signals</div></div>'
        f'<div class="stat"><div class="stat-value">{len(plan.get("projects", []))}</div><div class="stat-label">Build projects</div><div class="stat-trend">In motion</div></div>'
        f'<div class="stat"><div class="stat-value">7</div><div class="stat-label">Day launch sequence</div><div class="stat-trend">Ready to start</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["🧭 Roadmap", "📚 Resources", "🛠 Projects", "📅 7 Days", "✅ Progress"])

    with tabs[0]:
        for phase in plan.get("roadmap", []):
            topics = " · ".join(str(x) for x in phase.get("topics", []))
            st.markdown(
                f'<div class="card"><h3>Phase {escape(str(phase.get("phase", "")))}: {escape(str(phase.get("title", "")))}</h3>'
                f'<p class="muted">{escape(str(phase.get("objective", "")))}</p>'
                f'<b>Topics</b><p>{escape(topics)}</p>'
                f'<div class="small">Time: {escape(str(phase.get("estimated_time", "")))} &nbsp;•&nbsp; Deliverable: {escape(str(phase.get("deliverable", "")))}</div></div>',
                unsafe_allow_html=True,
            )
            phase_key = f"phase_{phase.get('phase')}"
            st.session_state.progress[phase_key] = st.checkbox(
                "Mark this phase complete",
                value=st.session_state.progress.get(phase_key, False),
                key=f"roadmap_{phase_key}",
            )

    with tabs[1]:
        for resource in plan.get("resources", []):
            url = str(resource.get("url", ""))
            st.markdown(
                f'<a class="source" href="{escape(url)}" target="_blank">'
                f'<b>{escape(str(resource.get("title", "Resource")))}</b><br>'
                f'<span class="small">{escape(str(resource.get("type", "Resource")))} · {escape(str(resource.get("why", "")))}</span></a>',
                unsafe_allow_html=True,
            )

    with tabs[2]:
        for project in plan.get("projects", []):
            milestones = "".join(f"<li>{escape(str(x))}</li>" for x in project.get("milestones", []))
            skills = ", ".join(str(x) for x in project.get("skills", []))
            st.markdown(
                f'<div class="card"><h3>{escape(str(project.get("title", "Project")))}</h3>'
                f'<div class="small">{escape(str(project.get("difficulty", "")))}</div>'
                f'<p class="muted">{escape(str(project.get("goal", "")))}</p>'
                f'<b>Skills:</b> {escape(skills)}<p><b>Milestones</b></p><ul>{milestones}</ul></div>',
                unsafe_allow_html=True,
            )

    with tabs[3]:
        for day in plan.get("first_7_days", []):
            st.markdown(
                f'<div class="card"><b>Day {escape(str(day.get("day", "")))} — {escape(str(day.get("task", "")))}</b>'
                f'<p class="muted">{escape(str(day.get("outcome", "")))}</p></div>',
                unsafe_allow_html=True,
            )

    with tabs[4]:
        values = list(st.session_state.progress.values())
        completed = sum(values)
        total = len(plan.get("roadmap", []))
        ratio = completed / total if total else 0
        st.markdown(
            f'<div class="card"><div class="small">ROADMAP MOMENTUM</div>'
            f'<h3>{completed} of {total} phases complete</h3>'
            f'<p class="muted">Use the checkboxes inside each roadmap phase to keep your path current.</p></div>',
            unsafe_allow_html=True,
        )
        st.progress(ratio)
        for phase in plan.get("roadmap", []):
            key = f"phase_{phase.get('phase')}"
            state = "Complete" if st.session_state.progress.get(key, False) else "Up next"
            st.markdown(
                f'<div class="card progress-summary"><b>Phase {escape(str(phase.get("phase", "")))}: {escape(str(phase.get("title", "")))}</b>'
                f'<div class="small">{state} &nbsp;•&nbsp; {escape(str(phase.get("deliverable", "")))}</div></div>',
                unsafe_allow_html=True,
            )

    if plan.get("sources"):
        st.markdown('<div class="section-title">The research behind your path</div>', unsafe_allow_html=True)
        for source in plan.get("sources", []):
            st.markdown(
                f'<a class="source" href="{escape(str(source.get("url", "")))}" target="_blank">'
                f'↗ {escape(str(source.get("title", "Source")))}</a>',
                unsafe_allow_html=True,
            )

# -----------------------------
# Follow-up conversation
# -----------------------------
st.markdown('<div class="section-title">Keep writing with Pathfinder</div>', unsafe_allow_html=True)
for message in st.session_state.messages[-8:]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Ask about your roadmap, resources, projects, or progress…")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.status("Working on your request…", expanded=True) as status:
        st.markdown('<div class="activity"><div class="activity-row"><span class="dot done"></span><b>Reading your current path</b></div><div class="small">Connecting your question with previous context.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="activity"><div class="activity-row"><span class="spinner"></span><b>Searching the web</b></div><div class="small">Researching fresh information when your question needs it.</div></div>', unsafe_allow_html=True)
        raw = run_agent_live(
            f"""
CURRENT GOAL:
{st.session_state.goal}

CURRENT PLAN:
{json.dumps(st.session_state.plan, ensure_ascii=False)[:18000]}

LEARNER PROFILE:
{profile_context()}

CONVERSATION CONTEXT:
{context_text()}

LATEST USER MESSAGE:
{prompt}

Answer the latest message directly and practically.
Resolve references such as 'it', 'that', 'those', 'the previous phase', and 'the project'
using the current plan and conversation. If the user asks for current information or resources,
use Web Research and only provide URLs returned by that tool.

Use CONVERSATION CONTEXT as persistent preference memory. Preserve explicit and recurring choices
such as YouTube versus articles, preferred platforms, video-first learning, depth, pacing, tone,
and project format across related requests. For example, if the user previously requested Python
mastery YouTube videos, use that preference when recommending related Python courses or resources
unless the latest message overrides it. Distinguish explicit preferences from cautious inferences,
and never claim personal traits that the conversation does not support.
""",
            "A direct, useful answer to the user's latest message.",
        )
        st.session_state.messages.append({"role": "assistant", "content": raw})
        status.update(label="Done", state="complete", expanded=False)
    st.rerun()
