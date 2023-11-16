from ._anvil_designer import Form1Template
from anvil import *
import anvil.users
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

        #User login
        # https://blog.futuresmart.ai/mastering-user-management-in-anvil-a-comprehensive-tutorial
        anvil.users.login_with_form()
        # email_addr = anvil.google.auth.login()
        # print(f"User logged in as {email_addr}")
    
        fig1, fig2, fig3, fig4, fig5 = anvil.server.call('get_user_data')
    
        self.plot_1.figure = fig1
        self.plot_2.figure = fig2
        self.plot_3.figure = fig3
        self.plot_4.figure = fig4
        self.plot_5.figure = fig5
        # self.plot_6.figure = fig6

    def outlined_button_1_click(self, **event_args):
        """This method is called when the button is clicked"""
        fig1, fig2, fig3, fig4, fig5 = anvil.server.call('get_user_data')

        self.plot_1.figure = fig1
        self.plot_2.figure = fig2
        self.plot_3.figure = fig3
        self.plot_4.figure = fig4
        self.plot_5.figure = fig5
        # self.plot_6.figure = fig6


    def log_out_button_click(self, **event_args):
        """This method is called when the button is clicked"""
        if confirm("Are you sure you want to log out {}?".format(anvil.users.get_user()['email'])):
            anvil.users.logout()
            self.content_panel.clear()
            open_form('LogOut')


