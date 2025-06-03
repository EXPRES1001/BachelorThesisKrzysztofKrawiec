import pandas as pd

from shinywidgets import render_widget 
from shiny import render
from pathlib import Path 
from Experiments.shiny_application.modules.optimization.optimization_and_backtesting import backtest_portfolio, plot_cumulative_returns, compare_multiperiod_portfolios
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

        strategy, benchmark_portfolio = backtest_portfolio(returns, optimization_method, benchmark, rebalancing_period, train_time_period)

        return plot_cumulative_returns(returns, optimization_method, strategy, benchmark, benchmark_portfolio)
    
    # -- render_benchmark_statistics -----------------------------------------
    @output
    @render.data_frame
    def render_benchmark_statistics():
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

        strategy, benchmark_portfolio = backtest_portfolio(returns, optimization_method, benchmark, rebalancing_period, train_time_period)

        return compare_multiperiod_portfolios(strategy, benchmark_portfolio, input.initial_amount(), [optimization_method, 
                                                                                                      benchmark])

