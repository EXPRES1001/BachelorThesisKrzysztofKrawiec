from shiny import render, ui, req
from skfolio.preprocessing import prices_to_returns
from Experiments.shiny_application.modules.data_gathering import gather_data, PERIODS, PORTFOLIOS_TO_PRICES

def register_callbacks2(input, output, session):
    pass