from astock_agent.agents.financial_analyst import analyze_financials
from astock_agent.agents.market_analyst import analyze_market
from astock_agent.agents.research_synthesizer import synthesize_research
from astock_agent.graph.state import ResearchState
from astock_agent.tools.financial_summary import get_financial_summary
from astock_agent.tools.market_summary import get_market_summary


def market_analysis_node(state: ResearchState) -> dict[str, object]:
    """Fetch market data and generate the market analysis report."""

    summary = get_market_summary(
        symbol=state["symbol"],
        start_date=state["start_date"],
        end_date=state["end_date"],
    )

    report = analyze_market(summary)

    return {
        "market_summary": summary,
        "market_report": report,
    }


def financial_analysis_node(state: ResearchState) -> dict[str, object]:
    """Fetch financial data and generate the financial analysis report."""

    summary = get_financial_summary(
        symbol=state["symbol"],
    )

    report = analyze_financials(summary)

    return {
        "financial_summary": summary,
        "financial_report": report,
    }
def synthesis_node(state: ResearchState) -> dict[str, object]:
    """Combine market and financial reports into the final report."""

    market_summary = state.get("market_summary")
    financial_summary = state.get("financial_summary")
    market_report = state.get("market_report")
    financial_report = state.get("financial_report")

    if market_summary is None:
        raise ValueError("Market summary is missing")

    if financial_summary is None:
        raise ValueError("Financial summary is missing")

    if not market_report:
        raise ValueError("Market report is missing")

    if not financial_report:
        raise ValueError("Financial report is missing")

    final_report = synthesize_research(
        market_summary=market_summary,
        financial_summary=financial_summary,
        market_report=market_report,
        financial_report=financial_report,
    )

    return {
        "final_report": final_report,
    }