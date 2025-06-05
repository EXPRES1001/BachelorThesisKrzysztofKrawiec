import pandas as pd
import yfinance as yf

from typing import List, Optional
from skfolio.datasets import load_ftse100_dataset, load_nasdaq_dataset, load_sp500_dataset



PERIODS = ['1d','5d','1mo','3mo','6mo','1y','2y','3y','5y']

ftse100_prices = load_ftse100_dataset()
sp500_prices = load_sp500_dataset()
nasdaq_prices = load_nasdaq_dataset()

PORTFOLIOS_TO_PRICES = {
    'SP500': sp500_prices,
    'FTSE100': ftse100_prices,
    'NASDAQ': nasdaq_prices
}


def gather_data(tickers: List[str],
                start_date: Optional[str]=None,
                end_date  : Optional[str]=None,
                period: str='1y') -> pd.DataFrame:
    tickers
    if start_date and end_date:
        data = yf.download(tickers, group_by="column",
                           start=start_date, end=end_date)
    else:
        data = yf.download(tickers, group_by="column", period=period)
    if data.empty:
        raise ValueError("yfinance returned empty Data Frame - "
                         "check tickers or date range.")

    if isinstance(data, pd.Series):
        data = data.to_frame(name=tickers[0])

    data = data.dropna()

    data = data["Close"].reset_index().rename(columns={"Date": "date"})
    data["date"] = pd.to_datetime(data["date"])
    return data.set_index("date").sort_index(ascending=False)