import pandas as pd
import numpy as np

from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

from data_gathering import Portfolio


        
class PortfolioOptimization(Portfolio):
    def __init__(self):
        self.expected_returns = mean_historical_return(self.historical_data) # notation: mu
        self.covariance_matrix = CovarianceShrinkage(self.historical_data).ledoit_wolf() # notation: S

    def optimize(self, method='MV'):
        mu = self.expected_returns
        S = self.covariance_matrix
        if method == 'MV':
            ef = EfficientFrontier(mu, S)
            weights = ef.max_sharpe()  # ugly version of weights
            cleaned_weights = ef.clean_weights() # extremely small weights are rounded to 0; is a dictionary -> ticker: weight
            performance = ef.portfolio_performance(verbose=True)
        return cleaned_weights
    

 
