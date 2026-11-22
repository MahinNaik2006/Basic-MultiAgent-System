from agent import build_search_agent, build_reader_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str) -> dict:
    state = {}

    search_agent = build_search_agent()
    reader_agent = build_reader_agent()

    search_result = search_agent.invoke({
        "messages": [("user", f"Find latest, reliable and detailed information on {topic}")]
    })
    state["search_result"] = search_result["messages"][-1].content

    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Pick the most relevant URL from the search results below on '{topic}' "
            f"and scrape it for deep content.\n"
            f"Search Results:\n{state['search_result'][:2000]}"
        )]
    })
    state["reader_result"] = reader_result["messages"][-1].content

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_result']}\n\n"
        f"DETAILED CONTENT:\n{state['reader_result']}\n"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    })

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    return state


if __name__ == "__main__":
    topic = input("Enter a research topic: ")
    result = run_research_pipeline(topic)
    print("\n=== REPORT ===\n", result["report"])
    print("\n=== FEEDBACK ===\n", result["feedback"])