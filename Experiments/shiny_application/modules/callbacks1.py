from shiny import render, ui, req
from skfolio.preprocessing import prices_to_returns
from Experiments.shiny_application.modules.data_gathering import gather_data, PERIODS, PORTFOLIOS_TO_PRICES
from pathlib import Path

def register_callbacks1(input, output, session):
    # -- dynamic_input_data_source --------------------------------------------------
    @output
    @render.ui
    def dynamic_input_data_source():
        match input.data_source():
            case "yahoo":
                return ui.TagList(
                    ui.input_select(
                        "ticker_mode", 
                        "How do you want to pass the tickers?",
                        {
                            "default": "Default tickers (SP500)", 
                            "file": "Upload .txt file", 
                            "manual": "Enter manually"
                        },
                        selected="file",
                        width="100%"
                    ),
                    ui.output_ui("dynamic_input_ticker_mode"),
                    ui.card(
                        ui.card_header("Selected tickers"),
                        ui.output_text("tickers_preview")
                    ),
                    ui.input_radio_buttons(
                        id="date_or_period",
                        label='Date or period selection',
                        choices={
                            "period": ui.tags.span("📅 Fixed Period", class_="ms-2"), 
                            "dates": ui.tags.span("🗓️ Custom Date Range", class_="ms-2")
                        },
                        selected="period",
                        width="100%"
                    ),
                    ui.output_ui("dynamic_input_date_or_period")
                )
            case "prepared":
                return ui.TagList(
                    ui.input_select(
                        "data_frame",
                        "Choose your default data frame",
                        ['SP500', 'NASDAQ', 'FTSE100'],
                        selected= 'SP500',
                        width="100%"
                    ),
                    ui.output_ui("dynamic_input_data_frame_info")
                )
            
    # -- dynamic_input_data_frame_info ---------------------------------------------
    @output
    @render.ui
    def dynamic_input_data_frame_info():
        descriptions = {
            "SP500": {
                "icon": "📊",
                "title": "S&P 500 Dataset",
                "content": ui.markdown("""
                    **Contains:** Prices of 20 assets from the S&P 500 Index  
                    **Period:** 1990-01-02 to 2022-12-28  
                    **Price Type:** Adjusted close (CRSP standard)  
                    **Adjustments:** Includes all splits and dividend distributions
                    """)
            },
            "NASDAQ": {
                "icon": "💻",
                "title": "NASDAQ Composite Dataset",
                "content": ui.markdown("""
                    **Contains:** Prices of 1,455 assets from NASDAQ Composite  
                    **Period:** 2018-01-02 to 2023-05-31  
                    **Price Type:** Adjusted close (CRSP standard)  
                    **Adjustments:** Includes all splits and dividend distributions
                    """)
            },
            "FTSE100": {
                "icon": "🇬🇧",
                "title": "FTSE 100 Dataset",
                "content": ui.markdown(f"""
                    **Contains:** Prices of 64 assets from FTSE 100 Index  
                    **Period:** 2000-01-04 to 2023-05-31  
                    **Price Type:** Adjusted close (CRSP standard)  
                    **Adjustments:** Includes all splits and dividend distributions  
                    {'**Note:** Contains missing values (NaN)'}
                    """)
            }
        }

        selected = input.data_frame()
        desc = descriptions.get(selected, {})

        return ui.card(
            ui.card_header(
                ui.tags.h5(f"{desc.get('icon', '')} {desc.get('title', '')}", 
                        class_="card-title"),
                class_="bg-primary text-white"
            ),
            desc.get("content", "No dataset selected"),
        ) if selected else ui.TagList()
    
    # -- dynamic_input_portfolio_customization_guide --------------------------------
    @output
    @render.ui
    def dynamic_input_portfolio_customization_guide():
        match input.data_source():
            case "yahoo":
                return ui.TagList(
                    ui.markdown(
                    """
                    **On this page**, you can prepare and customize your portfolio for further analysis and optimization.  
                    #### 📌 Ticker Input Options:
                    1. **Manual Input**  
                    - Separate tickers with commas 
                    - Example: `"AAPL", "MSFT"`  
                    2. **Text File Upload**  
                    - Place one ticker per line
                    - No commas or additional formatting needed  
                    - Example file content:  
                        ```
                        AAPL  
                        MSFT  
                        ```
                    #### 💡 Pro Tip:
                    Use official ticker symbols from yahoo finance.
                    """
                    ),
                    ui.card_footer(
                        ui.tags.small("Note: All tickers will be validated before processing.", class_="text-muted")
                    )
                )
            case "prepared":
                return ui.TagList(
                    ui.markdown(
                    """
                    **On this page**, you can prepare and customize your portfolio for further analysis and optimization.  
                    #### 📌 Ready prepared portfolios:
                    1. **SP500**  
                    - Portfolio containing 20 assets from the S&P 500 Index
                    2. **FTSE100**  
                    - Portfolio containing 64 assets from FTSE 100 Index
                    3. **NASDAQ**
                    - Portfolio containing 1,455 assets from NASDAQ Composite
                    #### 💡 Pro Tip:
                    Use SP500 for faster calculations, NASDAQ for asset variety.
                    """
                    ),
                    ui.card_footer(
                        ui.tags.small("Note: In FTSE100 there are missing values .", class_="text-muted")
                    )
                )
   
    
    # -- dynamic_input_ticker_mode --------------------------------------------------
    @output
    @render.ui
    def dynamic_input_ticker_mode():
        match input.ticker_mode():
            case "file":
                return ui.input_file("tickers_file",
                                     "Choose txt file with asset tickers",
                                     accept=[".txt"])
            case "manual":
                return ui.input_text("tickers_manual",
                                     "Insert tickers (comma-separated)")
            case "default":
                return ui.input_select(
                    "tickers_default","Choose default tickers",
                    ["SP500","WIG20","FTSE100"])

    # -- dynamic_input_date_or_period --------------------------------------------------
    @output
    @render.ui
    def dynamic_input_date_or_period():
        if input.date_or_period() == "period":
            return ui.input_select("period_selection", "Period", PERIODS, selected= '5y')
        return ui.input_date_range("date_range", "Date range",
                                   start="2020-01-01")

    # -- dynamic_input_portfolio_prices
    @output
    @render.ui
    def dynamic_input_portfolio_prices():
        match input.data_source():
            case "yahoo":
                return ui.TagList(
                    ui.card(
                        ui.output_data_frame("yf_portfolio_prices"),
                        style="border: none; padding: 0;"  
                    )
                )
            case "prepared":
                return ui.TagList(
                    ui.card(
                        ui.output_data_frame("prepared_df_portfolio_prices"),
                        style="border: none; padding: 0;"  
                    )
                )


    # -- tickers_preview ------------------------------------------------------
    @output
    @render.text
    def tickers_preview():
        mode = input.ticker_mode()
        if mode == "file":
            files = input.tickers_file();  # reactive value
            if not files:
                return "No file."
            with open(files[0]["datapath"], encoding="utf-8") as f:
                tickers = [ln.strip() for ln in f if ln.strip()]
            tickers_wrapped = [f"\"{t}\"" for t in tickers]     
            return f"{', '.join(tickers_wrapped)}"

        if mode == "manual":
            txt = input.tickers_manual()
            tickers = [x.strip() for x in txt.split(",") if x.strip()]
            return f"{', '.join(tickers)}"

        if mode == "default":
            return f"{input.tickers_default()}"
    

    # -- yf_portfolio_prices -----------------------------------------------------
    @output
    @render.data_frame
    def yf_portfolio_prices():
        mode  = input.ticker_mode()
        dates = input.date_or_period()

        if mode == "file":
            files = input.tickers_file()
            if not files:
                return None
            with open(files[0]["datapath"], encoding="utf-8") as f:
                tickers = [ln.strip() for ln in f if ln.strip()]

        elif mode == "manual":
            tickers = [x.strip() for x in input.tickers_manual().split(",")
                    if x.strip()]

        elif mode == "default":
            return None   

        req(tickers)     

        try:
            if dates == "period":
                df = gather_data(tickers, period=input.period_selection())
            else:
                start, end = input.date_range()
                df = gather_data(tickers, start_date=start, end_date=end)

        except ValueError as e:
            return ui.markdown(f"**Błąd ⚠️**: {e}")
        
        data_dir = Path("Experiments/shiny_application/modules/data")
        data_dir.mkdir(parents=True, exist_ok=True)
        csv_path = data_dir / "yf_downloaded_data.csv"
        df.to_csv(csv_path, index=True)
        
        match input.price_or_return():
            case "Prices":
                df = df.reset_index()
                df['date'] = df['date'].dt.date
                df = df.sort_values(by='date', ascending= False)
                return df
            case "Returns":
                df = prices_to_returns(df).round(5)
                df = df.reset_index()
                df['date'] = df['date'].dt.date
                df = df.sort_values(by='date', ascending= False)
                return df
    

    # -- prepared_df_portfolio_prices -------------------------------------------
    @output
    @render.data_frame
    def prepared_df_portfolio_prices():
        pft = PORTFOLIOS_TO_PRICES[input.data_frame()]
        data_dir = Path("Experiments/shiny_application/modules/data")
        data_dir.mkdir(parents=True, exist_ok=True)
        csv_path = data_dir / "prepared_data.csv"
        pft.to_csv(csv_path, index=True)
        match input.price_or_return():
            case "Prices":
                pft = pft.reset_index()
                pft['Date'] = pft['Date'].dt.date
                pft = pft.sort_values(by='Date', ascending= False)                
                return pft
            case "Returns":
                pft = prices_to_returns(pft).round(5)
                pft = pft.reset_index()
                pft['Date'] = pft['Date'].dt.date
                pft = pft.sort_values(by='Date', ascending= False)
                return pft
