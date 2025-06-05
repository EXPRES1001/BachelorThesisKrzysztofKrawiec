import pandas as pd
import numpy as np

from skfolio.model_selection import WalkForward, cross_val_predict
from skfolio import RiskMeasure
from skfolio.optimization import EqualWeighted, InverseVolatility, Random
from skfolio.optimization import MeanRisk, ObjectiveFunction, HierarchicalRiskParity, RiskBudgeting
from skfolio.prior import BlackLitterman
from skfolio.moments import DenoiseCovariance, EmpiricalMu
from skfolio.prior import EmpiricalPrior
from skfolio.distance import KendallDistance

import plotly.graph_objects as go


REBALANCING_PERIODS_TO_DAYS = {
    'Annually': 252,
    'Semi-Annually': 126,
    'Quarterly': 63,
    'Monthly': 21,
    'Weekly': 5
}

TRAIN_TIME_PERIODS_TO_DAYS = {
    '3Years': 756,
    '2Years': 504,
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



def create_performance_metrics_table(portfolio, initial_value, name="Portfolio 1"):
    metrics = {
        "Sharpe Ratio": round(portfolio.sharpe_ratio, 4),
        "Annualized Sharpe": round(portfolio.annualized_sharpe_ratio, 4),
        "Variance": round(portfolio.variance, 6),
        "Annualized Variance": round(portfolio.annualized_variance, 6),
        "Standard Deviation": round(portfolio.standard_deviation, 4),
        "Annualized Std Dev": round(portfolio.annualized_standard_deviation, 4),
        "Mean Return": round(portfolio.mean, 4),
        "Annualized Mean": round(portfolio.annualized_mean, 4),
        "Cumulative Return": round(portfolio.cumulative_returns[-1], 4),
        "Final Value": round((1 + portfolio.cumulative_returns[-1]) * initial_value, 4)
    }

    df = pd.DataFrame(list(metrics.items()), columns=["Metrics", name])
    return df

def backtest_portfolio(portfolio_historical_returns, method, benchmark, rebalancing_period, train_time_period, views=None):
    
    test_size = REBALANCING_PERIODS_TO_DAYS[rebalancing_period]
    train_size = TRAIN_TIME_PERIODS_TO_DAYS[train_time_period]
    benchmark_estimator = BENCHMARK_PORTFOLIOS_TO_ESTIMATORS[benchmark]
    
    if method == 'MeanVariance':
        model =  MeanRisk(
            objective_function = ObjectiveFunction.MINIMIZE_RISK,
            risk_measure = RiskMeasure.VARIANCE,
            risk_free_rate= 0.05,
            prior_estimator= EmpiricalPrior(
                mu_estimator= EmpiricalMu(), 
                covariance_estimator = DenoiseCovariance()
                ),
            portfolio_params=dict(name="Minimum Variance Portfolio")
        )
    elif method == 'BlackLitterman' and views is not None:
        analyst_views = views
        model = MeanRisk(
            risk_measure=RiskMeasure.VARIANCE,
            objective_function=ObjectiveFunction.MINIMIZE_RISK,
            prior_estimator=BlackLitterman(
                views= analyst_views,
                risk_free_rate= 0.05),
            portfolio_params = dict(name="Black & Litterman")
        )
    elif method == 'RP':
        model = RiskBudgeting(
            risk_measure = RiskMeasure.VARIANCE,
            risk_free_rate = 0.05,
            prior_estimator = EmpiricalPrior(
                mu_estimator = EmpiricalMu(), 
                covariance_estimator = DenoiseCovariance()
            ),
            portfolio_params=dict(name="Risk Parity - Variance"),
        )
    elif method == 'HRP':
        model = HierarchicalRiskParity(
            risk_measure=RiskMeasure.VARIANCE, portfolio_params=dict(name="HRP-Variance"),
            distance_estimator=KendallDistance(absolute=True),
            prior_estimator = EmpiricalPrior(
                mu_estimator= EmpiricalMu(), 
                covariance_estimator = DenoiseCovariance()
                )
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