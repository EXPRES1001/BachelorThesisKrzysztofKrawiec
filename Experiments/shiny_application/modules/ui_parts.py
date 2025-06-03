from shiny import ui
from Experiments.shiny_application.modules.data_gathering import PERIODS
from shinywidgets import output_widget  


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

sidebar_content = ui.card(
    ui.card_header(
        ui.tags.h5("📈 Customize Data for Portfolio Analysis", class_="card-title"),
        class_="bg-primary text-white"  # Matching header style
    ),
    ui.input_select(
        'benchmark_portfolio',
        'Select your benchmark portfolio',
        ['EqualWeighted', 'Random', 'InverseVolatility']
    ),
    ui.input_radio_buttons(
        'plot_type',
        'Which plot do you want to see?',
        ['CumulativeReturns', 'Returns', 'ReturnsDistribution', 'RollingMeasure', 'Composition'],
        selected= 'CumulativeReturns',
        inline= False
    )
)


analysis_content = None

analysis_panel = ui.page_sidebar(
    ui.sidebar(sidebar_content, bg="#f8f8f8", open="closed", width="300px"),  
    ui.layout_columns(
        ui.card(
            ui.card_header(
                ui.tags.h5("📈 Visualisations", class_="card-title"),
                class_="bg-primary text-white"  # Matching header style
            ),
            output_widget("render_portfolio_plots")
        )
    ),
)

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
        selected= 'MeanVariance'
    ),
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
        {
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
        selected=  '4months'
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
