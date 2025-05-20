from shiny import App, render, ui, reactive

from skfolio.datasets import load_ftse100_dataset
from skfolio.preprocessing import prices_to_returns

from yf_data_gathering import PERIODS, gather_data


prices = prices_to_returns(load_ftse100_dataset())

app_ui = ui.page_fluid(
    ui.tags.style("""
        h1.custom-title {
            font-family: 'Segoe UI', sans-serif;
            color: #2c3e50;
            font-weight: 600;
            font-size: 32px;
            margin-top: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
    """),
    ui.h1("📈 Investment Portfolio Analysis Utilizing AutoML and AutoEDA", class_="custom-title"),
    ui.navset_pill_list(  
        ui.nav_panel("Portfolio Customization", 
                    ui.layout_columns(
                        ui.card(
                            ui.card_header("Portoflio setup"),
                            ui.input_select(
                                id="ticker_mode",
                                label="How do you want to pass the tickers?",
                                choices={
                                    "default": "Ready tickers",     
                                    "file": "Via txt file",         
                                    "manual": "Manually"          
                                },
                                selected="txt"
                            ),
                            ui.output_ui("dynamic_input_area1"),
                            ui.input_radio_buttons(
                                id='date_or_period', 
                                label='Dates or period?',
                                choices={
                                    'period': 'Period',
                                    'dates': 'Start Date and End Date'
                                },
                                selected='period'
                                ),
                            ui.output_ui("dynamic_input_area2")
                        ),
                        ui.card(
                            ui.div("Here you can customize your portfolio"),
                            ui.hr(),
                            ui.output_text("tickers_preview")
                        ),
                        ui.card(
                            ui.output_data_frame("portfolio_prices")
                        ),
                        col_widths=(4, 3, 5),
                    ),
                    ),
        ui.nav_panel("Portfolio Optimization", "Panel B content"),
        id="tab"),
        title="BachelorThesis2025KrzysztofKrawiec",
    )  

def server(input, output, session):
    @render.ui
    def dynamic_input_area1():
        if input.ticker_mode() == "file":
            return ui.input_file("tickers_file", "Choose txt file with asset tickers", accept=[".txt"], multiple=False)
        
        elif input.ticker_mode() == "manual":
            return ui.input_text("tickers_manual", "Insert your tickers (with quotatian and comma separated)")
        
        elif input.ticker_mode() == "default":
            return ui.input_select(
                "tickers_default",
                "Choose your default tickers",
                choices=['SP500', 'WIG20', 'FTSE100'],
                multiple=False
            )
        
    @render.ui 
    def dynamic_input_area2():
        if input.date_or_period() == "period":
            return ui.input_select('period_selection', "Period", PERIODS)
        else:
            return ui.input_date_range('date_range', "Date range", start="2020-01-01")
        
    @render.text
    def tickers_preview():
        mode = input.ticker_mode()
        
        if mode == "file":
            files = input.tickers_file()
            if not files:
                return "No file."
            filepath = files[0]["datapath"]
        
            with open(filepath, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
            tickers = [f"{line.strip()}" for line in lines if line.strip()]
            return f"Tickers from file: \n {', '.join(tickers)}"
        
        elif mode == "manual":
            txt = input.tickers_manual()
            tickers = [x.strip() for x in txt.split(",") if x.strip()]
            return f"Manually inserted tickers: \n {', '.join(tickers)}"
        
        elif mode == "default":
            tickers = input.tickers_default()
            return f"Chosen group of tickers: {tickers}"
        
    @render.DataGrid
    def portfolio_prices():
        mode = input.ticker_mode()
        if input.date_or_period() == 'period':
            if mode == "file":
                files = input.tickers_file()
                if not files:
                    return "No file."
                filepath = files[0]["datapath"]
            
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
                tickers = [f"{line.strip()}" for line in lines if line.strip()]
                df = gather_data(tickers= tickers, period= input.date_or_period())
                return render.DataGrid(df) 
            elif mode == "manual":
                txt = input.tickers_manual()
                tickers = [x.strip() for x in txt.split(",") if x.strip()]
                df = gather_data(tickers= tickers, period= input.date_or_period())
                return render.DataGrid(df) 
            elif mode == "default":
                return
        else:
            if mode == "file":
                files = input.tickers_file()
                if not files:
                    return "No file."
                filepath = files[0]["datapath"]
            
                with open(filepath, "r", encoding="utf-8") as f:
                    lines = f.read().splitlines()
                tickers = [line.strip() for line in lines if line.strip()]
                df = gather_data(tickers= tickers, start_date= input.date_or_period()[0], end_date=input.date_or_period()[1])
                return render.DataGrid(df) 
            elif mode == "manual":
                txt = input.tickers_manual()
                tickers = [x.strip() for x in txt.split(",") if x.strip()]
                df = gather_data(tickers= tickers, start_date= input.date_or_period()[0], end_date=input.date_or_period()[1])
                return render.DataGrid(df)  
            elif mode == "default":
                return



app = App(app_ui, server)