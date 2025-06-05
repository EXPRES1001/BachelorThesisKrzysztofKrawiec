import pandas as pd

from shinywidgets import render_widget 
from shiny import render, ui
from pathlib import Path 
from Experiments.shiny_application.modules.optimization.optimization_and_backtesting import backtest_portfolio, plot_cumulative_returns, create_performance_metrics_table
from skfolio.preprocessing import prices_to_returns

def register_callbacks3(input, output, session):
    # -- dynamic_input_markdown_analyst_views ------------------------------
    @output
    @render.ui
    def dynamic_input_markdown_analyst_views():
        if input.optimization_method() == 'BlackLitterman':
            return ui.markdown(
                """
                **Analyst Views Input Format (Black-Litterman)**  
                
                Please enter your views about expected asset returns using the following formats:

                - **Absolute view**: `asset_i = a`  
                Example: `"KGH.WA = 0.00015"` → KGH.WA is expected to have a **daily return of 0.015%**

                - **Relative view**: `asset_i - asset_j = b`  
                Example: `"KHG.WA - PCO.WA = 0.00039"` → KGH.WA is expected to **outperform** PCO.WA by **0.039% daily**

                - **Combined**: `asset_i = a` and `asset_i - asset_j = b`
                Example: `"KHG.WA = 0.00015", "KGH.WA - PCO.WA = 0.00039"` → **combined views**

                All returns must be expressed in the **same frequency** as your input data (daily)
                """
            )
    # -- dynamic_input_analyst_views ----------------------------------------
    @output
    @render.ui
    def dynamic_input_analyst_views():
        if input.optimization_method() == 'BlackLitterman':
            return ui.input_text(
                    'views_black_litterman',
                    "Enter your analyst views below:"
            )

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
        views_raw = input.views_black_litterman()
        
        views_list = [
            view.strip().strip('"')
            for view in views_raw.split(',')
            if view.strip()
        ]

        strategy, benchmark_portfolio = backtest_portfolio(
            returns, optimization_method, benchmark, rebalancing_period, train_time_period, views_list
            )

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
        
        views_raw = input.views_black_litterman()
        views_list = [
            view.strip().strip('"')
            for view in views_raw.split(',')
            if view.strip()
        ]
        
        initial_value = input.initial_amount()

        if not views_raw:
            strategy, benchmark_portfolio = backtest_portfolio(
                returns, optimization_method, benchmark, rebalancing_period, train_time_period
                )
        else:
            strategy, benchmark_portfolio = backtest_portfolio(
                returns, optimization_method, benchmark, rebalancing_period, train_time_period, views_list
                )

        strategy_table = create_performance_metrics_table(strategy, initial_value, optimization_method)
        benchmark_table = create_performance_metrics_table(benchmark_portfolio, initial_value, benchmark)

        comparison_table = pd.merge(strategy_table, benchmark_table, on='Metrics')
        return comparison_table

