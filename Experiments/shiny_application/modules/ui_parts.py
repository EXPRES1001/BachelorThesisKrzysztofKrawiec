from shiny import ui
from Experiments.shiny_application.modules.data_gathering import PERIODS


portfolio_data_source_panel = ui.card(
    ui.card_header(
        ui.tags.h5("🌐 Data Source", class_="card-title"),
        class_="bg-primary text-white"
    ),
    ui.input_radio_buttons(
        "data_source",
        None, 
        {
            "yahoo": "Download fresh data from Yahoo Finance",
            "prepared": "Use prepared dataset"
        },
        selected="prepared"
    )
)


portolio_setup_panel = ui.card(
    ui.card_header(
        ui.tags.h5("⚙️ Portfolio Setup", class_="card-title"),
        class_="bg-primary text-white"  
    ),
    portfolio_data_source_panel,
    ui.output_ui('dynamic_input_data_source'),
    )


portfolio_setup_guide_panel = ui.card(
        ui.card_header(
        ui.tags.h5("📊 Portfolio Customization Guide", class_="card-title"),
        class_="bg-primary text-white"  # Adds a nice header background
        ),
        ui.output_ui('dynamic_input_portfolio_customization_guide')
        )


portfolio_prices_panel = ui.card(
    ui.card_header(
        ui.tags.h5("📈 Selected Portfolio Data", class_="card-title"),
        class_="bg-primary text-white"  # Matching header style
    ),
    ui.input_radio_buttons(
        "price_or_return",
        None,
        ['Prices', 'Returns'],
        selected='Prices',
        inline=True
    ),
    ui.output_ui("dynamic_input_portfolio_prices")
    )


customization_panel = ui.layout_columns(
    portfolio_setup_guide_panel,
    portolio_setup_panel,
    portfolio_prices_panel,
    col_widths=(3,3,6)
)


analysis_panel = ui.layout_columns()


optimization_panel = ui.layout_columns()


title_css = ui.tags.style("""
  h1.custom-title{
    font-family:'Segoe UI',sans-serif;color:#2c3e50;
    font-weight:600;font-size:32px;margin:10px 0;text-align:center;
  }""")



app_ui = ui.page_fluid(
    title_css,
    ui.h1("📈 Investment Portfolio Analysis Utilizing AutoML and AutoEDA",
          class_="custom-title"),
    ui.navset_pill(
        ui.nav_panel("Portfolio Customization", customization_panel),
        ui.nav_panel("Portfolio Exploratory Analysis", analysis_panel),
        ui.nav_panel("Portfolio Optimization", optimization_panel),
        ui.nav_spacer(),
        ui.nav_control(ui.input_dark_mode()),
        id="tab",
        selected="Portfolio Customization",
    ),
    title="BachelorThesis2025KrzysztofKrawiec"
)
