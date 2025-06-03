import pandas as pd
import numpy as np

from skfolio.model_selection import WalkForward, cross_val_predict
from skfolio import RiskMeasure
from skfolio.optimization import EqualWeighted, InverseVolatility, Random
from skfolio.optimization import MeanRisk, ObjectiveFunction, HierarchicalRiskParity, RiskBudgeting
from skfolio.prior import BlackLitterman
import plotly.graph_objects as go


REBALANCING_PERIODS_TO_DAYS = {
    'Annually': 252,
    'Semi-Annually': 126,
    'Quarterly': 63,
    'Monthly': 21,
    'Weekly': 5
}

TRAIN_TIME_PERIODS_TO_DAYS = {
    'Year': 252,
    '11months': 231,
    '10months': 210,
    '9months': 189,
    '8months': 168,
    '7months': 147,
    '6months': 126,
    '5months': 105,
    '4months': 84,
    '3months': 63,
    '2months': 42,
    '1month': 21,
    '3weeks': 15,
    '2weeks': 10,
    '1week': 5
}

BENCHMARK_PORTFOLIOS_TO_ESTIMATORS = {
    'EqualWeighted': EqualWeighted(),
    'Random': Random(), 
    'InverseVolatility': InverseVolatility()
}


def backtest_portfolio(portfolio_historical_returns, method, benchmark, rebalancing_period, train_time_period):
    
    test_size = REBALANCING_PERIODS_TO_DAYS[rebalancing_period]
    train_size = TRAIN_TIME_PERIODS_TO_DAYS[train_time_period]
    benchmark_estimator = BENCHMARK_PORTFOLIOS_TO_ESTIMATORS[benchmark]
    
    if method == 'MeanVariance':
        model =  MeanRisk(
            objective_function=ObjectiveFunction.MAXIMIZE_RATIO,
            risk_measure=RiskMeasure.VARIANCE,
        )
    elif method == 'BlackLitterman':
        model = MeanRisk(
            risk_measure=RiskMeasure.VARIANCE,
            objective_function=ObjectiveFunction.MAXIMIZE_RATIO,
            prior_estimator=BlackLitterman(views=None)
        )
    elif method == 'RP':
        model = RiskBudgeting(
            risk_measure=RiskMeasure.VARIANCE
        )
    elif method == 'HRP':
        model = HierarchicalRiskParity(
            risk_measure=RiskMeasure.VARIANCE
        )
    else:
        raise ValueError("Selected method does not exist!")


    strategy = cross_val_predict(model, portfolio_historical_returns, cv=WalkForward(test_size= test_size, train_size= train_size))
    benchmark_portfolio = cross_val_predict(benchmark_estimator, portfolio_historical_returns, cv=WalkForward(test_size= test_size, train_size= train_size))

    return (strategy, benchmark_portfolio)

def plot_cumulative_returns(portfolio_historical_returns, method, strategy, benchmark, benchmark_portfolio):
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=portfolio_historical_returns.index.strftime("%Y-%m-%d").tolist(),
        y=strategy.cumulative_returns,
        mode='lines',
        name=f'{method}',
        line=dict(color='blue')
    ))

    fig.add_trace(go.Scatter(
        x=portfolio_historical_returns.index.strftime("%Y-%m-%d").tolist(),
        y=benchmark_portfolio.cumulative_returns,
        mode='lines',
        name=f'{benchmark}',
        line=dict(color='red')
    ))

    fig.update_layout(
    title= f'Cumulative Returns: {method} vs {benchmark}',
    xaxis_title='Date',
    yaxis_title='Cumulative Return',
    yaxis=dict(tickformat=".1%"), 
    template='plotly_white',
    legend=dict(x=0.01, y=0.99, bordercolor='gray', borderwidth=0.5)
    )

    return fig

def compare_multiperiod_portfolios(p1, p2, initial_amount, names=["Portfolio 1", "Portfolio 2"]):
    metrics = [
        "Mean Return (Ann.)",
        "Volatility (Ann.)",
        "Sharpe Ratio",
        "Sortino Ratio",
        "Skewness",
        "Kurtosis",
        "Cumulative Return",
        "Final Value"
    ]

    descriptions = [
        "Annualized average return (%)",
        "Annualized volatility (%)",
        "Risk-adjusted return (Sharpe)",
        "Downside risk-adjusted return (Sortino)",
        "Asymmetry of return distribution",
        "Fat tails in return distribution",
        "Total return over full period (%)",
        "Final portfolio value in currency"
    ]

    data = {
        "Mean Return (Ann.)": [
            p1.annualized_mean,
            p2.annualized_mean
        ],
        "Volatility (Ann.)": [
            p1.annualized_variance,
            p2.annualized_variance
        ],
        "Sharpe Ratio": [
            p1.sharpe_ratio,
            p2.sharpe_ratio
        ],
        "Sortino Ratio": [
            p1.sortino_ratio,
            p2.sortino_ratio
        ],
        "Skewness": [
            p1.skew,
            p2.skew
        ],
        "Kurtosis": [
            p1.kurtosis,
            p2.kurtosis
        ],
        "Cumulative Return": [
            p1.cumulative_returns[-1],
            p2.cumulative_returns[-1]
        ],
        "Final Value": [
            (p1.cumulative_returns[-1]) * initial_amount,
            (p2.cumulative_returns[-1]) * initial_amount
        ]
    }

    df = pd.DataFrame(data, index=names).T
    df.insert(0, "Metrics", metrics)
    return df.round(4)