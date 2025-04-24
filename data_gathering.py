import pandas as pd
import numpy as np
import yfinance as yf
import datetime

from typing import List, Optional

def calculate_averages(df, column):
    """
    Calculates averages of a user-specified column (e.g., 'Open', 'Close', 'Volume') for different time periods
    (from 1 day to 5 years) measured in number of days for each ticker in the DataFrame, where the tickers are the column names.

    This function assumes the DataFrame has a 'Date' column and that the tickers are the column names. Data frame is assumed to be
    multi-leveled as an output from yfinance functions.
    It calculates the average for various time periods for each ticker and returns the result as a new DataFrame.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame that contains a 'Date' column and the column for which averages are calculated (e.g., 'Close', 'Volume').
        The tickers are the column names. Columns have to be multi-level indexe, it means column argument is the highest and tickers
        are one level below.
        
    column : str
        The name of the column for which averages will be calculated (e.g., 'Close', 'Volume'). They are related to prices.

    Returns:
    --------
    pandas.DataFrame
        A new DataFrame with calculated averages for each ticker and time period.
        Columns will include the ticker and the averages for periods such as 'Day', 'Week', 'Month', etc.

    """
    # Ensure the DataFrame is sorted by descending 'Date' to calculate averages correctly
    df = df.sort_values('Date', ascending=False)
    
    # Get the list of tickers (column names)
    tickers = df.columns.to_list()  
    
    # Define the periods (in days) for which we want to calculate the averages
    periods = [1, 5, 63, 90, 126, 252, 504, 756, 1008, 1260]  # Periods in trading days (depends on convention)
    
    # Define column names dynamically based on the input column
    if column == 'Volume':
        base = f"average{column}Last{{}}"
    else:
        base = f"average{column}PriceLast{{}}"  # For price-related columns like 'Close', 'Open'
    
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
    
    data_rows = []  # List to hold rows of data for the final DataFrame
    
    for ticker in tickers:
        row = [ticker]        
        for period in periods:
            # Take the most recent 'period' number of rows (up to the current date)
            sliced = df[ticker].iloc[:period]  # Take the last 'period' rows for this ticker
            row.append(sliced.mean(skipna=True))  # Calculate mean, skipping NaNs
        data_rows.append(row)
    
    # Create the final DataFrame from the collected data
    aggregated_df = pd.DataFrame(data_rows, columns=columns)
    
    return aggregated_df


def gather_asset_info(df, asset_info):
    """
    Gathers additional information for each ticker available through Yahoo Finance API.
    The tickers are assumed to be the column values of column 'Ticker' of the DataFrame.

    Parameters:
    -----------
    df : pandas.DataFrame
        DataFrame that contains a column 'Ticker'.
    
    asset_info : list
        A list of fields (strings) to fetch from Yahoo Finance for each ticker. For example: 
        ['previousClose', 'marketCap', 'peRatio'].

    Returns:
    --------
    pandas.DataFrame
        A new DataFrame with additional information for each ticker merged with the original DataFrame.
        The new DataFrame will contain the original data, along with the additional info for each ticker.


    """
    
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
RELEVANT_INFO = [
    'city', 'country', 'industryKey', 'sectorKey', 'fullTimeEmployees', 'currency', 'tradeable', 'quoteType',
    'financialCurrency', 'region', 'fullExchangeName', 'exchange', 'exchangeTimezoneName', 'market', 'marketCap',
    'shortName', 'ebitda', 'totalDebt', 'debtToEquity', 'totalRevenue']

class Portfolio:
    """
    A class for managing a collection of stock tickers, downloading financial data from Yahoo Finance, 
    and performing analysis such as daily price changes, volatility, and candle patterns. It is mainly a preparation to
    maintain clean code through entire project. 

    Parameters:
    -----------
    tickers : list
        A list of stock tickers (strings) to include in the portfolio.
    
    start_date : str, optional
        The start date for fetching data in 'YYYY-MM-DD' format. If not provided, the period parameter is used.
    
    end_date : str, optional
        The end date for fetching data in 'YYYY-MM-DD' format. If not provided, the period parameter is used.
    
    period : str, optional
        The period for fetching data (e.g., '1d', '1wk', '1mo', '1y'). Only used if start_date and end_date are not provided.
    
    """
    def __init__(
                 self, 
                 tickers: List[str], 
                 start_date: Optional[str] = None, 
                 end_date: Optional[str] = None, 
                 period: str = '1d'
                ):
        """
        Initializes the Portfolio class, determines the period to use for data download, and fetches stock data.
        
        Args:
            tickers (List[str]): List of stock tickers (e.g., ['AAPL', 'MSFT']). Check how yfinance reads tickers of stocks.
            start_date (Optional[str]): The start date for downloading data.
            end_date (Optional[str]): The end date for downloading data.
            period (str): The period for downloading stock data (e.g., '1d', '1wk').
        """
        # Managing the optionality of start-end dates and period:
        if start_date and end_date:
            self.start_date = start_date
            self.end_date = end_date
            self.use_period = False
        else:
            self.period = period
            self.use_period = True

        # Not sure if this attribute will be held in the future
        self.tickers = tickers
        
        # Downloading data grouped by columns (for easier analysis) and by ticker (for individual stock analysis)
        # It is important to distinguish these 2 different types of downloading data, because yahoo finance API 
        # downloads data and creates data frame with different types of multi-level index columns.

        self.column_grouped_data = self.download_data(group_by= 'column')
        self.ticker_grouped_data = self.download_data(group_by= 'Ticker')

        # Main data frame containing info about each stock. Each row is one day for one distinct asset. 
        # This frame will be used later in feature engineering, thus it will have many columns (features).
        self.daily_info = self.get_daily_info()
    
    def download_data(self, group_by: str):
        """
        Downloads financial data for the tickers in the portfolio using Yahoo Finance API.
        
        Args:
            group_by (str): The grouping method for the data, either 'column' or 'Ticker'. It is important later
                            for handling multi-level columns created by yfinance API.
        
        Returns:
            pd.DataFrame: A DataFrame containing the downloaded data, grouped as requested.
        """
        if self.use_period:
                data = yf.download(self.tickers, group_by= group_by, period=self.period)
        else:
            data = yf.download(self.tickers, group_by= group_by, start=self.start_date, end=self.end_date)
        return data

    def get_prices(self, column: Optional[str] = None):
        """
        Retrieves the prices of the tickers in the portfolio from column grouped data frame. Will be important for 
        optimization methods and calculations.
        
        Args:
            column (Optional[str]): The specific column (type of price e.g. Close) to extract the prices for.
        
        Returns:
            pd.DataFrame: A DataFrame with the prices, sorted by date.
        """
        if column:
            data = self.column_grouped_data[column]
        data = self.column_grouped_data

         # Ensure the data is in DataFrame format
        if isinstance(data, pd.Series):
            data = data.to_frame(name=self.tickers[0])
        
        # Reset index to ensure the 'Date' column is usable
        data = data.reset_index()

        # Ensure the date column has right format
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)

        # Managing chronological order of dates
        return data.sort_values('Date', ascending=False)
    
    def get_daily_info(self):
        """
        Calculates and returns daily information for each ticker in the portfolio, including price changes,
        daily returns, volatility, and candle patterns and  maaany more (up to 50 features)
        
        Returns:
            pd.DataFrame: A DataFrame containing the daily information for each ticker.
        """
        data = self.ticker_grouped_data

        # Handling multi-level columns in a harsh but elegant way
        data = data.stack(level=0).rename_axis(['Date', 'Ticker']).reset_index(level=1)

        # Calculate daily price change, daily return, range, and volatility ratio
        data['Change'] = data['Close'] - data['Open']
        data['Daily Return'] = np.where(data['Open'] != 0, (data['Close'] - data['Open']) / data['Open'], np.nan)
        data['Range'] = data['High'] - data['Low']
        data['Volatility Ratio'] = data['Range'] / data['Open']
        data['Upper Wick'] = data['High'] - np.maximum(data['Open'], data['Close'])
        data['Lower Wick'] = np.minimum(data['Open'], data['Close']) - data['Low']
        data['Candle type'] = np.where(data['Close'] > data['Open'], 1, 0)  # 1 means bullish, 0 means bearish

        # Merge with additional asset information
        # First, calculating averages, then adding info NOT DEPENDING ON DATE!
        data = pd.merge(data, calculate_averages(self.get_prices(), 'Close'), how='left', on='Ticker')
        data = pd.merge(data, calculate_averages(self.get_prices(), 'Volume'), how='left', on='Ticker')

        data = gather_asset_info(data, RELEVANT_INFO)
        return data

        
# ------------------------------ TESTS ----------------------------------------#

# Tickers for wig20
wig20 = [
    "ALR.WA", "ALE.WA", "BDX.WA", "CCC.WA", "CDR.WA",
    "CPS.WA", "DNP.WA", "KTY.WA", "JSW.WA", "KGH.WA",
    "KRU.WA", "LPP.WA", "MBK.WA", "OPL.WA", "PEO.WA",
    "PGE.WA", "PKN.WA", "PKO.WA", "PZU.WA", "PCO.WA"
]


start = datetime.datetime(2022,11,15)
end = datetime.datetime(2025,4,4)
period = '6y'

pft_1 = Portfolio(wig20, period = period)
pft_2 = Portfolio(wig20, start_date= start, end_date= end)

portfolios = [pft_1, pft_2]

for pft in portfolios:
    print(f'{pft} tickers: {pft.tickers}')
    print('Example showing differences between column/ticker downloading methods')
    print(f'{pft} column grouped data downloaded from Yahoo: {pft.column_grouped_data}')
    print(f'{pft} ticker grouped data downloaded from Yahoo: {pft.ticker_grouped_data}')
    print('Main table for portfolio:')
    print(pft.daily_info)

pft_1.daily_info.to_csv('pft1_daily_info')