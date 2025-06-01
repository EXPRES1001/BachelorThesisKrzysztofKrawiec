import pandas as pd

from shinywidgets import render_widget 
from pathlib import Path 
from Experiments.shiny_application.modules.optimization.optimization_and_backtesting import backtest_portfolio, REBALANCING_PERIODS_TO_DAYS, TRAIN_TIME_PERIODS_TO_DAYS, BENCHMARK_PORTFOLIOS_TO_ESTIMATORS
from skfolio.preprocessing import prices_to_returns

def register_callbacks3(input, output, session):
    # -- render_benchmark_cumulative_returns_plot ----------------------------
    @output
    @render_widget
    def render_benchmark_cumulative_returns_plot():
        match input.data_source():
            case 'yahoo':
                csv_path = Path("Experiments/shiny_application/modules/data/yf_downloaded_data.csv")
                prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            case 'prepared':
                csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
                prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        
        returns = prices_to_returns(prices)
        optimization_method = input.optimization_method()
        benchmark = input.backtesting_benchmark_portfolio()
        rebalancing_period = input.rebalancing_time_period()
        train_time_period = input.train_time_period()

        return backtest_portfolio(returns, optimization_method, benchmark, rebalancing_period, train_time_period)

