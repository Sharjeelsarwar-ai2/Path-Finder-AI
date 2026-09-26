import json
import re
from html import escape

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
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:11px; margin:16px 0 22px; }.stat { padding:16px 17px; border:1px solid rgba(116,80,76,.12); border-radius:15px; background:rgba(255,250,247,.68); box-shadow:0 8px 24px rgba(110,75,65,.04); }.stat-value { color:#634753; font-size:24px; font-weight:800; letter-spacing:-1px; }.stat-label { color:#9b8580; font-family:'DM Mono',monospace; font-size:8px; letter-spacing:.8px; margin-top:4px; text-transform:uppercase; }
.source { display:block; padding:15px 17px; margin:9px 0; border-radius:13px; background:rgba(255,251,248,.78); border:1px solid rgba(116,80,76,.13); color:#986077!important; text-decoration:none!important; box-shadow:0 8px 24px rgba(110,75,65,.05); transition:.2s; }.source:hover { transform:translateY(-2px); border-color:rgba(196,115,139,.38); box-shadow:0 13px 30px rgba(169,94,119,.12); }
.activity { position:relative; overflow:hidden; padding:16px 18px 16px 21px; border-radius:13px; background:linear-gradient(105deg,rgba(255,251,248,.94),rgba(250,237,233,.78)); border:1px solid rgba(145,94,100,.16); margin:10px 0; box-shadow:0 8px 22px rgba(110,75,65,.07); animation:activityIn .55s cubic-bezier(.2,.8,.2,1) both; transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease; }
.activity:hover { transform:translateY(-3px) translateX(2px); border-color:rgba(193,116,142,.38); box-shadow:0 15px 30px rgba(169,94,119,.14); }
.activity:before { content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(110deg,transparent 20%,rgba(255,255,255,.44) 45%,transparent 70%); transform:translateX(-120%); animation:activityShimmer 2.4s ease-out .55s 1 both; }
.activity:after { content:""; position:absolute; left:7px; top:38px; bottom:-16px; width:1px; background:linear-gradient(#d795a5,transparent); opacity:.48; transform-origin:top; animation:connectorIn .55s ease-out .18s both; }.activity:last-child:after { display:none; }
.activity-row { position:relative; z-index:1; display:flex; align-items:center; gap:11px; color:#59403f; font-size:13px; transition:color .2s ease; }.activity:hover .activity-row { color:#7c4f63; }.activity .small { position:relative; z-index:1; }
.dot { width:8px; height:8px; border-radius:50%; background:#d18b9f; box-shadow:0 0 0 5px rgba(209,139,159,.13); flex:none; animation:dotBreath 2.2s ease-in-out infinite; }.dot.done { background:#8f739d; box-shadow:0 0 0 5px rgba(143,115,157,.12); animation:dotDone .7s ease-out both; }.spinner { width:14px; height:14px; border-radius:50%; border:2px solid rgba(190,127,145,.22); border-top-color:#b5657f; animation:spin .8s linear infinite,spinnerGlow 1.8s ease-in-out infinite; flex:none; }
@keyframes spin { to { transform:rotate(360deg); } } @keyframes activityIn { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } } @keyframes activityShimmer { to { transform:translateX(120%); } } @keyframes connectorIn { from { transform:scaleY(0); opacity:0; } to { transform:scaleY(1); opacity:.48; } } @keyframes dotBreath { 0%,100% { box-shadow:0 0 0 5px rgba(209,139,159,.13); } 50% { box-shadow:0 0 0 8px rgba(209,139,159,.03); } } @keyframes dotDone { from { transform:scale(.4); opacity:.2; } 70% { transform:scale(1.25); } to { transform:scale(1); opacity:1; } } @keyframes spinnerGlow { 50% { filter:drop-shadow(0 0 4px rgba(181,101,127,.45)); } }
div[data-testid="stTextInput"] input { border-radius:12px!important; border:1px solid rgba(112,77,73,.18)!important; background:rgba(255,252,249,.92)!important; color:#493635!important; -webkit-text-fill-color:#493635!important; padding:15px 16px!important; box-shadow:0 9px 24px rgba(110,75,65,.06)!important; } div[data-testid="stTextInput"] input::placeholder { color:#aa9791!important; -webkit-text-fill-color:#aa9791!important; opacity:1!important; }
button[kind="primary"] { border:0!important; border-radius:10px!important; background:linear-gradient(135deg,#9e637d,#71566f)!important; color:#fffaf7!important; font-weight:800!important; box-shadow:0 10px 23px rgba(126,79,105,.22)!important; padding:10px 20px!important; }
.stTabs [data-baseweb="tab-list"] { gap:5px; background:rgba(235,219,216,.68); padding:5px; border-radius:13px; border:1px solid rgba(116,80,76,.10); }.stTabs [data-baseweb="tab"],.stTabs [role="tab"] { border-radius:9px!important; color:#886f6b!important; background:transparent!important; font-weight:700!important; opacity:1!important; }.stTabs [data-baseweb="tab"] *,.stTabs [role="tab"] * { color:#886f6b!important; opacity:1!important; -webkit-text-fill-color:#886f6b!important; }.stTabs [aria-selected="true"],.stTabs [role="tab"][aria-selected="true"] { background:#fffaf7!important; color:#68475b!important; box-shadow:0 4px 13px rgba(107,74,72,.09); }.stTabs [aria-selected="true"] *,.stTabs [role="tab"][aria-selected="true"] * { color:#68475b!important; -webkit-text-fill-color:#68475b!important; }.stTabs [data-baseweb="tab-highlight"] { background:#c1748e!important; height:2px!important; border-radius:999px!important; }
[data-testid="stCheckbox"] label { color:#765d5a!important; } [data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#d693a5,#8a7092)!important; } [data-testid="stProgressBar"] { background:rgba(214,185,184,.34)!important; }
[data-testid="stStatusWidget"] { background:rgba(255,250,247,.98)!important; color:#4b3837!important; border:1px solid rgba(116,80,76,.16)!important; box-shadow:0 18px 45px rgba(110,75,65,.14)!important; }
div[data-testid="stChatInput"] { position:fixed!important; pointer-events:auto!important; bottom:22px!important; left:50%!important; transform:translateX(-50%); width:min(860px,calc(100% - 34px))!important; z-index:999!important; padding:0!important; background:transparent!important; } div[data-testid="stChatInput"] > div { border-radius:17px!important; background:rgba(255,251,248,.96)!important; backdrop-filter:blur(24px)!important; border:1px solid rgba(116,80,76,.18)!important; box-shadow:0 18px 55px rgba(110,75,65,.18)!important; } div[data-testid="stChatInput"] textarea { color:#493635!important; -webkit-text-fill-color:#493635!important; } div[data-testid="stChatInput"] textarea::placeholder { color:#aa9791!important; -webkit-text-fill-color:#aa9791!important; opacity:1!important; } div[data-testid="stChatInput"] button { background:linear-gradient(135deg,#9e637d,#71566f)!important; color:#fffaf7!important; border-radius:10px!important; }
[data-testid="stChatMessage"] { background:rgba(255,250,247,.68); border:1px solid rgba(116,80,76,.12); border-radius:14px; padding:5px 12px; }
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
# Session state
# -----------------------------
for key, value in {
    "plan": None,
    "goal": "",
    "messages": [],
    "progress": {},
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


def make_agent():
    llm = LLM(
        model=f"gemini/{MODEL}",
        api_key=GEMINI_API_KEY,
        temperature=0.2,
        use_native=False,
    )
    return Agent(
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


def run_agent(instruction: str, expected_output: str) -> str:
    agent = make_agent()
    task = Task(description=instruction, expected_output=expected_output, agent=agent)
    crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
    result = crew.kickoff()
    return getattr(result, "raw", str(result))


def parse_json(raw: str):
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.I)
    match = re.search(r"\{.*\}", cleaned, flags=re.S)
    return json.loads(match.group(0) if match else cleaned)


def context_text():
    return "\n\n".join(
        f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[-12:]
    )

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

if st.button("Build my path  →", type="primary", use_container_width=False) and goal.strip():
    st.session_state.goal = goal.strip()
    with st.status("Building your personalized path…", expanded=True) as status:
        st.markdown('<div class="activity"><div class="activity-row"><span class="dot done"></span><b>Understanding your goal</b></div><div class="small">Identifying prerequisites, scope and the destination.</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="activity"><div class="activity-row"><span class="spinner"></span><b>Searching the web</b></div><div class="small">Finding current documentation, courses and high-quality resources.</div></div>', unsafe_allow_html=True)
        raw = run_agent(
            f"""
USER GOAL:
{goal.strip()}

PREVIOUS SESSION CONTEXT:
{context_text() or 'No previous conversation.'}

Use the Web Research tool before answering.
Return ONLY valid JSON with these keys:
title, summary, prerequisites, roadmap, resources, projects, first_7_days, sources.

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
        f'<div class="stat"><div class="stat-value">{len(plan.get("roadmap", []))}</div><div class="stat-label">Roadmap phases</div></div>'
        f'<div class="stat"><div class="stat-value">{len(plan.get("resources", []))}</div><div class="stat-label">Curated resources</div></div>'
        f'<div class="stat"><div class="stat-value">{len(plan.get("projects", []))}</div><div class="stat-label">Build projects</div></div>'
        f'<div class="stat"><div class="stat-value">7</div><div class="stat-label">Day launch sequence</div></div>'
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
        for phase in plan.get("roadmap", []):
            key = f"phase_{phase.get('phase')}"
            st.session_state.progress[key] = st.checkbox(
                f"Phase {phase.get('phase')}: {phase.get('title')}",
                value=st.session_state.progress.get(key, False),
                key=f"cb_{key}",
            )
        values = list(st.session_state.progress.values())
        st.progress(sum(values) / len(values) if values else 0)

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
        raw = run_agent(
            f"""
CURRENT GOAL:
{st.session_state.goal}

CURRENT PLAN:
{json.dumps(st.session_state.plan, ensure_ascii=False)[:18000]}

CONVERSATION CONTEXT:
{context_text()}

LATEST USER MESSAGE:
{prompt}

Answer the latest message directly and practically.
Resolve references such as 'it', 'that', 'those', 'the previous phase', and 'the project'
using the current plan and conversation. If the user asks for current information or resources,
use Web Research and only provide URLs returned by that tool.
""",
            "A direct, useful answer to the user's latest message.",
        )
        st.session_state.messages.append({"role": "assistant", "content": raw})
        status.update(label="Done", state="complete", expanded=False)
    st.rerun()
