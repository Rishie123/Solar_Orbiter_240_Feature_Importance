import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

solar_data = pd.read_csv("../Solar_Orbiter.csv")
sensor_columns = solar_data.columns[1:-2]  # Exclude 'Date', 'anomaly', and 'anomaly_score'

# Initialize the Dash app
app = dash.Dash(__name__, title="Advanced Solar Orbiter Data Visualization")
server=app.server

# Layout of the Dash app, with four major sections
app.layout = html.Div([
    html.H1("Solar Orbiter Instrument Data Visualization", style={'text-align': 'center'}),
    dcc.Checklist(
        id='sensor-checklist',
        options=[{'label': col, 'value': col} for col in sensor_columns],
        value=[sensor_columns[0]],
        inline=True
    ),
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=solar_data['Date'].min(),
        max_date_allowed=solar_data['Date'].max(),
        start_date=solar_data['Date'].min(),
        end_date=solar_data['Date'].max()
    ),
    html.Div([
        html.Div([dcc.Graph(id='time-series-chart')], className="six columns"),
        html.Div([dcc.Graph(id='correlation-heatmap')], className="six columns"),
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='anomaly-score-chart')], className="six columns"),
        html.Div([dcc.Graph(id='sensor-histogram')], className="six columns"),
    ], className="row"),
    html.Div(id='anomaly-stats', style={'margin-top': '20px', 'text-align': 'center'})
])

# Callbacks to update graphs
@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('anomaly-score-chart', 'figure'),
     Output('sensor-histogram', 'figure')],
    [Input('sensor-checklist', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(selected_sensors, start_date, end_date):
    filtered_data = solar_data[(solar_data['Date'] >= start_date) & (solar_data['Date'] <= end_date)]
    
    # Time Series Chart
    time_series_fig = go.Figure()
    for sensor in selected_sensors:
        time_series_fig.add_trace(
            go.Scatter(
                x=filtered_data['Date'],
                y=filtered_data[sensor],
                mode='lines+markers',
                name=sensor
            )
        )
    time_series_fig.update_layout(title="Time Series of Selected Sensors")




    return time_series_fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
