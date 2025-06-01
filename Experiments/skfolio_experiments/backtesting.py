import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


from skfolio.preprocessing import prices_to_returns
from skfolio.model_selection import WalkForward, cross_val_predict

from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn import set_config

from skfolio import RiskMeasure
from skfolio.optimization import MeanRisk, ObjectiveFunction, InverseVolatility

import plotly.graph_objects as go


WIG20 = [
        "ALR.WA", "ALE.WA", "BDX.WA", "CCC.WA", "CDR.WA",
        "CPS.WA", "DNP.WA", "KTY.WA", "JSW.WA", "KGH.WA",
        "KRU.WA", "LPP.WA", "MBK.WA", "OPL.WA", "PEO.WA",
        "PGE.WA", "PKN.WA", "PKO.WA", "PZU.WA", "PCO.WA"
    ]





def main():

    csv_path = Path("Experiments/shiny_application/modules/data/prepared_data.csv")
    prices = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    returns = prices_to_returns(prices)

    model =  MeanRisk(
    objective_function=ObjectiveFunction.MAXIMIZE_RATIO,
    risk_measure=RiskMeasure.VARIANCE,
    )
    
    pred = cross_val_predict(model, returns, cv=WalkForward(test_size=21, train_size=120))
    bench = cross_val_predict(InverseVolatility(), returns, cv=WalkForward(test_size=21, train_size=120))

    print(pred.cumulative_returns_df)
    print(returns.head())
    


if __name__ == "__main__":
    main()

