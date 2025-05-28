from shiny import App
from modules.ui_parts import app_ui
from Experiments.shiny_application.modules.callbacks1 import register_callbacks1
from Experiments.shiny_application.modules.callbacks2 import register_callbacks2

def server(input, output, session):
    register_callbacks1(input, output, session)
    register_callbacks2(input, output, session)

app = App(app_ui, server)

if __name__ == "__main__":
    import shiny
    shiny.run_app(app, port=8000, reload=True)