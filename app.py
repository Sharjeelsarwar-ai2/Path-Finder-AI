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
#MainMenu, header, footer, [data-testid="stDecoration"] { visibility: hidden !important; }
.stApp {
    background:
      radial-gradient(circle at 8% 2%, rgba(75,190,255,.20), transparent 30%),
      radial-gradient(circle at 92% 4%, rgba(143,102,255,.18), transparent 30%),
      radial-gradient(circle at 50% 80%, rgba(50,210,180,.08), transparent 32%),
      #f5f9ff;
    color:#14243a;
}
.block-container { max-width:1180px; padding:26px 28px 150px; }
.nav {
    position:sticky; top:14px; z-index:100;
    display:flex; align-items:center; justify-content:space-between; gap:18px;
    padding:13px 18px; margin-bottom:30px;
    border:1px solid rgba(20,50,90,.10); border-radius:24px;
    background:rgba(255,255,255,.76); backdrop-filter:blur(22px);
    box-shadow:0 16px 50px rgba(32,65,105,.10);
}
.brand {font-size:19px; font-weight:850; letter-spacing:-.5px; color:#172942;}
.brand-mark { display:inline-flex; align-items:center; justify-content:center; width:34px; height:34px; border-radius:11px; margin-right:8px; color:white; background:linear-gradient(135deg,#27b9e8,#6d62ef); box-shadow:0 8px 20px rgba(68,139,236,.25); }
.nav-copy { color:#71839a; font-size:13px; font-weight:650; }
.hero {
    position:relative; overflow:hidden;
    padding:58px 54px 50px; margin-bottom:22px;
    border:1px solid rgba(25,75,120,.10); border-radius:34px;
    background:linear-gradient(135deg,rgba(255,255,255,.96),rgba(239,247,255,.88));
    box-shadow:0 28px 80px rgba(48,83,125,.13);
}
.hero:after { content:""; position:absolute; width:260px; height:260px; right:-90px; top:-90px; border-radius:50%; background:linear-gradient(135deg,rgba(52,199,238,.22),rgba(123,95,255,.18)); filter:blur(2px); }
.eyebrow { display:inline-block; padding:8px 13px; border-radius:999px; background:#e8f8ff; border:1px solid #bdeafa; color:#168bb5; font-size:12px; font-weight:850; letter-spacing:.8px; }
h1 { font-size:clamp(44px,6vw,76px)!important; line-height:.98!important; letter-spacing:-3.5px!important; margin:22px 0 16px!important; color:#10243d!important; }
.gradient { background:linear-gradient(90deg,#159fda,#5967e8,#8a5de8); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.subtitle { max-width:820px; color:#64788f; font-size:18px; line-height:1.7; }
.card { border:1px solid rgba(25,70,110,.10); border-radius:23px; padding:24px; margin:12px 0; background:rgba(255,255,255,.80); box-shadow:0 15px 42px rgba(39,75,115,.08); }
.section-title { margin:28px 0 12px; font-size:24px; font-weight:850; color:#152a43; }
.muted { color:#657991; }
.small { color:#73869b; font-size:13px; }
.source { display:block; padding:15px 17px; margin:9px 0; border-radius:17px; background:rgba(255,255,255,.84); border:1px solid rgba(28,86,135,.10); color:#167fa9!important; text-decoration:none!important; box-shadow:0 8px 25px rgba(35,82,124,.06); transition:.2s; }
.source:hover { transform:translateY(-1px); box-shadow:0 13px 32px rgba(35,82,124,.11); }
.activity { padding:15px 18px; border-radius:17px; background:rgba(255,255,255,.82); border:1px solid rgba(25,70,110,.10); margin:9px 0; box-shadow:0 9px 28px rgba(40,80,120,.06); }
.activity-row { display:flex; align-items:center; gap:12px; color:#526a83; font-size:14px; }
.dot { width:9px; height:9px; border-radius:50%; background:#20b8df; box-shadow:0 0 0 5px rgba(32,184,223,.10); flex:none; }
.dot.done { background:#37b879; box-shadow:0 0 0 5px rgba(55,184,121,.10); }
.spinner { width:14px; height:14px; border-radius:50%; border:2px solid #bfeaf5; border-top-color:#1aa9d5; animation:spin .8s linear infinite; flex:none; }
@keyframes spin { to { transform:rotate(360deg); } }
div[data-testid="stTextInput"] input { border-radius:17px!important; border:1px solid rgba(30,90,135,.13)!important; background:rgba(255,255,255,.90)!important; color:#172942!important; padding:15px 17px!important; box-shadow:0 10px 30px rgba(39,75,115,.06)!important; }
button[kind="primary"] { border:0!important; border-radius:15px!important; background:linear-gradient(135deg,#17a9da,#6465e8)!important; color:white!important; font-weight:800!important; box-shadow:0 12px 28px rgba(72,113,226,.22)!important; }
.stTabs [data-baseweb="tab-list"] { gap:8px; background:rgba(228,237,247,.70); padding:6px; border-radius:17px; }
.stTabs [data-baseweb="tab"] { border-radius:12px; color:#60758b; }
.stTabs [aria-selected="true"] { background:white!important; color:#1a6f9b!important; box-shadow:0 5px 15px rgba(30,70,110,.08); }
div[data-testid="stChatInput"] { position:fixed!important; bottom:20px!important; left:50%!important; transform:translateX(-50%); width:min(860px,calc(100% - 34px))!important; z-index:999; }
div[data-testid="stChatInput"] > div { border-radius:22px!important; background:rgba(255,255,255,.90)!important; backdrop-filter:blur(24px)!important; border:1px solid rgba(25,70,110,.13)!important; box-shadow:0 18px 60px rgba(28,65,105,.18)!important; }
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
    '<div class="eyebrow">✦ MULTI-STEP PROBLEM SOLVER</div>'
    '<h1>Turn a goal into a <span class="gradient">path.</span></h1>'
    '<div class="subtitle">Give Pathfinder a goal. It researches the current landscape, discovers useful resources, builds a progressive roadmap, creates practical projects, and helps you track the work.</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="section-title">What do you want to accomplish?</div>', unsafe_allow_html=True)
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
        f'<div class="card"><div class="small">CURRENT GOAL</div>'
        f'<h2>{escape(str(plan.get("title", "Your Path")))}</h2>'
        f'<p class="muted">{escape(str(plan.get("summary", "")))}</p></div>',
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
        st.markdown('<div class="section-title">Research Sources</div>', unsafe_allow_html=True)
        for source in plan.get("sources", []):
            st.markdown(
                f'<a class="source" href="{escape(str(source.get("url", "")))}" target="_blank">'
                f'↗ {escape(str(source.get("title", "Source")))}</a>',
                unsafe_allow_html=True,
            )

# -----------------------------
# Follow-up conversation
# -----------------------------
st.markdown('<div class="section-title">Continue with Pathfinder</div>', unsafe_allow_html=True)
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
