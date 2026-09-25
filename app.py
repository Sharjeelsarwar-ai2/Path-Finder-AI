import json, re
import streamlit as st
from crewai import Agent, Crew, Process, Task, LLM
from crewai.tools import tool
from tavily import TavilyClient

st.set_page_config(page_title='Pathfinder AI', page_icon='✦', layout='wide')
st.markdown('''<style>#MainMenu,header,footer{visibility:hidden}.stApp{background:radial-gradient(circle at 10% 0%,#12304a,transparent 35%),radial-gradient(circle at 90% 0%,#28204e,transparent 35%),#07111f}.block-container{max-width:1180px;padding:28px 28px 120px}.dock{position:sticky;top:14px;z-index:20;padding:14px 20px;border:1px solid #ffffff20;border-radius:24px;background:#102038bb;backdrop-filter:blur(20px);margin-bottom:35px}.hero,.card{border:1px solid #ffffff14;border-radius:28px;background:#102039b8;padding:30px;box-shadow:0 20px 70px #0005}.hero{padding:48px}.ey{color:#86e6ff;font-weight:800;letter-spacing:1px}.grad{background:linear-gradient(90deg,#fff,#7de3ff,#a88cff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}.muted{color:#9db0c6}.source{display:block;padding:14px;margin:8px 0;border-radius:16px;background:#ffffff08;border:1px solid #ffffff12;color:#9de7ff!important;text-decoration:none}.activity{padding:15px 18px;border-radius:17px;background:#0b1728;border:1px solid #ffffff12;margin:10px 0}.stChatInput{bottom:18px!important}div[data-testid='stChatInput']>div{border-radius:22px!important;background:#101d30ee!important;backdrop-filter:blur(20px)!important;border:1px solid #ffffff18!important}</style>''', unsafe_allow_html=True)

GEMINI_API_KEY=st.secrets.get('GEMINI_API_KEY'); TAVILY_API_KEY=st.secrets.get('TAVILY_API_KEY')
MODEL=st.secrets.get('GEMINI_MODEL','gemini-3.5-flash-lite')
if not GEMINI_API_KEY or not TAVILY_API_KEY: st.error('Add GEMINI_API_KEY and TAVILY_API_KEY to Streamlit Secrets.'); st.stop()

for k,v in {'plan':None,'goal':'','messages':[],'progress':{}}.items():
    if k not in st.session_state: st.session_state[k]=v

tavily=TavilyClient(api_key=TAVILY_API_KEY)
@tool('Web Research')
def web_search(query:str)->str:
    r=tavily.search(query=query,search_depth='advanced',max_results=6,include_raw_content=True)
    return '\n\n---SOURCE---\n'.join([f"TITLE: {x.get('title')}\nURL: {x.get('url')}\nCONTENT: {(x.get('raw_content') or x.get('content') or '')[:5000]}" for x in r.get('results',[])])

def agent():
    llm=LLM(model=f'gemini/{MODEL}',api_key=GEMINI_API_KEY,temperature=.2,use_native=False)
    return Agent(role='Learning Path Architect',goal='Research a goal and turn it into a practical, progressive plan.',backstory='You are a technical learning strategist. Research current information, prefer official sources, never invent URLs, and make plans actionable.',tools=[web_search],llm=llm,allow_delegation=False,verbose=False,max_iter=10)

def ask(text,expected='Valid JSON'):
    a=agent(); t=Task(description=text,expected_output=expected,agent=a)
    r=Crew(agents=[a],tasks=[t],process=Process.sequential,verbose=False).kickoff()
    return getattr(r,'raw',str(r))

def parse(s):
    s=re.sub(r'^```json\s*|\s*```$','',s.strip(),flags=re.I); m=re.search(r'\{.*\}',s,re.S); return json.loads(m.group(0) if m else s)

def context(): return '\n'.join(f"{m['role']}: {m['content']}" for m in st.session_state.messages[-12:])

st.markdown("<div class='dock'><b>✦ <span style='color:#86e6ff'>Pathfinder</span> AI</b> &nbsp; Research → Roadmap → Practice → Progress</div>",unsafe_allow_html=True)
st.markdown("<div class='hero'><div class='ey'>✦ MULTI-STEP PROBLEM SOLVER</div><h1>Turn a goal into a <span class='grad'>path.</span></h1><p class='muted' style='font-size:18px'>Research the goal, discover resources, build a roadmap, create practice projects, and track progress.</p></div>",unsafe_allow_html=True)

goal=st.text_input('Goal',value=st.session_state.goal,placeholder='e.g. I want to learn LangGraph from beginner to production-style agents.',label_visibility='collapsed')
if st.button('✦ Build My Path',type='primary') and goal.strip():
    st.session_state.goal=goal.strip()
    with st.status('Building your path...',expanded=True) as s:
        st.write('Understanding your goal and prerequisites')
        st.write('Searching the web for current resources')
        raw=ask(f'''Goal: {goal}\nPrevious context:\n{context() or 'None'}\n\nUse Web Research. Return ONLY JSON with keys: title,summary,prerequisites,roadmap,resources,projects,first_7_days,sources. roadmap is a list of objects with phase,title,objective,topics,estimated_time,deliverable. resources contains title,type,url,why. projects contains title,difficulty,goal,skills,milestones. first_7_days contains day,task,outcome. sources contains title,url. Every URL must come from your research. Make the plan progressive and practical.''')
        st.session_state.plan=parse(raw); st.session_state.progress={}
        st.session_state.messages.append({'role':'user','content':goal.strip()})
        st.session_state.messages.append({'role':'assistant','content':'Created a research-backed path for this goal.'})
        s.update(label='Path ready',state='complete',expanded=False)
    st.rerun()

if st.session_state.plan:
    p=st.session_state.plan
    st.markdown(f"<div class='card'><small>CURRENT GOAL</small><h2>{p.get('title','Your Path')}</h2><p class='muted'>{p.get('summary','')}</p></div>",unsafe_allow_html=True)
    tabs=st.tabs(['🧭 Roadmap','📚 Resources','🛠 Projects','📅 7 Days','✅ Progress'])
    with tabs[0]:
        for x in p.get('roadmap',[]):
            st.markdown(f"<div class='card'><h3>Phase {x.get('phase')}: {x.get('title')}</h3><p class='muted'>{x.get('objective')}</p><b>Topics</b><p>{' · '.join(x.get('topics',[]))}</p><small>Time: {x.get('estimated_time')} · Deliverable: {x.get('deliverable')}</small></div>",unsafe_allow_html=True)
    with tabs[1]:
        for x in p.get('resources',[]): st.markdown(f"<a class='source' href='{x.get('url','')}' target='_blank'><b>{x.get('title')}</b><br><small>{x.get('type')} · {x.get('why')}</small></a>",unsafe_allow_html=True)
    with tabs[2]:
        for x in p.get('projects',[]): st.markdown(f"<div class='card'><h3>{x.get('title')}</h3><small>{x.get('difficulty')}</small><p class='muted'>{x.get('goal')}</p><b>Skills:</b> {', '.join(x.get('skills',[]))}<p><b>Milestones</b></p><ul>{''.join('<li>'+str(m)+'</li>' for m in x.get('milestones',[]))}</ul></div>",unsafe_allow_html=True)
    with tabs[3]:
        for x in p.get('first_7_days',[]): st.markdown(f"<div class='card'><b>Day {x.get('day')} — {x.get('task')}</b><p class='muted'>{x.get('outcome')}</p></div>",unsafe_allow_html=True)
    with tabs[4]:
        for x in p.get('roadmap',[]):
            key=f"phase_{x.get('phase')}"; st.session_state.progress[key]=st.checkbox(f"Phase {x.get('phase')}: {x.get('title')}",value=st.session_state.progress.get(key,False),key='cb_'+key)
        vals=list(st.session_state.progress.values()); st.progress(sum(vals)/len(vals) if vals else 0)
    st.markdown('### Research Sources')
    for x in p.get('sources',[]): st.markdown(f"<a class='source' href='{x.get('url','')}' target='_blank'>↗ {x.get('title')}</a>",unsafe_allow_html=True)

st.markdown('### Continue with Pathfinder')
for m in st.session_state.messages[-8:]:
    with st.chat_message(m['role']): st.write(m['content'])
prompt=st.chat_input('Ask about your roadmap, resources, projects, or progress…')
if prompt:
    st.session_state.messages.append({'role':'user','content':prompt})
    raw=ask(f'''Current goal: {st.session_state.goal}\nCurrent plan: {json.dumps(st.session_state.plan)[:16000]}\nConversation context:\n{context()}\nLatest user message: {prompt}\nAnswer directly. Resolve references like it, that, those, previous phase/project from the conversation. Use Web Research if current information or new URLs are requested.''',expected='A direct helpful answer')
    st.session_state.messages.append({'role':'assistant','content':raw}); st.rerun()
