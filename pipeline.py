from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str, status_callback=None) -> dict:
    """
    Run the full 4-step research pipeline.
    status_callback(step: int, message: str) is called at each stage so a UI can react.
    """
    state = {}

    def update(step, msg):
        if status_callback:
            status_callback(step, msg)

    
    update(1, "Search agent is scouring the web...")
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })
    state["search_results"] = search_result["messages"][-1].content
    update(1, "Search complete.")

  
    update(2, "Reader agent is scraping top resources...")
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URLs (you can use multiple for better research) and scrape them for deeper content.\n\n"
            f"Search Results:\n{state['search_results'][:800]}"
        )]
    })
    state["scraped_content"] = reader_result["messages"][-1].content
    update(2, "Scraping complete.")

   
    update(3, "Writer is drafting the report...")
    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined,
    })
    update(3, "Report drafted.")

    
    update(4, "Critic is reviewing the report...")
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    update(4, "Review complete.")

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    result = run_research_pipeline(topic)
    print("\n=== REPORT ===\n", result["report"])
    print("\n=== FEEDBACK ===\n", result["feedback"])