import pandas as pd
import numpy as np
import yfinance as yf
import datetime

from typing import List, Optional

RELEVANT_INFO = [
    'city', 'country', 'industryKey', 'sectorKey', 'fullTimeEmployees', 'currency', 'tradeable', 'quoteType',
    'financialCurrency', 'region', 'fullExchangeName', 'exchange', 'exchangeTimezoneName', 'market', 'marketCap',
    'shortName', 'ebitda', 'totalDebt', 'debtToEquity', 'totalRevenue'
    ]

def calculate_averages(df, column):
    df = df.sort_values('Date', ascending=False)
    
    tickers = df.columns.to_list()  
    
    # Define the periods (in days) for which we want to calculate the averages
    periods = [1, 5, 63, 90, 126, 252, 504, 756, 1008, 1260]  
    
    if column == 'Volume':
        base = f"average{column}Last{{}}"
    else:
        base = f"average{column}PriceLast{{}}"  
    
    # Create column names based on periods (e.g., averageLastDayClosePrice, averageLastWeekVolume, etc.)
    columns = [
        'Ticker',
        base.format('Day'),
        base.format('Week'),
        base.format('Month'),
        base.format('Quarter'),
        base.format('HalfYear'),
        base.format('1Y'),
        base.format('2Y'),
        base.format('3Y'),
        base.format('4Y'),
        base.format('5Y')
    ]
    
    data_rows = []  
    
    for ticker in tickers:
        row = [ticker]        
        for period in periods:
            # Take the most recent 'period' number of rows (up to the current date)
            sliced = df[ticker].iloc[:period]  # Take the last 'period' rows for this ticker
            row.append(sliced.mean(skipna=True))  
        data_rows.append(row)
    
    aggregated_df = pd.DataFrame(data_rows, columns=columns)
    
    return aggregated_df


def gather_asset_info(df, asset_info):
    
    
    # Prepare column names for the additional information
    columns = ['Ticker'] + asset_info
    distinct_tickers = df['Ticker'].unique()
    rows = []
    
    for ticker in distinct_tickers:
        try:
            # Fetch the information for the ticker from Yahoo Finance
            info_dict = yf.Ticker(ticker).info
            
            # Extract the requested asset information, using None if the info is missing
            data_row = [ticker] + [info_dict.get(field, None) for field in asset_info]
            rows.append(data_row)
        except Exception as e:
            print(f"Warning: Could not retrieve info for {ticker}: {e}")
            continue
    
    # Create a DataFrame from the gathered rows
    df_additional_info = pd.DataFrame(rows, columns=columns)
    
    # Merge the additional information with the original DataFrame (on 'Ticker')
    enriched_df = pd.merge(df, df_additional_info, how='left', on= 'Ticker')
    
    return enriched_df

# some info that me and Marek thought it is a good idea to fetch form yfinance API


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




# class Portfolio:
#     def __init__(
#                  self, 
#                  tickers: List[str], 
#                  start_date: Optional[str] = None, 
#                  end_date: Optional[str] = None, 
#                  period: str = '1d'
#                 ):
        
#         if start_date and end_date:
#             self.start_date = start_date
#             self.end_date = end_date
#             self.use_period = False
#         else:
#             self.period = period
#             self.use_period = True

#         self.tickers = tickers
        
        

#         self.column_grouped_data = self.download_data(group_by= 'column')
#         self.ticker_grouped_data = self.download_data(group_by= 'Ticker')

        
#         self.daily_info = self.get_daily_info()

#         self.daily_returns = self.get_daily_returns()
#         self.historical_data = self.get_prices(column='Close')

#     def get_daily_returns(self):
#         return self.get_prices(column='Close').pct_change()
    
    
    
    # def download_data(self, group_by: str):
    #     if self.use_period:
    #             data = yf.download(self.tickers, group_by= group_by, period=self.period)
    #     else:
    #         data = yf.download(self.tickers, group_by= group_by, start=self.start_date, end=self.end_date)
    #     return data

    # def get_prices(self, column: Optional[str] = None):
    #     if column:
    #         data = self.column_grouped_data[column]
    #     else:
    #         data = self.column_grouped_data

    #     if isinstance(data, pd.Series):
    #         data = data.to_frame(name=self.tickers[0])
        
    #     # Reset index to ensure the 'Date' column is usable
    #     data = data.reset_index()

    #     data['Date'] = pd.to_datetime(data['Date'])
    #     data.set_index('Date', inplace=True)

    #     return data.sort_values('Date', ascending=False)
    
    # def get_daily_info(self):
    #     data = self.ticker_grouped_data

    #     # Handling multi-level columns in a harsh but elegant way
    #     data = data.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)

    #     # Calculate daily price change, daily return, range, and volatility ratio
    #     data['Change'] = data['Close'] - data['Open']
    #     data['Daily Return'] = np.where(data['Open'] != 0, (data['Close'] - data['Open']) / data['Open'], np.nan)
    #     data['Range'] = data['High'] - data['Low']
    #     data['Volatility Ratio'] = data['Range'] / data['Open']
    #     data['Upper Wick'] = data['High'] - np.maximum(data['Open'], data['Close'])
    #     data['Lower Wick'] = np.minimum(data['Open'], data['Close']) - data['Low']
    #     data['Candle type'] = np.where(data['Close'] > data['Open'], 1, 0)  # 1 means bullish, 0 means bearish

    #     # Merge with additional asset information
    #     # First, calculating averages, then adding info NOT DEPENDING ON DATE!
    #     data = pd.merge(data, calculate_averages(self.get_prices(), 'Close'), how='left', on='Ticker')
    #     data = pd.merge(data, calculate_averages(self.get_prices(), 'Volume'), how='left', on='Ticker')

    #     data = gather_asset_info(data, RELEVANT_INFO)
    #     return data


# ------------------------------ TESTS ----------------------------------------#

WIG20 = [
        "ALR.WA", "ALE.WA", "BDX.WA", "CCC.WA", "CDR.WA",
        "CPS.WA", "DNP.WA", "KTY.WA", "JSW.WA", "KGH.WA",
        "KRU.WA", "LPP.WA", "MBK.WA", "OPL.WA", "PEO.WA",
        "PGE.WA", "PKN.WA", "PKO.WA", "PZU.WA", "PCO.WA"
    ]


start = datetime.datetime(2022,11,15)
end = datetime.datetime(2025,4,4)
period = '3y'

wig20 = gather_data(WIG20, period='3y')
print(wig20.head(10))