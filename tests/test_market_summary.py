from datetime import date

import pytest

from astock_agent.schemas.stock import StockBar
from astock_agent.tools.market_summary import build_market_summary


def create_bar(
    symbol: str,
    trade_date: date,
    close_price: float,
    high_price: float,
    low_price: float,
    volume: float,
    turnover: float,
) -> StockBar:
    return StockBar(
        symbol=symbol,
        trade_date=trade_date,
        open_price=close_price,
        close_price=close_price,
        high_price=high_price,
        low_price=low_price,
        volume=volume,
        turnover=turnover,
    )


def test_build_market_summary_calculates_metrics():
    bars = [
        create_bar(
            symbol="600519",
            trade_date=date(2026, 9, 18),
            close_price=110.0,
            high_price=112.0,
            low_price=100.0,
            volume=200.0,
            turnover=2000.0,
        ),
        create_bar(
            symbol="600519",
            trade_date=date(2026, 9, 17),
            close_price=100.0,
            high_price=105.0,
            low_price=95.0,
            volume=100.0,
            turnover=1000.0,
        ),
    ]

    summary = build_market_summary(bars)

    assert summary.symbol == "600519"
    assert summary.start_date == date(2026, 9, 17)
    assert summary.end_date == date(2026, 9, 18)
    assert summary.trading_days == 2
    assert summary.start_close == 100.0
    assert summary.end_close == 110.0
    assert summary.period_return_pct == 10.0
    assert summary.highest_price == 112.0
    assert summary.lowest_price == 95.0
    assert summary.average_volume == 150.0
    assert summary.average_turnover == 1500.0


def test_build_market_summary_rejects_empty_bars():
    with pytest.raises(
        ValueError,
        match="At least one stock bar",
    ):
        build_market_summary([])


def test_build_market_summary_rejects_mixed_symbols():
    bars = [
        create_bar(
            symbol="600519",
            trade_date=date(2026, 9, 17),
            close_price=100.0,
            high_price=105.0,
            low_price=95.0,
            volume=100.0,
            turnover=1000.0,
        ),
        create_bar(
            symbol="300750",
            trade_date=date(2026, 9, 18),
            close_price=110.0,
            high_price=112.0,
            low_price=100.0,
            volume=200.0,
            turnover=2000.0,
        ),
    ]

    with pytest.raises(
        ValueError,
        match="same symbol",
    ):
        build_market_summary(bars)
