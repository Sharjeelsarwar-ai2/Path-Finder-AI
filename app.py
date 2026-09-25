import json
import re
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from tavily import TavilyClient

st.set_page_config(page_title="Pathfinder AI", page_icon="✦", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------
# Design system + UI
# -----------------------------
st.markdown("""
<style>
/* ---------- Design tokens ---------- */
:root {
    --bg: #f7f7f9;
    --surface: #ffffff;
    --surface-alt: #f2f3f7;
    --surface-glass: rgba(255,255,255,0.86);
    --border: rgba(15,23,42,0.08);
    --border-strong: rgba(15,23,42,0.14);
    --text: #16181f;
    --text-strong: #0b0d13;
    --muted: #5b6270;
    --muted-soft: #8a90a1;

    --accent: #5b56e0;
    --accent-strong: #4640c9;
    --accent-soft: #eeecfe;
    --accent-gradient: linear-gradient(135deg, #6a63f0, #5b56e0);
    --success: #17a769;

    --radius-xl: 26px;
    --radius-lg: 18px;
    --radius-md: 13px;
    --radius-sm: 9px;

    --shadow-sm: 0 6px 18px rgba(15,23,42,0.06);
    --shadow-md: 0 14px 36px rgba(15,23,42,0.08);
    --shadow-lg: 0 22px 60px rgba(15,23,42,0.12);

    --space-1: 8px;
    --space-2: 14px;
    --space-3: 20px;
    --space-4: 28px;
    --space-5: 40px;
}

/* ---------- Chrome removal ---------- */
#MainMenu,
header,
footer,
[data-testid="stDecoration"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stStatusWidget"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
}
[data-testid="stAppViewContainer"] { padding-top: 0 !important; }

section[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"],
[data-testid="stBottomBlockContainer"] *,
div[class*="stBottom"],
section[class*="stBottom"] {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}

/* ---------- Base ---------- */
.stApp {
    background: var(--bg);
    color: var(--text);
}
.block-container { max-width: 1120px; padding: 26px 28px 220px; }

/* ---------- Nav ---------- */
.nav {
    position: sticky; top: 14px; z-index: 100;
    display: flex; align-items: center; justify-content: space-between; gap: var(--space-3);
    padding: 13px 18px; margin-bottom: var(--space-4);
    border: 1px solid var(--border); border-radius: var(--radius-xl);
    background: var(--surface-glass); backdrop-filter: blur(20px);
    box-shadow: var(--shadow-sm);
}
.brand { font-size: 18px; font-weight: 800; letter-spacing: -0.3px; color: var(--text-strong); display: flex; align-items: center; }
.brand-mark {
    display: inline-flex; align-items: center; justify-content: center;
    width: 32px; height: 32px; border-radius: var(--radius-sm); margin-right: var(--space-1);
    color: white; background: var(--accent-gradient);
    box-shadow: 0 6px 16px rgba(91,86,224,0.28);
}
.nav-copy { color: var(--muted-soft); font-size: 13px; font-weight: 600; }

/* ---------- Hero ---------- */
.hero {
    position: relative; overflow: hidden;
    padding: 52px 48px 46px; margin-bottom: var(--space-4);
    border: 1px solid var(--border); border-radius: var(--radius-xl);
    background: var(--surface);
    box-shadow: var(--shadow-md);
}
.hero:after {
    content: ""; position: absolute; width: 220px; height: 220px; right: -80px; top: -80px;
    border-radius: 50%; background: radial-gradient(circle, rgba(91,86,224,0.10), transparent 70%);
}
.eyebrow {
    display: inline-block; padding: 7px 12px; border-radius: 999px;
    background: var(--accent-soft); border: 1px solid rgba(91,86,224,0.18); color: var(--accent-strong);
    font-size: 11.5px; font-weight: 800; letter-spacing: 0.6px;
}
h1 {
    font-size: clamp(34px, 5.2vw, 64px) !important;
    line-height: 1.04 !important; letter-spacing: -1.8px !important;
    margin: 20px 0 14px !important; color: var(--text-strong) !important;
}
.gradient {
    background: var(--accent-gradient);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.subtitle { max-width: 760px; color: var(--muted); font-size: 16.5px; line-height: 1.7; }

/* ---------- Cards ---------- */
.card {
    border: 1px solid var(--border); border-radius: var(--radius-lg);
    padding: var(--space-4); margin: 12px 0;
    background: var(--surface); box-shadow: var(--shadow-sm);
    transition: box-shadow .2s ease;
}
.card:hover { box-shadow: var(--shadow-md); }
.section-title { margin: var(--space-4) 0 var(--space-2); font-size: 21px; font-weight: 800; color: var(--text-strong); }
.muted { color: var(--muted); }
.small { color: var(--muted-soft); font-size: 12.5px; }

.source {
    display: block; padding: 14px 16px; margin: 8px 0; border-radius: var(--radius-md);
    background: var(--surface); border: 1px solid var(--border);
    color: var(--accent-strong) !important; text-decoration: none !important;
    box-shadow: var(--shadow-sm); transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.source:hover { transform: translateY(-1px); box-shadow: var(--shadow-md); border-color: rgba(91,86,224,0.25); }

/* ---------- Activity indicator: quiet, Claude-style ---------- */
.activity {
    padding: 10px 4px; margin: 2px 0;
    background: transparent; border: none; box-shadow: none;
}
.activity-row { display: flex; align-items: center; gap: 10px; color: var(--muted); font-size: 13.5px; font-weight: 500; }
.activity .small { margin-left: 18px; color: var(--muted-soft); }
.pulse-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--muted-soft); flex: none;
    animation: pulseDot 1.3s ease-in-out infinite;
}
.pulse-dot.done { background: var(--success); animation: none; opacity: 1; }
@keyframes pulseDot {
    0%, 100% { opacity: 0.35; transform: scale(0.8); }
    50% { opacity: 1; transform: scale(1); }
}

/* ---------- Inputs / buttons ---------- */
div[data-testid="stTextInput"] input {
    border-radius: var(--radius-md) !important;
    border: 1px solid var(--border-strong) !important;
    background: var(--surface) !important;
    color: var(--text-strong) !important;
    -webkit-text-fill-color: var(--text-strong) !important;
    padding: 14px 16px !important;
    box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stTextInput"] input::placeholder {
    color: var(--muted-soft) !important;
    -webkit-text-fill-color: var(--muted-soft) !important;
    opacity: 1 !important;
}
button[kind="primary"] {
    border: 0 !important; border-radius: var(--radius-sm) !important;
    background: var(--accent-gradient) !important; color: white !important;
    font-weight: 700 !important; box-shadow: 0 10px 24px rgba(91,86,224,0.24) !important;
    transition: transform .15s ease, box-shadow .15s ease !important;
}
button[kind="primary"]:hover { transform: translateY(-1px); box-shadow: 0 14px 30px rgba(91,86,224,0.30) !important; }

/* ---------- Tabs ---------- */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px; background: var(--surface-alt); padding: 5px;
    border-radius: var(--radius-md); border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"], .stTabs [role="tab"] {
    border-radius: var(--radius-sm) !important;
    color: var(--muted) !important; background: transparent !important;
    font-weight: 650 !important; opacity: 1 !important;
}
.stTabs [data-baseweb="tab"] *, .stTabs [role="tab"] * {
    color: var(--muted) !important; opacity: 1 !important; -webkit-text-fill-color: var(--muted) !important;
}
.stTabs [aria-selected="true"], .stTabs [role="tab"][aria-selected="true"] {
    background: var(--surface) !important; color: var(--accent-strong) !important; box-shadow: var(--shadow-sm);
}
.stTabs [aria-selected="true"] *, .stTabs [role="tab"][aria-selected="true"] * {
    color: var(--accent-strong) !important; -webkit-text-fill-color: var(--accent-strong) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background: var(--accent-gradient) !important; height: 2.5px !important; border-radius: 999px !important;
}

/* ---------- Chat messages: explicit contrast, fixes "masked" text ---------- */
[data-testid="stChatMessage"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-left: 3px solid var(--border-strong) !important;
    border-radius: var(--radius-md) !important;
    padding: 14px 16px !important;
    margin-bottom: 12px !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stChatMessage"] * {
    color: var(--text) !important;
    -webkit-text-fill-color: var(--text) !important;
}
[data-testid="stChatMessage"]:nth-of-type(odd) {
    border-left-color: var(--accent) !important;
    background: var(--accent-soft) !important;
}
[data-testid="stChatMessage"]:last-child { margin-bottom: 48px !important; }

/* ---------- Floating chat dock ---------- */
.dock-fade {
    position: fixed; left: 0; right: 0; bottom: 0; height: 130px;
    background: linear-gradient(to bottom, rgba(247,247,249,0), var(--bg) 65%);
    pointer-events: none; z-index: 998;
}
div[data-testid="stChatInput"] {
    position: fixed !important; bottom: 22px !important; left: 50% !important;
    transform: translateX(-50%);
    width: min(820px, calc(100% - 34px)) !important;
    z-index: 999 !important; padding: 0 !important; background: transparent !important;
}
div[data-testid="stChatInput"] > div {
    border-radius: var(--radius-xl) !important;
    background: rgba(255,255,255,0.98) !important; backdrop-filter: blur(20px) !important;
    border: 1px solid var(--border-strong) !important;
    box-shadow: var(--shadow-lg) !important;
}
div[data-testid="stChatInput"] textarea {
    color: var(--text-strong) !important; -webkit-text-fill-color: var(--text-strong) !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: var(--muted-soft) !important; -webkit-text-fill-color: var(--muted-soft) !important; opacity: 1 !important;
}
div[data-testid="stChatInput"] button {
    background: var(--accent-gradient) !important; color: #fff !important; border-radius: var(--radius-sm) !important;
}

/* ---------- Responsive ---------- */
@media (max-width: 760px) {
    .block-container { padding: 16px 14px 200px; }
    .hero { padding: 30px 22px 26px; border-radius: var(--radius-lg); }
    .nav { padding: 10px 14px; border-radius: var(--radius-lg); flex-wrap: wrap; }
    .nav-copy { display: none; }
    .subtitle { font-size: 15px; }
    div[data-testid="stChatInput"] { width: calc(100% - 20px) !important; bottom: 14px !important; }
}
</style>
<div class="dock-fade"></div>
""", unsafe_allow_html=True)

# Best-effort hide of Streamlit Community Cloud's own "Manage app" bar.
# Caveat: this only affects the signed-in owner's view (regular visitors
# generally never see this bar), reaches into the parent document via
# window.parent (not an official API), and can break on Streamlit Cloud
# frontend updates. It is not something app.py's own CSS can reach directly,
# since that bar is not part of this app's DOM.
components.html("""
<script>
function hideManageBar() {
  try {
    const doc = window.parent.document;
    doc.querySelectorAll('*').forEach(el => {
      if (el.children.length === 0 && el.textContent && el.textContent.trim() === 'Manage app') {
        let target = el;
        let hops = 0;
        while (target.parentElement && getComputedStyle(target).position !== 'fixed' && hops < 8) {
          target = target.parentElement;
          hops += 1;
        }
        target.style.setProperty('display', 'none', 'important');
      }
    });
  } catch (e) { /* cross-origin or DOM shape changed; fail silently */ }
}
hideManageBar();
try {
  new MutationObserver(hideManageBar).observe(window.parent.document.body, {childList: true, subtree: true});
} catch (e) {}
</script>
""", height=0)

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


def activity(label: str, sub: str, state: str = "pending"):
    """state: 'pending' (pulsing) or 'done' (solid)."""
    dot_class = "pulse-dot done" if state == "done" else "pulse-dot"
    st.markdown(
        f'<div class="activity"><div class="activity-row"><span class="{dot_class}"></span>'
        f'<b>{escape(label)}</b></div><div class="small">{escape(sub)}</div></div>',
        unsafe_allow_html=True,
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
        activity("Understanding your goal", "Identifying prerequisites, scope and the destination.", state="done")
        activity("Searching the web", "Finding current documentation, courses and high-quality resources.")
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
        activity("Designing your roadmap", "Turning the research into phases, practice and measurable outcomes.")
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
        activity("Reading your current path", "Connecting your question with previous context.", state="done")
        activity("Searching the web", "Researching fresh information when your question needs it.")
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
