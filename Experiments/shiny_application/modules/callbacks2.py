from skfolio.optimization import EqualWeighted, Random, InverseVolatility
from pathlib import Path
import pandas as pd
from shinywidgets import render_widget  

def register_callbacks2(input, output, session):
    # -- render_portfolio_plots ----------------------------
    @output
    @render_widget
    def render_portfolio_plots():
        match input.data_source():
            case 'yahoo':
                csv_path = Path("Experiments/shiny_application/modules/data/yf_downloaded_data.csv")
                prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            case 'prepared':
                csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
                prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                
        match input.benchmark_portfolio():
            case 'EqualWeighted':  
                portfolio = EqualWeighted().fit(prices).predict(prices)
            case 'Random':
                portfolio = Random().fit(prices).predict(prices)
            case 'InverseVolatility':
                portfolio = InverseVolatility().fit(prices).predict(prices)
        
        match input.plot_type():
            case 'CumulativeReturns':
                fig = portfolio.plot_cumulative_returns()
                return fig
            case 'Returns':
                fig = portfolio.plot_returns()
                return fig
            case 'ReturnsDistribution':
                fig = portfolio.plot_returns_distribution()
                return fig
            case 'RollingMeasure':
                fig = portfolio.plot_rolling_measure()
                return fig
            case 'Composition':
                fig = portfolio.plot_composition()
                return fig
            
