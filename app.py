import time

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import build_reader_agent, build_search_agent, critic_chain, writer_chain

st.set_page_config(
    page_title="Ember Research",
    page_icon="🟧",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEME = """
<style>
:root {
    --orange: #ff8a1f;
    --orange-light: #ffb56b;
    --white: #ffffff;
    --black: #070707;
    --glass: rgba(255, 255, 255, 0.055);
    --glass-line: rgba(255, 255, 255, 0.15);
}

.stApp {
    background:
        radial-gradient(900px 480px at 88% -8%, rgba(255, 138, 31, 0.20), transparent 62%),
        radial-gradient(700px 420px at -12% 108%, rgba(255, 138, 31, 0.12), transparent 62%),
        var(--black);
    color: var(--white);
    font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
}

header[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }

[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.66) !important;
    border-right: 1px solid var(--glass-line);
    backdrop-filter: blur(26px);
}

[data-testid="stSidebar"] * { color: var(--white) !important; }

::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #000; }
::-webkit-scrollbar-thumb { background: var(--orange); border-radius: 20px; }

.glass {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.085), rgba(255, 255, 255, 0.02));
    border: 1px solid var(--glass-line);
    border-radius: 24px;
    box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55), inset 0 1px 0 rgba(255, 255, 255, 0.09);
    backdrop-filter: blur(22px) saturate(140%);
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 34px 38px 30px;
    margin: 10px 0 26px;
}

.hero::after {
    content: "";
    position: absolute;
    top: -150px;
    right: -70px;
    width: 320px;
    height: 320px;
    background: radial-gradient(circle, rgba(255, 138, 31, 0.38), transparent 70%);
    pointer-events: none;
}

.eyebrow {
    color: var(--orange);
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.26em;
    text-transform: uppercase;
}

.hero h1 {
    margin: 10px 0 8px;
    font-size: clamp(2.2rem, 4.4vw, 3.7rem);
    line-height: 1.05;
    letter-spacing: -0.045em;
    font-weight: 800;
}

.hero h1 span { color: var(--orange); }

.lede {
    max-width: 620px;
    color: rgba(255, 255, 255, 0.68);
    font-size: 0.98rem;
    line-height: 1.6;
    margin: 0;
}

.flow {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px;
    margin-top: 26px;
}

.node {
    padding: 8px 14px;
    border-radius: 999px;
    border: 1px solid rgba(255, 138, 31, 0.42);
    background: rgba(255, 138, 31, 0.09);
    color: var(--white);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.09em;
}

.node b { color: var(--orange); }
.arrow { color: var(--orange); font-size: 0.9rem; padding: 0 2px; }

.card {
    padding: 26px 28px;
    height: 100%;
}

.card-kicker {
    color: var(--orange);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}

.card-title {
    color: var(--white);
    font-size: 1.35rem;
    font-weight: 750;
    margin: 8px 0 6px;
    letter-spacing: -0.02em;
}

.card-sub {
    color: rgba(255, 255, 255, 0.55);
    font-size: 0.85rem;
    margin: 0 0 20px;
    line-height: 1.5;
}

.agent-row {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 13px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.09);
}

.agent-index {
    color: var(--orange);
    font-size: 0.78rem;
    font-weight: 800;
    letter-spacing: 0.08em;
    min-width: 26px;
}

.agent-copy b { display: block; font-size: 0.92rem; }
.agent-copy small { color: rgba(255, 255, 255, 0.5); font-size: 0.76rem; }

.side-brand {
    padding: 18px 16px;
    margin-bottom: 18px;
    border-radius: 18px;
    border: 1px solid rgba(255, 138, 31, 0.35);
    background: rgba(255, 138, 31, 0.08);
}

.side-brand b {
    color: var(--white);
    font-size: 1.05rem;
    letter-spacing: 0.02em;
}

.side-brand span {
    display: block;
    margin-top: 4px;
    color: var(--orange);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.2em;
}

.side-label {
    color: var(--orange);
    font-size: 0.67rem;
    font-weight: 800;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin: 22px 0 10px;
}

.history-item {
    padding: 9px 11px;
    margin-bottom: 7px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.05);
    border-left: 2px solid var(--orange);
    color: rgba(255, 255, 255, 0.85);
    font-size: 0.8rem;
}

.empty-note {
    color: rgba(255, 255, 255, 0.42);
    font-size: 0.8rem;
    font-style: italic;
}

.stTextInput label { color: rgba(255, 255, 255, 0.82) !important; font-weight: 600; }

.stTextInput > div > div > input {
    background: rgba(0, 0, 0, 0.48) !important;
    color: var(--white) !important;
    border: 1px solid rgba(255, 138, 31, 0.42) !important;
    border-radius: 14px !important;
    padding: 14px 16px !important;
    font-size: 0.98rem !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba(255, 138, 31, 0.20) !important;
}

.stTextInput > div > div > input::placeholder { color: rgba(255, 255, 255, 0.32) !important; }

.stButton > button, .stFormSubmitButton > button {
    background: linear-gradient(120deg, var(--orange), var(--orange-light)) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.72rem 1.3rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 12px 26px rgba(255, 138, 31, 0.28) !important;
    transition: transform 0.18s ease, box-shadow 0.18s ease !important;
}

.stButton > button:hover, .stFormSubmitButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 16px 34px rgba(255, 138, 31, 0.4) !important;
}

button[kind="secondary"] {
    background: rgba(255, 255, 255, 0.05) !important;
    color: var(--white) !important;
    border: 1px solid var(--glass-line) !important;
    box-shadow: none !important;
}

.tracker { padding: 24px 26px; }

.tracker-head {
    display: flex;
    justify-content: space-between;
    color: var(--orange);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.2em;
    margin-bottom: 12px;
}

.step {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 0;
    border-top: 1px solid rgba(255, 255, 255, 0.09);
}

.step-badge {
    width: 34px;
    height: 34px;
    min-width: 34px;
    display: grid;
    place-items: center;
    border-radius: 11px;
    border: 1px solid rgba(255, 138, 31, 0.4);
    color: var(--orange);
    font-size: 0.8rem;
    font-weight: 800;
    background: rgba(255, 138, 31, 0.07);
}

.step.active .step-badge {
    background: var(--orange);
    color: #000;
    animation: glow 1.5s ease-in-out infinite;
}

.step.done .step-badge { background: rgba(255, 138, 31, 0.22); }

.step-copy { flex: 1; }
.step-copy b { display: block; font-size: 0.9rem; }
.step-copy small { color: rgba(255, 255, 255, 0.45); font-size: 0.74rem; }

.step-state {
    color: var(--orange);
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.step.pending .step-state { color: rgba(255, 255, 255, 0.3); }

@keyframes glow {
    0%, 100% { box-shadow: 0 0 0 0 rgba(255, 138, 31, 0.45); }
    50% { box-shadow: 0 0 0 8px rgba(255, 138, 31, 0); }
}

.section-head {
    margin: 30px 0 16px;
    display: flex;
    align-items: baseline;
    gap: 14px;
}

.section-head h2 {
    margin: 0;
    font-size: 1.6rem;
    letter-spacing: -0.03em;
}

.section-head span {
    color: var(--orange);
    font-size: 0.7rem;
    font-weight: 800;
    letter-spacing: 0.18em;
}

[data-testid="stMetric"] {
    background: var(--glass);
    border: 1px solid var(--glass-line);
    border-radius: 16px;
    padding: 14px 16px !important;
    backdrop-filter: blur(16px);
}

[data-testid="stMetricLabel"] { color: rgba(255, 255, 255, 0.55) !important; font-size: 0.74rem !important; }
[data-testid="stMetricValue"] { color: var(--white) !important; font-size: 1.25rem !important; }
[data-testid="stMetricValue"] span { color: var(--orange) !important; }

[data-testid="stTabs"] button {
    color: rgba(255, 255, 255, 0.55) !important;
    font-weight: 700 !important;
}

[data-testid="stTabs"] button[aria-selected="true"] { color: var(--orange) !important; }
[data-baseweb="tab-highlight"] { background: var(--orange) !important; }
[data-baseweb="tab-border"] { background: rgba(255, 255, 255, 0.12) !important; }

.panel {
    padding: 26px 30px;
    margin-top: 16px;
    min-height: 160px;
}

.panel h1, .panel h2, .panel h3, .panel h4 { color: var(--white); }
.panel p, .panel li { color: rgba(255, 255, 255, 0.78); line-height: 1.7; }
.panel a { color: var(--orange) !important; }
.panel strong { color: var(--white); }

[data-testid="stDownloadButton"] button {
    background: transparent !important;
    color: var(--orange) !important;
    border: 1px solid var(--orange) !important;
    box-shadow: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
}

.stAlert {
    background: rgba(255, 138, 31, 0.12) !important;
    border: 1px solid var(--orange) !important;
    color: var(--white) !important;
    border-radius: 14px !important;
}

.stAlert svg { color: var(--orange) !important; fill: var(--orange) !important; }
.stMarkdown a { color: var(--orange) !important; }
hr { border-color: rgba(255, 255, 255, 0.12) !important; }
</style>
"""

st.markdown(THEME, unsafe_allow_html=True)

PipelineFailure = Exception

STEPS = [
    ("01", "Search", "Locating reliable sources"),
    ("02", "Read", "Extracting the strongest material"),
    ("03", "Write", "Drafting the research report"),
    ("04", "Critique", "Reviewing quality and evidence"),
]

AGENTS = [
    ("01", "Search agent", "Finds the latest relevant sources"),
    ("02", "Reader agent", "Scrapes the most useful page"),
    ("03", "Writer", "Turns research into a clear report"),
    ("04", "Critic", "Scores and challenges the draft"),
]


def to_text(output) -> str:
    if isinstance(output, str):
        return output
    return getattr(output, "content", str(output))


def render_tracker(states, timings) -> str:
    rows = []
    for index, (number, title, description) in enumerate(STEPS):
        state = states[index]
        if state == "done":
            badge = "✓"
            status = f"done · {timings.get(title.lower(), 0):.1f}s"
        elif state == "active":
            badge = "◌"
            status = "running"
        else:
            badge = number
            status = "queued"
        rows.append(
            f'<div class="step {state}">'
            f'<div class="step-badge">{badge}</div>'
            f'<div class="step-copy"><b>{title}</b><small>{description}</small></div>'
            f'<div class="step-state">{status}</div>'
            f'</div>'
        )
    return (
        '<div class="glass tracker">'
        '<div class="tracker-head"><span>LIVE PIPELINE</span>'
        f'<span>{states.count("done")} / {len(STEPS)} COMPLETE</span></div>'
        + "".join(rows)
        + "</div>"
    )


def run_pipeline_with_progress(topic: str, placeholder) -> dict:
    state = {"topic": topic}
    timings = {}
    states = ["active", "pending", "pending", "pending"]

    def paint():
        placeholder.markdown(render_tracker(states, timings), unsafe_allow_html=True)

    paint()

    t0 = time.time()
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find latest, reliable and detailed information on {topic}")]
    })
    state["search_result"] = search_result["messages"][-1].content
    timings["search"] = time.time() - t0
    states[0] = "done"
    states[1] = "active"
    paint()

    t0 = time.time()
    reader_agent = build_reader_agent()
    reader_prompt = (
        f"Scrape the content from the {topic}\n"
        f"pick the most relevant source and scrape it for deep content\n"
        f"Search Results : \n{state['search_result'][:800]}"
    )
    reader_result = reader_agent.invoke({
        "messages": [("user", reader_prompt)]
    })
    state["reader_result"] = reader_result["messages"][-1].content
    timings["read"] = time.time() - t0
    states[1] = "done"
    states[2] = "active"
    paint()

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_result']} \n"
        f"Detailed Search RESULTS : \n {state['reader_result']} \n"
    )

    t0 = time.time()
    state["report"] = to_text(writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    }))
    timings["write"] = time.time() - t0
    states[2] = "done"
    states[3] = "active"
    paint()

    t0 = time.time()
    state["feedback"] = to_text(critic_chain.invoke({"report": state["report"]}))
    timings["critique"] = time.time() - t0
    states[3] = "done"
    paint()

    state["timings"] = timings
    return state


def panel(text: str):
    st.markdown('<div class="glass panel">', unsafe_allow_html=True)
    st.markdown(text)
    st.markdown("</div>", unsafe_allow_html=True)


if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []


st.markdown(
    """
    <div class="glass hero">
        <div class="eyebrow">Orchestrated intelligence</div>
        <h1>Research, <span>refined.</span></h1>
        <p class="lede">Four specialist agents turn one question into a sourced,
        written and critically reviewed report.</p>
        <div class="flow">
            <span class="node"><b>01</b> SEARCH</span><span class="arrow">⟶</span>
            <span class="node"><b>02</b> READ</span><span class="arrow">⟶</span>
            <span class="node"><b>03</b> WRITE</span><span class="arrow">⟶</span>
            <span class="node"><b>04</b> CRITIQUE</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown(
        '<div class="side-brand"><b>EMBER</b><span>RESEARCH SYSTEM</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="side-label">The crew</div>', unsafe_allow_html=True)
    for number, name, description in AGENTS:
        st.markdown(
            f'<div class="agent-row"><div class="agent-index">{number}</div>'
            f'<div class="agent-copy"><b>{name}</b><small>{description}</small></div></div>',
            unsafe_allow_html=True,
        )

    st.markdown('<div class="side-label">Recent topics</div>', unsafe_allow_html=True)
    if st.session_state.history:
        for past in reversed(st.session_state.history[-5:]):
            st.markdown(f'<div class="history-item">{past}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-note">No runs yet.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear results", type="secondary", use_container_width=True):
        st.session_state.result = None
        st.rerun()


input_col, crew_col = st.columns([3, 2], gap="large")

with input_col:
    st.markdown(
        """
        <div class="glass card">
            <div class="card-kicker">New assignment</div>
            <div class="card-title">What should we investigate?</div>
            <p class="card-sub">Give the agents a topic. They handle the searching,
            reading, drafting and review.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("research_form", clear_on_submit=False):
        topic = st.text_input(
            "Research topic",
            placeholder="e.g. Latest advances in continual learning for LLMs",
            label_visibility="visible",
        )
        submitted = st.form_submit_button("Run research ⟶", type="primary")

with crew_col:
    tracker_placeholder = st.empty()
    tracker_placeholder.markdown(
        render_tracker(["pending"] * len(STEPS), {}), unsafe_allow_html=True
    )

if submitted:
    if not topic.strip():
        st.warning("Enter a topic to start the pipeline.")
    else:
        try:
            result = run_pipeline_with_progress(topic.strip(), tracker_placeholder)
            st.session_state.result = result
            st.session_state.history.append(topic.strip())
        except PipelineFailure as exc:
            st.session_state.result = None
            st.error(f"The pipeline stopped: {exc}")

result = st.session_state.result

if result:
    st.markdown(
        f'<div class="section-head"><h2>{result["topic"]}</h2>'
        f'<span>FINAL BRIEF</span></div>',
        unsafe_allow_html=True,
    )

    total = sum(result["timings"].values())
    labels = [("Search", "search"), ("Read", "read"), ("Write", "write"), ("Critique", "critique")]
    cols = st.columns(len(labels) + 1)
    for col, (label, key) in zip(cols, labels):
        col.metric(label, f'{result["timings"].get(key, 0):.1f}s')
    cols[-1].metric("Total", f"{total:.1f}s")

    tab_report, tab_feedback, tab_search, tab_reader = st.tabs(
        ["Report", "Critic feedback", "Search results", "Scraped content"]
    )

    with tab_report:
        panel(result["report"])
        st.download_button(
            "Download report (.md)",
            data=result["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        panel(result["feedback"])

    with tab_search:
        panel(result["search_result"])

    with tab_reader:
        panel(result["reader_result"])
