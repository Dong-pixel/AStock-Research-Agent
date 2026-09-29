from statistics import fmean

from astock_agent.schemas.stock import MarketSummary, StockBar
from astock_agent.tools.stock_data import get_stock_bars


def build_market_summary(
    bars: list[StockBar],
) -> MarketSummary:
    """Build a compact market summary from normalized stock bars."""

    if not bars:
        raise ValueError("At least one stock bar is required")
    symbols = {bar.symbol for bar in bars}

    if len(symbols) != 1:
        raise ValueError("All stock bars must belong to the same symbol")

    ordered_bars = sorted(
        bars,
        key=lambda bar: bar.trade_date,
    )

    first_bar = ordered_bars[0]
    last_bar = ordered_bars[-1]

    if first_bar.close_price == 0:
        raise ValueError("The first closing price must not be zero")

    period_return_pct = (last_bar.close_price / first_bar.close_price - 1) * 100

    return MarketSummary(
        symbol=first_bar.symbol,
        start_date=first_bar.trade_date,
        end_date=last_bar.trade_date,
        trading_days=len(ordered_bars),
        start_close=first_bar.close_price,
        end_close=last_bar.close_price,
        period_return_pct=round(period_return_pct, 4),
        highest_price=max(bar.high_price for bar in ordered_bars),
        lowest_price=min(bar.low_price for bar in ordered_bars),
        average_volume=round(
            fmean(bar.volume for bar in ordered_bars),
            2,
        ),
        average_turnover=round(
            fmean(bar.turnover for bar in ordered_bars),
            2,
        ),
    )


def get_market_summary(
    symbol: str,
    start_date: str,
    end_date: str,
    adjust: str = "qfq",
) -> MarketSummary:
    """Fetch stock bars and return a normalized market summary."""

    bars = get_stock_bars(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        adjust=adjust,
    )

    return build_market_summary(bars)
