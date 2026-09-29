from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class StockBar(BaseModel):
    """A normalized daily price record for one A-share stock."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^\d{6}$")
    trade_date: date

    open_price: float
    close_price: float
    high_price: float
    low_price: float

    volume: float = Field(ge=0)
    turnover: float = Field(ge=0)

    amplitude_pct: float | None = None
    change_pct: float | None = None
    change_amount: float | None = None
    turnover_rate_pct: float | None = None


class MarketSummary(BaseModel):
    """A compact summary of historical market data."""

    model_config = ConfigDict(frozen=True)

    symbol: str = Field(pattern=r"^\d{6}$")
    start_date: date
    end_date: date
    trading_days: int = Field(gt=0)

    start_close: float
    end_close: float
    period_return_pct: float

    highest_price: float
    lowest_price: float

    average_volume: float = Field(ge=0)
    average_turnover: float = Field(ge=0)
