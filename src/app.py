#!/bin/bash

import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Load the combined DataFrame
df = pd.read_csv('combined_feature_importances.csv')

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Prepare data by type
def prepare_data(df, type_label):
    # Filter DataFrame by the specified type
    df_filtered = df[df['Type'] == type_label]
    # Create pivot table
    pivot_df = df_filtered.pivot_table(
            values='Normalized_Importance', index='Duration', columns='Feature', aggfunc='sum')
    # Filter out columns where all values are zero
    pivot_df = pivot_df.loc[:, (pivot_df != 0).any(axis=0)]
    return pivot_df

# Create Plotly Express graphs for each type
def create_figure(data, title):
    fig = px.line(data, title=title)  # Change from area to line plot
    fig.update_layout(yaxis_title='Average Treatment Effect', xaxis_title='Time of Profile')
    return fig

# Types to include in the dashboard
types = ['IBS_R', 'IBS_N', 'IBS_T', 'OBS_R', 'OBS_N', 'OBS_T']
figures = [create_figure(prepare_data(df, type_label), f'Cumulative Normalized Feature Importance of Heater Profiles {type_label}') for type_label in types]

# Add Interval component to the layout and graphs
app.layout = html.Div([
    dcc.Interval(
        id='interval-component',
        interval=10*60*1000,  # 10 minutes in milliseconds
        n_intervals=0  # initial value
    ),
    html.Div([dcc.Graph(figure=fig) for fig in figures])
])

# Callback to reload the page
@app.callback(
    dash.dependencies.Output('interval-component', 'n_intervals'),
    [dash.dependencies.Input('interval-component', 'n_intervals')]
)
def refresh_page(n):
    return n

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True, port=8071)
