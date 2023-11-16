from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import plotly.graph_objects as go
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.google.auth

class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def outlined_button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        fig1, fig2, fig3, fig4 = anvil.server.call('get_user_data')

        self.plot_1.figure = fig1
        self.plot_2.figure = fig2
        self.plot_3.figure = fig3
        self.plot_4.figure = fig4