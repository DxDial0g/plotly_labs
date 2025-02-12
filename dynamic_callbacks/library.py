from typing import Any, Callable

import dash
import dash_bootstrap_components as dbc
import pandas as pd
from dash import Input, Output, State, dash_table, html

from .callback_manager import CallbackManager


class Figure:
    """Base class for figure components.

    This abstract class defines the interface for building figures and registering callbacks.
    """

    def build(self) -> Any:
        """Build the figure component.

        Returns:
            Any: The built figure component.
        """
        pass

    def register_callback(self, *, callback_manager: CallbackManager | None = None, **kwargs) -> Callable:
        """Register callbacks for the figure.

        Args:
            callback_manager (CallbackManager | None, optional): The callback manager instance.
                Defaults to None.
            **kwargs: Additional keyword arguments.

        Returns:
            Callable: The registered callback function.
        """
        pass


class TableBuilder(Figure):
    """A class for building interactive data tables with Dash.

    This class creates a data table with an alert component that displays information
    about selected cells.

    Attributes:
        data (pd.DataFrame): The data to display in the table.
        figure_title (str): The title of the table.
        html_table_id (dict): Dictionary containing table ID information.
        html_alert_id (dict): Dictionary containing alert ID information.
        columns (pd.Index): The columns of the data.
        callback_id (str): Unique identifier for the callback.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        suffix: str | None = None,
    ):
        """Initialize the TableBuilder.

        Args:
            data (pd.DataFrame): The data to display in the table.
            suffix (str | None, optional): Suffix for generating component IDs.
                If None, uses the object's id. Defaults to None.
        """
        self.data = data
        self.figure_title = f"Descriptive table {id(self)}"
        suffix = str(suffix or id(self)).replace(" ", "_").strip("-").strip("_").lower()
        self.html_table_id = {"type": f"{suffix}_tbl", "index": suffix}
        self.html_alert_id = {"type": f"{suffix}_alert", "index": suffix}
        self.columns = data.columns
        self.callback_id = str(suffix or id(self))

    def build(self) -> dbc.Container:
        """Build the table component with its container and alert.

        Returns:
            dbc.Container: A Bootstrap container containing the table and alert components.
        """
        page_size = min(len(self.data.index), 100)
        table = dash_table.DataTable(
            id=self.html_table_id,
            columns=[{"name": col, "id": col} for col in self.columns],
            data=self.data.to_dict("records"),
            page_size=page_size,
            style_header=dict(backgroundColor="rgb(230, 230, 230)"),
            style_cell=dict(backgroundColor="rgb(245, 245, 245)"),
            editable=False,
            column_selectable="single",
            style_table={"overflow": "scroll"},
        )
        return dbc.Container([
            dbc.Label(self.figure_title),
            table,
            dbc.Alert(children=[html.P(children=["Select a cell"])], id=self.html_alert_id),
        ])

    def register_callback(self, callback_manager: CallbackManager | None = None, **kwargs) -> Callable | None:
        """Register a callback for handling cell selection in the table.

        Args:
            callback_manager (CallbackManager | None, optional): The callback manager instance.
                Defaults to None.
            **kwargs: Additional keyword arguments passed to the callback registration.

        Returns:
            Callable | None: The registered callback function if callback_manager is provided,
            None otherwise.

        Note:
            The callback updates the alert component with information about the selected cell.
        """

        def describe_table(active_cell, item_id):
            """Callback function to describe the selected table cell.

            Args:
                active_cell (dict): Information about the selected cell.
                item_id (str): The ID of the table component.

            Returns:
                list: A list containing an html.P element with the cell description.

            Raises:
                dash.exceptions.PreventUpdate: If no cell is selected.
            """
            if active_cell is None:
                raise dash.exceptions.PreventUpdate

            print(active_cell, ":", item_id)
            value = self.data.iloc[active_cell["row"]][active_cell["column_id"]]
            return [
                html.P(
                    children=[
                        f"Selected cell: Row {active_cell['row']}, Column {active_cell['column']}, Value: {value}"
                    ]
                )
            ]

        if not callback_manager:
            return

        return callback_manager.register_callback(
            self.callback_id,
            describe_table,
            outputs=Output({"type": self.html_alert_id["type"], "index": dash.MATCH}, "children"),
            inputs=[Input({"type": self.html_table_id["type"], "index": dash.MATCH}, "active_cell")],
            states=[State({"type": self.html_table_id["type"], "index": dash.MATCH}, "id")],
            allow_duplicate=True,
            prevent_initial_call=False,
        )
