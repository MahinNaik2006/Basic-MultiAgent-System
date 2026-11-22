import time
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import build_search_agent, build_reader_agent, writer_chain, critic_chain

# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Multi-Agent Research Assistant",
    page_icon="🔎",
    layout="wide",
)

st.title("🔎 Multi-Agent Research Assistant")
st.caption("Search Agent → Reader Agent → Writer → Critic")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "result" not in st.session_state:
    st.session_state.result = None
if "history" not in st.session_state:
    st.session_state.history = []


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def to_text(output) -> str:
    """Chain outputs may be a str or a message object; normalise to str."""
    if isinstance(output, str):
        return output
    return getattr(output, "content", str(output))


def run_pipeline_with_progress(topic: str) -> dict:
    """Same steps as pipeline.py, but with live progress in the UI."""
    state = {"topic": topic}
    timings = {}

    # 1. Search
    with st.status("🔍 Search agent is looking for sources...", expanded=False) as status:
        t0 = time.time()
        search_agent = build_search_agent()
        search_result = search_agent.invoke({
            "messages": [("user", f"Find latest, reliable and detailed information on {topic}")]
        })
        state["search_result"] = search_result["messages"][-1].content
        timings["Search"] = time.time() - t0
        status.update(label=f"✅ Search complete ({timings['Search']:.1f}s)", state="complete")

    # 2. Read / scrape
    with st.status("📖 Reader agent is scraping the best source...", expanded=False) as status:
        t0 = time.time()
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "messages": [("user",
                f"Scrape the content from the {topic}\n"
                f"pick the most relevant source and scrape it for deep content\n"
                f"Search Results : \n{state['search_result'][:800]}"
            )]
        })
        state["reader_result"] = reader_result["messages"][-1].content
        timings["Reader"] = time.time() - t0
        status.update(label=f"✅ Reading complete ({timings['Reader']:.1f}s)", state="complete")

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_result']} \n"
        f"Detailed Search RESULTS : \n {state['reader_result']} \n"
    )

    # 3. Write
    with st.status("✍️ Writer is drafting the report...", expanded=False) as status:
        t0 = time.time()
        state["report"] = to_text(writer_chain.invoke({
            "topic": topic,
            "research": research_combined,
        }))
        timings["Writer"] = time.time() - t0
        status.update(label=f"✅ Report drafted ({timings['Writer']:.1f}s)", state="complete")

    # 4. Critique
    with st.status("🧐 Critic is reviewing the report...", expanded=False) as status:
        t0 = time.time()
        state["feedback"] = to_text(critic_chain.invoke({"report": state["report"]}))
        timings["Critic"] = time.time() - t0
        status.update(label=f"✅ Review complete ({timings['Critic']:.1f}s)", state="complete")

    state["timings"] = timings
    return state


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("About")
    st.write(
        "Enter a topic and the pipeline will search the web, read the most "
        "relevant source, write a report, and have a critic review it."
    )

    st.divider()
    st.subheader("Recent topics")
    if st.session_state.history:
        for past in reversed(st.session_state.history[-5:]):
            st.markdown(f"- {past}")
    else:
        st.caption("Nothing yet.")

    st.divider()
    if st.button("🗑️ Clear results", use_container_width=True):
        st.session_state.result = None
        st.rerun()

# ---------------------------------------------------------------------------
# Input
# ---------------------------------------------------------------------------
with st.form("research_form", clear_on_submit=False):
    topic = st.text_input(
        "Research topic",
        placeholder="e.g. Latest advances in continual learning for LLMs",
    )
    submitted = st.form_submit_button("🚀 Run research", type="primary")

if submitted:
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        try:
            result = run_pipeline_with_progress(topic.strip())
            st.session_state.result = result
            st.session_state.history.append(topic.strip())
        except Exception as e:
            st.session_state.result = None
            st.error(f"Something went wrong while running the pipeline: {e}")

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------
result = st.session_state.result

if result:
    st.divider()
    st.subheader(f"Results: {result['topic']}")

    total = sum(result["timings"].values())
    cols = st.columns(len(result["timings"]) + 1)
    for col, (name, secs) in zip(cols, result["timings"].items()):
        col.metric(name, f"{secs:.1f}s")
    cols[-1].metric("Total", f"{total:.1f}s")

    tab_report, tab_feedback, tab_search, tab_reader = st.tabs(
        ["📄 Report", "🧐 Critic Feedback", "🔍 Search Results", "📖 Scraped Content"]
    )

    with tab_report:
        st.markdown(result["report"])
        st.download_button(
            "⬇️ Download report (.md)",
            data=result["report"],
            file_name="research_report.md",
            mime="text/markdown",
        )

    with tab_feedback:
        st.markdown(result["feedback"])

    with tab_search:
        st.markdown(result["search_result"])

    with tab_reader:
        st.markdown(result["reader_result"])