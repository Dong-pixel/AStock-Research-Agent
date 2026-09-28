from datetime import date

import pandas as pd
import pytest

from astock_agent.tools import stock_data


def test_get_stock_history_returns_data(monkeypatch):
    expected_data = pd.DataFrame(
        {
            "日期": ["2026-09-18"],
            "收盘": [1500.0],
        }
    )

    def fake_stock_zh_a_hist(**kwargs):
        assert kwargs["symbol"] == "600519"
        assert kwargs["period"] == "daily"
        assert kwargs["adjust"] == "qfq"
        return expected_data

    monkeypatch.setattr(
        stock_data.ak,
        "stock_zh_a_hist",
        fake_stock_zh_a_hist,
    )

    result = stock_data.get_stock_history(
        symbol="600519",
        start_date="20260901",
        end_date="20260918",
    )

    pd.testing.assert_frame_equal(result, expected_data)


def test_get_stock_history_reports_fetch_error(monkeypatch):
    def fail_fetch(**kwargs):
        raise ConnectionError("proxy connection failed")

    monkeypatch.setattr(stock_data.ak, "stock_zh_a_hist", fail_fetch)

    with pytest.raises(
        RuntimeError,
        match=r"ConnectionError: proxy connection failed",
    ):
        stock_data.get_stock_history(
            symbol="600519",
            start_date="20260901",
            end_date="20260918",
        )


@pytest.mark.parametrize(
    "invalid_symbol",
    [
        "",
        "AAPL",
        "60051",
        "600519.SS",
    ],
)
def test_get_stock_history_rejects_invalid_symbol(invalid_symbol):
    with pytest.raises(ValueError, match="exactly 6 digits"):
        stock_data.get_stock_history(
            symbol=invalid_symbol,
            start_date="20260901",
            end_date="20260918",
        )

def test_normalize_stock_history_returns_stock_bars():
    raw_data = pd.DataFrame(
        {
            "日期": ["2026-09-18"],
            "开盘": [1500.0],
            "收盘": [1510.0],
            "最高": [1520.0],
            "最低": [1490.0],
            "成交量": [10000],
            "成交额": [15000000],
            "振幅": [2.0],
            "涨跌幅": [1.35],
            "涨跌额": [20.0],
            "换手率": [0.5],
        }
    )

    bars = stock_data.normalize_stock_history(
        symbol="600519",
        data=raw_data,
    )

    assert len(bars) == 1

    bar = bars[0]

    assert bar.symbol == "600519"
    assert bar.trade_date == date(2026, 9, 18)
    assert bar.open_price == 1500.0
    assert bar.close_price == 1510.0
    assert bar.change_pct == 1.35


def test_normalize_stock_history_rejects_missing_columns():
    incomplete_data = pd.DataFrame(
        {
            "日期": ["2026-09-18"],
            "收盘": [1510.0],
        }
    )

    with pytest.raises(
        ValueError,
        match="missing required columns",
    ):
        stock_data.normalize_stock_history(
            symbol="600519",
            data=incomplete_data,
        )