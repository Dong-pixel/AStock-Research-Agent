from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class FinancialSnapshot(BaseModel):
    """One company's financial metrics for one reporting period."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^\d{6}$")
    report_date: date
    notice_date: date | None = None
    update_date: date | None = None
    report_type: str

    revenue_yuan: float | None = None
    parent_net_profit_yuan: float | None = None
    weighted_roe_pct: float | None = None
    gross_margin_pct: float | None = None

    source: str = "AKShare / 东方财富"
    period_basis: str = "按报告期"
class FinancialSummary(BaseModel):
    """A deterministic summary comparing equivalent reporting periods."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^\d{6}$")

    latest_report_date: date
    latest_notice_date: date | None = None
    report_type: str
    comparable_report_date: date | None = None

    revenue_yuan: float | None = None
    revenue_yoy_pct: float | None = None

    parent_net_profit_yuan: float | None = None
    parent_net_profit_yoy_pct: float | None = None

    weighted_roe_pct: float | None = None
    weighted_roe_change_pct_points: float | None = None

    gross_margin_pct: float | None = None
    gross_margin_change_pct_points: float | None = None

    source: str = "AKShare / 东方财富"