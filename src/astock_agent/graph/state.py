from typing import NotRequired, TypedDict

from astock_agent.schemas.financial import FinancialSummary
from astock_agent.schemas.stock import MarketSummary


class ResearchState(TypedDict):
    """Shared state passed between research graph nodes."""

    symbol: str
    start_date: str
    end_date: str

    market_summary: NotRequired[MarketSummary]
    financial_summary: NotRequired[FinancialSummary]

    market_report: NotRequired[str]
    financial_report: NotRequired[str]
    final_report: NotRequired[str]
