"""
Main application script for creating a dynamic table dashboard using Dash.

This script sets up a Dash web application that displays multiple interactive tables
with the ability to refresh them using a button click. It demonstrates the usage of
Context, TableBuilder, and CallbackManager classes to manage the application state
and callbacks.

Note:
    The script should be run directly to start the Dash server.
"""

import dash
import pandas as pd
from dash import Input, Output, html

from .callback_manager import CallbackManager
from .context import Context
from .library import TableBuilder

# Create the Dash app
app = dash.Dash(__name__)
app.layout = html.Div([html.Button("Create Tables", id="create-button"), html.Div(id="tables-container")])

# Initialize application components and data
callback_manager = CallbackManager(app)

# Sample data for demonstration
sample_df1 = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
sample_df2 = pd.DataFrame({"X": [100, 200], "Y": [300, 400]})

# Initialize Context with tables and callback manager
Context(
    figures=[
        TableBuilder(sample_df1),
        TableBuilder(sample_df2),
    ],
    callback_manager_type=CallbackManager,
)

# Set up context and register callbacks
Context.load_callback_manager(app)
Context.register_callbacks()


@app.callback(
    Output("tables-container", "children"),
    Input("create-button", "n_clicks"),
)
def create_tables(n_clicks: int | None) -> list:
    """Callback function to create and update tables in response to button clicks.

    This callback is triggered when the "Create Tables" button is clicked. It rebuilds
    all tables managed by the Context class and returns them as children of the
    tables container.

    Args:
        n_clicks (int | None): Number of times the button has been clicked.
            None if the button hasn't been clicked yet.

    Returns:
        list: A list of table components to be rendered in the tables container.
            Returns an empty list if the button hasn't been clicked.

    Note:
        The tables are cleared and rebuilt on each button click using Context.build_figures().
    """
    if n_clicks is None:
        return []

    return Context.build_figures(clear_before=True)


if __name__ == "__main__":
    app.run_server(debug=True)
