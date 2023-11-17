import anvil.users
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

#-----------------------------------------------------------------------------------------------------------------------------------
#Create pandas data frame from table
# https://anvil.works/forum/t/using-pandas-with-anvil/1699
@anvil.server.callable
def get_user_data():
    # Get an iterable object with all the rows in my_table
    all_records = app_tables.user_data.search()
    # For each row, pull out only the data we want to put into pandas
    dicts = [{'user_id': r['user_id'],
            'days_op_per_year': r['days_op_per_year'],
            'cost_fuel': r['cost_fuel'],
            'cost_electric': r['cost_electric'],
            'avg_pwr': r['avg_pwr'],
            'energy_inflation': r['energy_inflation'],
            'avg_solar_irr': r['avg_solar_irr'],
            'avg_wind_speed': r['avg_wind_speed'],
            'run_time': r['run_time'],
            'date_time': r['date_time'],
            'country': r['country'],
            'user_ip': r['user_ip']
            }
            for r in all_records]
    
    user_df = pd.DataFrame.from_dict(dicts)

    # Ensure the data for plotting has no NaN values
    user_df = user_df.dropna()
    
    print(f"User data frame \n {user_df} \n")
    data_types = user_df.dtypes
    print(data_types)

    #-------------------------------------------
    #Get plots done

    #-------------------------------------------
    # Create a pie chart
    country_counts = user_df['country'].value_counts()
    fig1 = px.pie(country_counts,
                  names=country_counts.index,
                  values=country_counts.values,
                  title='Country Distribution'
                 )

    #-------------------------------------------
    # Count the frequency of each user_id
    user_session_counts = user_df['user_id'].value_counts().reset_index()
    user_session_counts.columns = ['user_id', 'session_count']
    
    # Map each user_id to a sequential label
    session_label_map = {id: f"Session {i+1}" for i, id in enumerate(user_session_counts['user_id'].unique())}
    user_session_counts['user_id'] = user_session_counts['user_id'].map(session_label_map)
    
    # Create a bar chart
    fig2 = px.bar(user_session_counts, x='user_id', y='session_count', title='Frequency of User Sessions')

    # Update axis labels
    fig2.update_xaxes(title_text='User session number')
    fig2.update_yaxes(title_text='Frequency of runs per Sessions')

    #-------------------------------------------
    # Count the frequency of each user_ip
    user_ip_counts = user_df['user_ip'].value_counts().reset_index()
    user_ip_counts.columns = ['user_ip', 'frequency']
    
    # Map each user_ip to a sequential label
    user_label_map = {ip: f"User {i+1}" for i, ip in enumerate(user_ip_counts['user_ip'].unique())}
    user_ip_counts['user_ip'] = user_ip_counts['user_ip'].map(user_label_map)
    
    # Create a bar chart
    fig3 = px.bar(user_ip_counts, x='user_ip', y='frequency', title='Frequency of Dashboard Use by User IP Address')
    
    # Update axis labels
    fig3.update_xaxes(title_text='User ID')
    fig3.update_yaxes(title_text='Frequency for User')
    #-------------------------------------------
    # Create the parallel coordinates plot

    # Convert columns to numeric
    numeric_columns = ['days_op_per_year', 'cost_fuel', 'cost_electric', 'avg_pwr', 'energy_inflation', 'avg_solar_irr', 'avg_wind_speed', 'run_time']
    for col in numeric_columns:
        user_df[col] = pd.to_numeric(user_df[col], errors='coerce')

    # Optionally, remove rows with NaN values if they were created due to conversion errors
    user_df = user_df.dropna(subset=numeric_columns)

    # Normalize the columns
    # Normalize each column so that the values fall within a standard range,
    # typically 0 to 1. This can be done by subtracting the minimum value of 
    # each column and dividing by the range (max - min) of that column.
    
    columns_to_normalize = ['days_op_per_year',
                            'cost_fuel',
                            'cost_electric',
                            'avg_pwr',
                            'energy_inflation',
                            'avg_solar_irr',
                            'avg_wind_speed',
                            'run_time'
                           ]
    for col in columns_to_normalize:
        user_df[col] = pd.to_numeric(user_df[col], errors='coerce')  # Ensure the data is numeric
        user_df[col] = (user_df[col] - user_df[col].min()) / (user_df[col].max() - user_df[col].min())

    # Map each unique user_ip to a numerical value
    unique_ips = user_df['user_ip'].unique()
    ip_to_num = {ip: i for i, ip in enumerate(unique_ips)}
    user_df['user_ip_color'] = user_df['user_ip'].map(ip_to_num)

    #Not normalized plot version below
    
    # fig4 = px.parallel_coordinates(user_df, color='user_ip_color',
    #                             dimensions=['days_op_per_year',
    #                                         'cost_fuel',
    #                                         'cost_electric',
    #                                         'avg_pwr',
    #                                         'energy_inflation',
    #                                         'avg_solar_irr',
    #                                         'avg_wind_speed',
    #                                         'run_time'
    #                                        ],
    #                             labels={'user_id': 'User ID',
    #                                     'days_op_per_year': 'Days Operating per Year',
    #                                     'cost_fuel': 'Fuel Cost',
    #                                     'cost_electric': 'Electric Cost',
    #                                     'avg_pwr': 'Average Power',
    #                                     'energy_inflation': 'Energy Inflation',
    #                                     'avg_solar_irr': 'Average Solar Irradiance',
    #                                     'avg_wind_speed': 'Average Wind Speed',
    #                                     'run_time': 'Run Time'
    #                                    },
    #                             title="User Choices Across Different Parameters")

    fig4 = px.parallel_coordinates(user_df,
                              color='user_ip_color',     
                              dimensions=columns_to_normalize,
                                   labels={'user_id': 'User ID',
                                        'days_op_per_year': 'Days Operating per Year',
                                        'cost_fuel': 'Fuel Cost',
                                        'cost_electric': 'Electric Cost',
                                        'avg_pwr': 'Average Power',
                                        'energy_inflation': 'Energy Inflation',
                                        'avg_solar_irr': 'Average Solar Irradiance',
                                        'avg_wind_speed': 'Average Wind Speed',
                                        'run_time': 'Run Time'
                                       },
                              title="Normalized User Choices Across Different Parameters")

    #----------------------------------------
    # Create a box plot figure

    # Normalize the columns

    for col in columns_to_normalize:
        user_df[col] = pd.to_numeric(user_df[col], errors='coerce')  # Ensure the data is numeric
        user_df[col] = (user_df[col] - user_df[col].min()) / (user_df[col].max() - user_df[col].min())
    
    # Map each unique user_ip to a sequential label
    unique_ips = user_df['user_ip'].unique()
    ip_to_label = {ip: f"User {i+1}" for i, ip in enumerate(unique_ips)}
    user_df['user_label'] = user_df['user_ip'].map(ip_to_label)
   
    
    fig5 = go.Figure()
    
    # Add a box plot for each normalized column
    for col in columns_to_normalize:
        fig5.add_trace(go.Box(y=user_df[col], x=user_df['user_label'], name=col))
    
    # Update layout
    fig5.update_layout(title="Box Plots of Normalized Columns by User", xaxis_title="User", yaxis_title="Normalized Value")

    #------------------------------------
    #Scatter plot of user loggins
    # Convert 'date_time' to datetime objects
    # user_df['date_time'] = pd.to_datetime(user_df['date_time'], utc=True, errors='coerce')
    
    # # # Check if 'date_time' contains timezone information and remove it
    # # if user_df['date_time'].dt.tz is not None:
    # #     user_df['date_time'] = user_df['date_time'].dt.tz_localize(None)

    
    # # # Map each unique user_ip to a sequential label
    # # unique_ips = user_df['user_ip'].unique()
    # # ip_to_label = {ip: f"User {i+1}" for i, ip in enumerate(unique_ips)}
    # # user_df['user_label'] = user_df['user_ip'].map(ip_to_label)
    
    # # Create a scatter plot
    # fig6 = px.scatter(user_df, x='date_time', y='user_label', title='User Logins Over Time')
    
    # # Update layout
    # fig6.update_layout(xaxis_title='Date', yaxis_title='User', xaxis_rangeslider_visible=True)

    #ValueError: too many values to unpack (expected 5) whne runnig this section but only when returning fig6.
    # Can it be I need to split the amount of figres to return into tow functions?
    
    
    return fig1, fig2, fig3, fig4, fig5

    