from plotly.io import show

from skfolio.preprocessing import prices_to_returns
from skfolio.datasets import load_ftse100_dataset
from skfolio.optimization import MeanRisk, ObjectiveFunction
from skfolio.pre_selection import DropCorrelated
from skfolio import Population, RatioMeasure
from skfolio.model_selection import (
    CombinatorialPurgedCV,
    cross_val_predict,
    optimal_folds_number,
)

from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn import set_config

# First, focus solely on Mean-Variance optimization and its extensions  

prices = load_ftse100_dataset()

X = prices_to_returns(prices)
X_train, X_test = train_test_split(X, test_size=0.33, shuffle=False)

# 1. Maximum Sharpe Ratio model without pre-selection and fit on the training set
model1 = MeanRisk(objective_function=ObjectiveFunction.MAXIMIZE_RATIO)
model1.fit(X_train)
model1.weights_
 
# 2. Maximum Sharpe Ratio model with pre-selection using Pipepline and fit on the training set
set_config(transform_output="pandas")

model2 = Pipeline(
    [
        ("drop_correlated", DropCorrelated(threshold=0.5)),
        ("optimization", MeanRisk(objective_function=ObjectiveFunction.MAXIMIZE_RATIO)),
    ]
)
model2.fit(X_train)
model2.named_steps["optimization"].weights_

# 3. Predict both models on the test set
ptf1 = model1.predict(X_test)
ptf1.name = "model1"
ptf2 = model2.predict(X_test)
ptf2.name = "model2"

print(ptf1.n_assets)
print(ptf2.n_assets)

# Each predicted object is a MultiPeriodPortfolio. For improved analysis, we can add them to a Population
population = Population([ptf1, ptf2])

population.plot_cumulative_returns() # model2 performs better than model1

# Only using one testing path (the historical path) may not be enough for comparing both models. 
# For a more robust analysis, we can use the CombinatorialPurgedCV to create 
# multiple testing paths from different training folds combinations.

n_folds, n_test_folds = optimal_folds_number(
    n_observations=X_test.shape[0],
    target_n_test_paths=100,
    target_train_size=800,
)

cv = CombinatorialPurgedCV(n_folds=n_folds, n_test_folds=n_test_folds)
cv.summary(X_test)

pred_1 = cross_val_predict(
    model1,
    X_test,
    cv=cv,
    n_jobs=-1,
    portfolio_params=dict(annualized_factor=252, tag="model1"),
)

pred_2 = cross_val_predict(
    model2,
    X_test,
    cv=cv,
    n_jobs=-1,
    portfolio_params=dict(annualized_factor=252, tag="model2"),
)