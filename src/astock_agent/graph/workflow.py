from langgraph.graph import END, START, StateGraph

from astock_agent.graph.nodes import (
    financial_analysis_node,
    market_analysis_node,
    synthesis_node,
)
from astock_agent.graph.state import ResearchState


def build_research_graph():
    """Build and compile the A-share research workflow."""

    workflow = StateGraph(ResearchState)

    workflow.add_node(
        "market_analysis",
        market_analysis_node,
    )
    workflow.add_node(
        "financial_analysis",
        financial_analysis_node,
    )
    workflow.add_node(
        "synthesis",
        synthesis_node,
    )

    workflow.add_edge(
        START,
        "market_analysis",
    )
    workflow.add_edge(
        START,
        "financial_analysis",
    )

    workflow.add_edge(
        ["market_analysis", "financial_analysis"],
        "synthesis",
    )

    workflow.add_edge(
        "synthesis",
        END,
    )

    return workflow.compile()


research_graph = build_research_graph()