from datetime import date

from astock_agent.schemas.financial import (
    FinancialSnapshot,
    FinancialSummary,
)
from astock_agent.tools.financial_data import get_financial_snapshots


def calculate_growth_pct(
    current: float | None,
    previous: float | None,
) -> float | None:
    """Calculate growth relative to the comparable period."""

    if current is None or previous is None or previous == 0:
        return None

    return (current - previous) / abs(previous) * 100


def calculate_change_points(
    current: float | None,
    previous: float | None,
) -> float | None:
    """Calculate the change between two percentage values."""

    if current is None or previous is None:
        return None

    return current - previous


def find_comparable_snapshot(
    latest: FinancialSnapshot,
    snapshots: list[FinancialSnapshot],
) -> FinancialSnapshot | None:
    """Find the same reporting period from the previous year."""

    previous_year = latest.report_date.year - 1

    for snapshot in snapshots:
        same_year = snapshot.report_date.year == previous_year
        same_month = snapshot.report_date.month == latest.report_date.month
        same_day = snapshot.report_date.day == latest.report_date.day

        if same_year and same_month and same_day:
            return snapshot

    return None


def build_financial_summary(
    snapshots: list[FinancialSnapshot],
) -> FinancialSummary:
    """Build a financial summary from normalized snapshots."""

    if not snapshots:
        raise ValueError("Financial snapshots cannot be empty")

    symbols = {snapshot.symbol for snapshot in snapshots}

    if len(symbols) != 1:
        raise ValueError("All financial snapshots must use the same symbol")

    ordered_snapshots = sorted(
        snapshots,
        key=lambda snapshot: snapshot.report_date,
        reverse=True,
    )

    latest = ordered_snapshots[0]
    comparable = find_comparable_snapshot(
        latest=latest,
        snapshots=ordered_snapshots[1:],
    )

    return FinancialSummary(
        symbol=latest.symbol,
        latest_report_date=latest.report_date,
        latest_notice_date=latest.notice_date,
        report_type=latest.report_type,
        comparable_report_date=(comparable.report_date if comparable is not None else None),
        revenue_yuan=latest.revenue_yuan,
        revenue_yoy_pct=(
            calculate_growth_pct(
                latest.revenue_yuan,
                comparable.revenue_yuan,
            )
            if comparable is not None
            else None
        ),
        parent_net_profit_yuan=latest.parent_net_profit_yuan,
        parent_net_profit_yoy_pct=(
            calculate_growth_pct(
                latest.parent_net_profit_yuan,
                comparable.parent_net_profit_yuan,
            )
            if comparable is not None
            else None
        ),
        weighted_roe_pct=latest.weighted_roe_pct,
        weighted_roe_change_pct_points=(
            calculate_change_points(
                latest.weighted_roe_pct,
                comparable.weighted_roe_pct,
            )
            if comparable is not None
            else None
        ),
        gross_margin_pct=latest.gross_margin_pct,
        gross_margin_change_pct_points=(
            calculate_change_points(
                latest.gross_margin_pct,
                comparable.gross_margin_pct,
            )
            if comparable is not None
            else None
        ),
        source=latest.source,
    )


def get_financial_summary(
    symbol: str,
    as_of_date: date | None = None,
) -> FinancialSummary:
    """Build a summary using reports available by the research date."""

    snapshots = get_financial_snapshots(
        symbol=symbol,
        limit=12,
        as_of_date=as_of_date,
    )

    return build_financial_summary(snapshots)
