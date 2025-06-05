from pathlib import Path
import pandas as pd
import numpy as np
from shinywidgets import render_widget  
from shiny import render, ui
import plotly.graph_objects as go
from skfolio.preprocessing import prices_to_returns


def register_callbacks2(input, output, session):
# -- dynamic_input_portfolio_analysis_guide --------------------------
    @output
    @render.ui
    def dynamic_input_portfolio_analysis_guide():
        match input.data_source():
            case 'yahoo':
                  return ui.TagList(
                            ui.markdown(
                                """
                                **On this page**, you can perform a preliminary analysis of assets in your portfolio.  
                                Analyze them individually or compare multiple assets side-by-side.

                                #### 📌 Asset Plot Options:
                                1. **Asset Selection**  
                                - Search and select one or more asset tickers for analysis.

                                2. **Plot Type Selection**  
                                - Choose the type of plot you want to generate:
                                    - Historical prices  
                                    - Historical returns  
                                    - Rolling Sharpe ratio  
                                - For the Rolling Sharpe ratio, you can customize the window size used for calculations.

                                #### 💡 Tip:
                                You can toggle between prices and returns on the main page.  
                                The selected mode is displayed at the top-left corner of the Plot tab.
                                """
                            ),
                            ui.card_footer(
                                ui.tags.small("Note: All tickers are validated before processing.", class_="text-muted")
                            )
                        )

            case 'prepared':
                  return ui.TagList(
                            ui.markdown(
                                """
                                **On this page**, you can perform a preliminary analysis of assets in your portfolio.  
                                Analyze them individually or compare multiple assets side-by-side.

                                #### 📌 Asset Plot Options:
                                1. **Asset Selection**  
                                - Search and select one or more asset tickers for analysis.

                                2. **Plot Type Selection**  
                                - Choose the type of plot you want to generate:
                                    - Historical prices  
                                    - Historical returns  
                                    - Rolling Sharpe ratio  
                                - For the Rolling Sharpe ratio, you can customize the window size used for calculations.

                                #### 💡 Tip:
                                You can toggle between prices and returns on the main page.  
                                The selected mode is displayed at the top-left corner of the Plot tab.
                                """
                            ),
                            ui.card_footer(
                                ui.tags.small("Note: All tickers are validated before processing.", class_="text-muted")
                            )
                        )

# -- dynamic_input_asset_selectize -----------------------------------
    @output
    @render.ui
    def dynamic_input_asset_selectize():
            match input.data_source():
                case 'yahoo':
                    csv_path = Path("Experiments/shiny_application/modules/data/yf_downloaded_data.csv")
                    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                case 'prepared':
                    csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
                    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            asset_names = list(prices.columns)
            dynamic_select = ui.input_selectize(
                'selected_assets',
                'Choose assets for performance analysis',
                asset_names,
                multiple= True,
                selected= asset_names[1]
            )
            return dynamic_select

# -- render_asset_summary -----------------------------------------------      
    @output
    @render.data_frame
    def render_asset_summary():
        tickers = list(input.selected_assets())
            
        match input.data_source():
                case 'yahoo':
                    csv_path = Path("Experiments/shiny_application/modules/data/yf_downloaded_data.csv")
                    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                case 'prepared':
                    csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
                    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        match input.price_or_return():
                case "Prices":
                    data = prices.copy()[tickers]
                    returns = prices_to_returns(data).round(5)[tickers]


                    cumulative_returns = (data / data.iloc[0]) - 1
                    cagr = (data.iloc[-1] / data.iloc[0]) ** (252 / len(data)) - 1
                    volatility = returns.std() * np.sqrt(252)
                    annual_return = (1 + returns.mean()) ** 252 - 1

                    sharpe = (returns.mean() * 252 - 0.05) / (returns.std() * np.sqrt(252))
                    skewness = returns.skew()
                    kurtosis = returns.kurtosis()
                    positive_days = (returns > 0).sum()
                    negative_days = (returns < 0).sum()

                    metrics_df = pd.DataFrame({
                        'CAGR': cagr,
                        'Annual Volatility': volatility,
                        'Annual Return': annual_return,
                        'Sharpe Ratio': sharpe,
                        'Skewness': skewness,
                        'Kurtosis': kurtosis,
                        'Positive Days': positive_days,
                        'Negative Days': negative_days
                    })
                    metrics_df = metrics_df.T.reset_index()
                    metrics_df = metrics_df.rename(columns={'index': 'Metric'})
                    return metrics_df.round(4)
    
                case "Returns":
                    returns = prices_to_returns(prices).round(5)[tickers]
                    cumulative_returns = (1 + returns).cumprod() - 1
                    cagr = (1 + returns.mean()) ** 252 - 1
                    volatility = returns.std() * np.sqrt(252)
                    annual_return = (1 + returns.mean()) ** 252 - 1
        
                    sharpe = (returns.mean() * 252 - 0.05) / (returns.std() * np.sqrt(252))
                    skewness = returns.skew()
                    kurtosis = returns.kurtosis()
                    positive_days = (returns > 0).sum()
                    negative_days = (returns < 0).sum()
                    
                    metrics_df = pd.DataFrame({
                        'CAGR': cagr,
                        'Annual Volatility': volatility,
                        'Annual Return': annual_return,
                        'Sharpe Ratio': sharpe,
                        'Skewness': skewness,
                        'Kurtosis': kurtosis,
                        'Positive Days': positive_days,
                        'Negative Days': negative_days
                    })
                    metrics_df = metrics_df.T.reset_index()
                    metrics_df = metrics_df.rename(columns={'index': 'Metric'})
                    return metrics_df.round(4)

        
        

# -- render_stock_returns_plot ----------------------------------------
    @output
    @render_widget 
    def render_stock_returns_plot():
            match input.data_source():
                case 'yahoo':
                    csv_path = Path("Experiments/shiny_application/modules/data/yf_downloaded_data.csv")
                    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                case 'prepared':
                    csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
                    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
            match input.price_or_return():
                case "Prices":
                    df = prices.copy()
                case "Returns":
                    df = prices_to_returns(prices).round(5)
                    
            tickers = list(input.selected_assets())
            
            df = df[tickers]
            
            fig = go.Figure()
            if not tickers:
                return fig
            for col in df.columns:
                fig.add_trace(
                    go.Scatter(x=df.index.strftime("%Y-%m-%d").tolist(), y=df[col], mode='lines', name=col)
                    )
                
            fig.update_layout(title="Asset Historical Returns", xaxis_title="Date", yaxis_title= f'{input.price_or_return()}')
            return fig
    
# -- render_prices_mode_text ---------------------------------------------------
    @output
    @render.text
    def render_prices_mode_text():
         return f'Current Mode: {input.price_or_return()}'
        
# -- render_rolling_sharpe_ratio_plot ------------------------------------------
    @output
    @render_widget 
    def render_rolling_sharpe_plot():
        match input.data_source():
                    case 'yahoo':
                        csv_path = Path("Experiments/shiny_application/modules/data/yf_downloaded_data.csv")
                        prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
                    case 'prepared':
                        csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
                        prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
        returns = prices_to_returns(prices)
        tickers = list(input.selected_assets())
        if not tickers:
            return go.Figure()

        df = returns[tickers]  
        window = input.window_slider()  

        risk_free_rate = 0.00

        rolling_mean = df.rolling(window = window).mean()
        rolling_std = df.rolling(window = window).std()
        rolling_sharpe = ((rolling_mean - risk_free_rate) / rolling_std).dropna()

        fig = go.Figure()

        for col in df.columns:
                fig.add_trace(go.Scatter(
                    x = df.index.strftime("%Y-%m-%d").tolist() ,
                    y = rolling_sharpe[col],
                    mode='lines',
                    name=col
                ))
        fig.update_layout(
                title=f"{window}-day Rolling Sharpe Ratio",
                xaxis_title = "Date",
                yaxis_title = "Sharpe Ratio",
                height=500
            )

        return fig

            
     
        