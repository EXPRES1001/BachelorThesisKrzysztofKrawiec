import pandas as pd
import yfinance as yf
import os

from typing import List, Optional

PERIODS = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '3y', '5y']

GROUPS_OF_TICKERS = {
    'SP500': [],
    'WIG20': [],
    'FTSE100': []
}

def gather_data(tickers: List[str], 
                start_date: Optional[str] = None, 
                end_date: Optional[str] = None, 
                period: str = '1y'):
    if start_date and end_date:
        data = yf.download(tickers, group_by= "column", start= start_date, end= end_date)
    else:
        data = yf.download(tickers, group_by= "column", period= period)
    if isinstance(data, pd.Series):
        data = data.to_frame(name=tickers[0])      
    data = data['Close']
    data = data.reset_index()
    data['Date'] = pd.to_datetime(data['Date'])
    data.set_index('Date', inplace=True)

    return data.sort_values('Date', ascending=False)