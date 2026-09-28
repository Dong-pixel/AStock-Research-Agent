from datetime import date

import akshare as ak
import pandas as pd

from astock_agent.schemas.financial import FinancialSnapshot

REQUIRED_COLUMNS = {
    "REPORT_DATE",
    "REPORT_TYPE",
}


def to_exchange_symbol(symbol: str) -> str:
    """Convert a 6-digit A-share code to the Eastmoney symbol format."""

    symbol = symbol.strip()

    if len(symbol) != 6 or not symbol.isdigit():
        raise ValueError(
            f"Stock symbol must contain exactly 6 digits, received: {symbol}"
        )

    if symbol.startswith("6"):
        return f"{symbol}.SH"

    if symbol.startswith(("0", "3")):
        return f"{symbol}.SZ"

    if symbol.startswith(("4", "8", "9")):
        return f"{symbol}.BJ"

    raise ValueError(
        f"Unable to determine exchange for stock symbol: {symbol}"
    )


def optional_date(value: object) -> date | None:
    """Convert an optional date value to datetime.date."""

    if value is None or pd.isna(value):
        return None

    return pd.to_datetime(value).date()


def optional_float(value: object) -> float | None:
    """Convert an optional numeric value to float."""

    if value is None or pd.isna(value):
        return None

    return float(value)


def normalize_financial_data(
    symbol: str,
    data: pd.DataFrame,
) -> list[FinancialSnapshot]:
    """Convert an AKShare financial table into normalized snapshots."""

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)

    if missing_columns:
        raise ValueError(
            f"Financial data is missing required columns: {sorted(missing_columns)}"
        )

    snapshots: list[FinancialSnapshot] = []

    for row in data.to_dict(orient="records"):
        snapshot = FinancialSnapshot(
            symbol=symbol,
            report_date=pd.to_datetime(row["REPORT_DATE"]).date(),
            notice_date=optional_date(row.get("NOTICE_DATE")),
            update_date=optional_date(row.get("UPDATE_DATE")),
            report_type=str(row["REPORT_TYPE"]),
            revenue_yuan=optional_float(row.get("TOTALOPERATEREVE")),
            parent_net_profit_yuan=optional_float(
                row.get("PARENTNETPROFIT")
            ),
            weighted_roe_pct=optional_float(row.get("ROEJQ")),
            gross_margin_pct=optional_float(row.get("XSMLL")),
        )
        snapshots.append(snapshot)

    return sorted(
        snapshots,
        key=lambda snapshot: snapshot.report_date,
        reverse=True,
    )


def get_financial_snapshots(
    symbol: str,
    limit: int = 8,
) -> list[FinancialSnapshot]:
    """Fetch and normalize recent A-share financial indicators."""

    if limit <= 0:
        raise ValueError("limit must be greater than zero")

    exchange_symbol = to_exchange_symbol(symbol)

    try:
        data = ak.stock_financial_analysis_indicator_em(
            symbol=exchange_symbol,
            indicator="按报告期",
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch financial data for stock {symbol}"
        ) from exc

    if data.empty:
        raise RuntimeError(
            f"No financial data returned for stock {symbol}"
        )

    snapshots = normalize_financial_data(
        symbol=symbol.strip(),
        data=data,
    )

    return snapshots[:limit]