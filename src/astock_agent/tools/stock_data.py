from datetime import UTC, datetime

import akshare as ak
import pandas as pd

from astock_agent.schemas.stock import StockBar

VALID_ADJUSTMENTS = {"", "qfq", "hfq"}

REQUIRED_COLUMNS = {
    "日期",
    "开盘",
    "收盘",
    "最高",
    "最低",
    "成交量",
    "成交额",
}


def validate_date(value: str, field_name: str) -> None:
    """Validate that a date uses the YYYYMMDD format."""

    try:
        datetime.strptime(value, "%Y%m%d").replace(tzinfo=UTC)
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYYMMDD format, received: {value}") from exc


def optional_float(value: object) -> float | None:
    """Convert an optional numeric value to float."""

    if value is None or pd.isna(value):
        return None

    return float(value)


def normalize_stock_history(
    symbol: str,
    data: pd.DataFrame,
) -> list[StockBar]:
    """Convert an AKShare DataFrame into normalized StockBar objects."""

    missing_columns = REQUIRED_COLUMNS.difference(data.columns)

    if missing_columns:
        raise ValueError(f"Market data is missing required columns: {sorted(missing_columns)}")

    bars: list[StockBar] = []

    for row in data.to_dict(orient="records"):
        bar = StockBar(
            symbol=symbol,
            trade_date=pd.to_datetime(row["日期"]).date(),
            open_price=float(row["开盘"]),
            close_price=float(row["收盘"]),
            high_price=float(row["最高"]),
            low_price=float(row["最低"]),
            volume=float(row["成交量"]),
            turnover=float(row["成交额"]),
            amplitude_pct=optional_float(row.get("振幅")),
            change_pct=optional_float(row.get("涨跌幅")),
            change_amount=optional_float(row.get("涨跌额")),
            turnover_rate_pct=optional_float(row.get("换手率")),
        )
        bars.append(bar)

    return bars


def get_stock_history(
    symbol: str,
    start_date: str,
    end_date: str,
    adjust: str = "qfq",
) -> pd.DataFrame:
    """Fetch historical daily prices for a China A-share stock."""

    symbol = symbol.strip()

    if len(symbol) != 6 or not symbol.isdigit():
        raise ValueError(f"Stock symbol must contain exactly 6 digits, received: {symbol}")

    validate_date(start_date, "start_date")
    validate_date(end_date, "end_date")

    if start_date > end_date:
        raise ValueError("start_date must not be later than end_date")

    if adjust not in VALID_ADJUSTMENTS:
        raise ValueError("adjust must be one of: '', 'qfq', or 'hfq'")

    try:
        data = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust=adjust,
            timeout=15,
        )
    except Exception as exc:
        raise RuntimeError(
            f"Failed to fetch market data for stock {symbol} ({type(exc).__name__}: {exc})"
        ) from exc

    if data.empty:
        raise RuntimeError(f"No market data returned for stock {symbol}")

    return data


def get_stock_bars(
    symbol: str,
    start_date: str,
    end_date: str,
    adjust: str = "qfq",
) -> list[StockBar]:
    """Fetch and normalize historical A-share prices."""

    data = get_stock_history(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )

    return normalize_stock_history(
        symbol=symbol.strip(),
        data=data,
    )
