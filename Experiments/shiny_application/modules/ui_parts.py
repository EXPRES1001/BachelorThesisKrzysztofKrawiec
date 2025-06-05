from shiny import ui
from shinywidgets import output_widget  

# ------------- CUSTOMIZATION PANEL ----------------------

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
        ui.tags.h5("💡 Portfolio Customization Guide", class_="card-title"),
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

# ---------- ANALYSIS PANEL ---------------------------

analysis_guide_panel = ui.card(
    ui.card_header(
                ui.tags.h5("💡 Visualisation Setup Guide", class_="card-title"),
                class_="bg-primary text-white"  # Matching header style
            ),
    ui.output_ui("dynamic_input_portfolio_analysis_guide")
)

asset_analysis_summary = ui.card(
    ui.card_header(
                ui.tags.h5("🔎 Asset Performance Summary Panel", class_="card-title"),
                class_="bg-primary text-white"  # Matching header style
            ),
    ui.output_data_frame("render_asset_summary")
)

analysis_setup_panel = ui.card(
            ui.card_header(
                ui.tags.h5("⚙️ Visualisation Setup Panel", class_="card-title"),
                class_="bg-primary text-white"  # Matching header style
            ),
            ui.output_ui("dynamic_input_asset_selectize"),
            ui.input_select(
                'plot_type',
                'Select which plot do you want to see',
                {
                    'PricesReturns': 'Prices/Returns of Assets Over Time',
                    'RollingSharpe': 'Rolling Sharpe Ratio Over Time Windows'
                }
            ),
            asset_analysis_summary
        )

analysis_visualisations_panel = ui.card(
            ui.card_header(
                ui.tags.h5("📈Asset Visualisations", class_="card-title"),
                class_="bg-primary text-white"  # Matching header style
            ),
            ui.layout_columns(
                ui.output_text("render_prices_mode_text"),
                ui.input_slider(
                    'window_slider',
                    'Set a window for a rolling sharpe ratio',
                    5,
                    100,
                    30
                )
            ),
            output_widget("render_stock_returns_plot"),
            output_widget("render_rolling_sharpe_plot")
        )

analysis_panel = ui.layout_columns(
        analysis_guide_panel,
        analysis_setup_panel,
        analysis_visualisations_panel,
        col_widths=(3, 3, 6)
    )


# -------- OPTIMIZATION PANEL ----------------------------

backtesting_setup = ui.card(
    ui.card_header(
            ui.tags.h5("⚙️ Optimization and Backtesting Setup", class_="card-title"),
            class_="bg-primary text-white"  # Matching header style
        ),
    ui.input_select(
        'backtesting_benchmark_portfolio',
        'Select benchmark portfolio for backtesting',
        ['EqualWeighted', 'Random', 'InverseVolatility'],
        selected= 'EqualWeighted'
    ),
    ui.input_select(
        'optimization_method',
        'Select portfolio optimization method for backtesting',
        {
            'MeanVariance': 'Mean-Variance Optimization', 'BlackLitterman': 'Black-Litterman Optimization',
            'RP': 'Risk-Parity Optimization', 'HRP': 'Hierarchical Risk Parity Optimization'
        },
        selected= 'BlackLitterman'
    ),
    ui.output_ui("dynamic_input_markdown_analyst_views"),
    ui.output_ui("dynamic_input_analyst_views"),
    ui.input_select(
        'rebalancing_time_period',
        'Choose your rebalancing period (on the first day)',
        {
            'Annually': 'Rebalance Annually', 'Semi-Annually': 'Rebalance Semi-Annually',
            'Quarterly': 'Rebalance Quarterly', 'Monthly': 'Rebalance Monthly', 'Weekly': 'Rebalance Weekly'
        },
        selected= 'Monthly'
    ),
    ui.input_select(
        'train_time_period',
        'Choose your train time period',
        {   '3Years': 'Three Years',
            '2Years': 'Two Years',
            'Year': 'One Year',
            '11months': '11 Months',
            '10months': '10 Months',
            '9months': '9 Months',
            '8months': '8 Months',
            '7months': '7 Months',
            '6months': '6 Months',
            '5months': '5 Months',
            '4months': '4 Months',
            '3months': '3 Months',
            '2months': '2 Months',
            '1month': '1 Month',
            '3weeks': '3 Weeks',
            '2weeks': '2 Weeks',
            '1week': '1 Week'
        },
        selected=  'Year'
    ),
    ui.input_numeric(
        'initial_amount',
        'Insert your initial amount of capital',
        10000,
        min = 1
    )
)

data_summary = ui.card(
    ui.output_data_frame("render_benchmark_statistics")
)

backtesting_plots = ui.card(
    output_widget("render_benchmark_cumulative_returns_plot")
)

backtesting_summary = ui.card(
    ui.card_header(
            ui.tags.h5("🔍 Optimization and Backtesting Summary", class_="card-title"),
            class_="bg-primary text-white"  # Matching header style
        ),
    ui.layout_columns(
        data_summary,
        backtesting_plots,
        col_widths=(4,8)
    )
)

optimization_panel = ui.layout_columns(
    backtesting_setup,
    backtesting_summary,
    col_widths=(3, 9)
)


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
        ui.nav_panel("Portfolio Optimization and Backtesting", optimization_panel),
        ui.nav_spacer(),
        ui.nav_control(ui.input_dark_mode()),
        id="tab",
        selected="Portfolio Customization",
    ),
    title="BachelorThesis2025KrzysztofKrawiec"
)
