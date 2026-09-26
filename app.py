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
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

:root { --ink:#f5f7ff; --muted:#9aa7c3; --line:rgba(176,193,255,.14); --panel:rgba(17,24,49,.72); --cyan:#63e5ff; --violet:#9b8cff; --pink:#ff77b7; }
#MainMenu, header, footer, [data-testid="stDecoration"], [data-testid="stToolbar"], [data-testid="stStatusWidget"] { display:none !important; visibility:hidden !important; }
[data-testid="stHeader"], .stApp > footer, footer { display:none !important; height:0 !important; }
[data-testid="stAppViewContainer"] { padding-top:0 !important; }
section[data-testid="stBottomBlockContainer"], [data-testid="stBottomBlockContainer"], [data-testid="stBottomBlockContainer"] * { background:transparent !important; border-color:transparent !important; box-shadow:none !important; }
.stApp { min-height:100vh; color:var(--ink); background:radial-gradient(circle at 7% 8%,rgba(88,220,255,.13),transparent 25%),radial-gradient(circle at 92% 0%,rgba(137,99,255,.18),transparent 30%),radial-gradient(circle at 78% 78%,rgba(255,75,166,.08),transparent 28%),#080b18; font-family:'Manrope',sans-serif; }
.stApp:before { content:""; position:fixed; inset:0; pointer-events:none; opacity:.22; background-image:linear-gradient(rgba(255,255,255,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.025) 1px,transparent 1px); background-size:48px 48px; mask-image:linear-gradient(to bottom,black,transparent 88%); }
.block-container { max-width:1280px; padding:26px 34px 190px; }
.nav { position:sticky; top:14px; z-index:100; display:flex; align-items:center; justify-content:space-between; gap:18px; padding:13px 16px; margin-bottom:26px; border:1px solid var(--line); border-radius:20px; background:rgba(10,15,32,.78); backdrop-filter:blur(26px); box-shadow:0 18px 60px rgba(0,0,0,.28); }
.brand { display:flex; align-items:center; font-size:15px; font-weight:800; letter-spacing:.2px; color:#f8f9ff; }.brand-mark { display:inline-flex; align-items:center; justify-content:center; width:34px; height:34px; border-radius:11px; margin-right:10px; color:#07111e; background:linear-gradient(135deg,var(--cyan),var(--violet)); box-shadow:0 0 28px rgba(99,229,255,.28); }.nav-copy { color:#8390ad; font-size:11px; font-weight:700; letter-spacing:1.2px; text-transform:uppercase; }
.hero { position:relative; overflow:hidden; padding:62px 58px 58px; margin-bottom:24px; border:1px solid var(--line); border-radius:30px; background:linear-gradient(130deg,rgba(22,31,65,.90),rgba(16,19,44,.72)); box-shadow:0 30px 100px rgba(0,0,0,.24); }.hero:before { content:""; position:absolute; width:420px; height:420px; right:-160px; top:-210px; border-radius:50%; background:radial-gradient(circle,rgba(99,229,255,.26),rgba(155,140,255,.09) 40%,transparent 70%); }.hero:after { content:""; position:absolute; inset:auto 14% -110px auto; width:260px; height:180px; background:rgba(255,119,183,.12); filter:blur(70px); transform:rotate(-16deg); }.eyebrow { display:inline-flex; align-items:center; gap:8px; padding:8px 12px; border-radius:999px; background:rgba(99,229,255,.08); border:1px solid rgba(99,229,255,.22); color:var(--cyan); font-family:'DM Mono',monospace; font-size:10px; font-weight:500; letter-spacing:1.1px; }.hero h1 { position:relative; z-index:1; font-size:clamp(44px,6vw,78px)!important; line-height:.98!important; letter-spacing:-4px!important; margin:22px 0 16px!important; color:#fbfbff!important; }.gradient { background:linear-gradient(90deg,var(--cyan),#a795ff 62%,var(--pink)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }.subtitle { position:relative; z-index:1; max-width:800px; color:#9aa7c3; font-size:16px; line-height:1.75; }
.section-title { display:flex; align-items:center; gap:12px; margin:30px 0 12px; font-size:13px; font-weight:800; color:#dfe5fb; letter-spacing:1.1px; text-transform:uppercase; }.section-title:after { content:""; height:1px; flex:1; background:linear-gradient(90deg,var(--line),transparent); }.muted { color:var(--muted); line-height:1.7; }.small { color:#7d89a7; font-family:'DM Mono',monospace; font-size:10px; letter-spacing:.35px; }.card { border:1px solid var(--line); border-radius:22px; padding:24px; margin:12px 0; background:linear-gradient(145deg,rgba(24,31,63,.78),rgba(13,18,39,.70)); box-shadow:0 18px 55px rgba(0,0,0,.18); }.card h2,.card h3 { color:#f3f5ff; margin-top:0; letter-spacing:-.6px; }.card h3 { font-size:19px; }.card b { color:#dfe5fb; }
.stat-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:12px; margin:16px 0 22px; }.stat { padding:18px; border:1px solid var(--line); border-radius:18px; background:rgba(16,23,47,.72); }.stat-value { color:#fff; font-size:25px; font-weight:800; letter-spacing:-1px; }.stat-label { color:#7785a4; font-family:'DM Mono',monospace; font-size:9px; letter-spacing:1px; margin-top:4px; text-transform:uppercase; }
.source { display:block; padding:16px 18px; margin:9px 0; border-radius:16px; background:rgba(19,28,57,.72); border:1px solid var(--line); color:var(--cyan)!important; text-decoration:none!important; box-shadow:0 10px 30px rgba(0,0,0,.12); transition:.2s; }.source:hover { transform:translateY(-2px); border-color:rgba(99,229,255,.42); box-shadow:0 15px 38px rgba(36,177,217,.10); }.activity { padding:15px 18px; border-radius:16px; background:rgba(14,21,44,.8); border:1px solid var(--line); margin:9px 0; }.activity-row { display:flex; align-items:center; gap:12px; color:#dce4fa; font-size:13px; }.dot { width:8px; height:8px; border-radius:50%; background:var(--cyan); box-shadow:0 0 0 5px rgba(99,229,255,.10); flex:none; }.dot.done { background:#72e0ad; box-shadow:0 0 0 5px rgba(114,224,173,.10); }.spinner { width:14px; height:14px; border-radius:50%; border:2px solid rgba(99,229,255,.2); border-top-color:var(--cyan); animation:spin .8s linear infinite; flex:none; } @keyframes spin { to { transform:rotate(360deg); } }
div[data-testid="stTextInput"] input { border-radius:15px!important; border:1px solid rgba(143,164,226,.23)!important; background:rgba(12,18,39,.82)!important; color:#f5f7ff!important; -webkit-text-fill-color:#f5f7ff!important; padding:16px 17px!important; box-shadow:0 12px 35px rgba(0,0,0,.16)!important; } div[data-testid="stTextInput"] input::placeholder { color:#71809e!important; -webkit-text-fill-color:#71809e!important; opacity:1!important; }
button[kind="primary"] { border:0!important; border-radius:14px!important; background:linear-gradient(135deg,#39cfee,#756bff)!important; color:#07111e!important; font-weight:800!important; box-shadow:0 12px 30px rgba(83,128,255,.25)!important; padding:10px 20px!important; }
.stTabs [data-baseweb="tab-list"] { gap:6px; background:rgba(13,19,40,.8); padding:6px; border-radius:16px; border:1px solid var(--line); }.stTabs [data-baseweb="tab"],.stTabs [role="tab"] { border-radius:11px!important; color:#8794b1!important; background:transparent!important; font-weight:700!important; opacity:1!important; }.stTabs [data-baseweb="tab"] *,.stTabs [role="tab"] * { color:#8794b1!important; opacity:1!important; -webkit-text-fill-color:#8794b1!important; }.stTabs [aria-selected="true"],.stTabs [role="tab"][aria-selected="true"] { background:linear-gradient(135deg,rgba(99,229,255,.15),rgba(155,140,255,.14))!important; color:#f4f6ff!important; box-shadow:inset 0 0 0 1px rgba(99,229,255,.18); }.stTabs [aria-selected="true"] *,.stTabs [role="tab"][aria-selected="true"] * { color:#f4f6ff!important; -webkit-text-fill-color:#f4f6ff!important; }.stTabs [data-baseweb="tab-highlight"] { background:var(--cyan)!important; height:2px!important; border-radius:999px!important; }
[data-testid="stCheckbox"] label { color:#b7c2dc!important; } [data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,var(--cyan),var(--violet))!important; }
div[data-testid="stChatInput"] { position:fixed!important; bottom:22px!important; left:50%!important; transform:translateX(-50%); width:min(860px,calc(100% - 34px))!important; z-index:999!important; padding:0!important; background:transparent!important; } div[data-testid="stChatInput"] > div { border-radius:22px!important; background:rgba(14,21,44,.94)!important; backdrop-filter:blur(24px)!important; border:1px solid rgba(143,164,226,.25)!important; box-shadow:0 20px 70px rgba(0,0,0,.42)!important; } div[data-testid="stChatInput"] textarea { color:#f5f7ff!important; -webkit-text-fill-color:#f5f7ff!important; } div[data-testid="stChatInput"] textarea::placeholder { color:#71809e!important; -webkit-text-fill-color:#71809e!important; opacity:1!important; } div[data-testid="stChatInput"] button { background:linear-gradient(135deg,#39cfee,#756bff)!important; color:#07111e!important; border-radius:12px!important; }
[data-testid="stChatMessage"] { background:rgba(19,27,55,.58); border:1px solid var(--line); border-radius:17px; padding:5px 12px; } [data-testid="stStatusWidget"] { background:rgba(17,24,49,.95)!important; color:#fff!important; }
@media (max-width:760px) { .block-container{padding:18px 16px 170px}.nav-copy{display:none}.hero{padding:42px 28px}.hero h1{letter-spacing:-2.5px!important}.stat-grid{grid-template-columns:repeat(2,1fr)} }
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
    '<div class="nav-copy">Research&nbsp;&nbsp;•&nbsp;&nbsp;Roadmap&nbsp;&nbsp;•&nbsp;&nbsp;Practice&nbsp;&nbsp;•&nbsp;&nbsp;Progress</div></div>',
    unsafe_allow_html=True,
)

# -----------------------------
# Hero
# -----------------------------
st.markdown(
    '<div class="hero">'
    '<div class="eyebrow"><span>✦</span> MULTI-STEP PROBLEM SOLVER <span style="opacity:.45">//</span> INTELLIGENCE CONSOLE</div>'
    '<h1>Turn a goal into a <span class="gradient">path.</span></h1>'
    '<div class="subtitle">Give Pathfinder a goal. It researches the current landscape, discovers useful resources, builds a progressive roadmap, creates practical projects, and helps you track the work.</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">Define your destination</div>', unsafe_allow_html=True)
goal = st.text_input(
    "Goal",
    value=st.session_state.goal,
    placeholder="e.g. I want to learn LangGraph from beginner to building production-style AI agents.",
    label_visibility="collapsed",
)

if st.button("✦ Build My Path", type="primary", use_container_width=False) and goal.strip():
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
        f'<div class="card"><div class="small">ACTIVE MISSION / PERSONALIZED PATH</div>'
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
        st.markdown('<div class="section-title">Evidence layer / research sources</div>', unsafe_allow_html=True)
        for source in plan.get("sources", []):
            st.markdown(
                f'<a class="source" href="{escape(str(source.get("url", "")))}" target="_blank">'
                f'↗ {escape(str(source.get("title", "Source")))}</a>',
                unsafe_allow_html=True,
            )

# -----------------------------
# Follow-up conversation
# -----------------------------
st.markdown('<div class="section-title">Command Pathfinder</div>', unsafe_allow_html=True)
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
