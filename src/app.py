import os
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
import pandas as pd
from download_db import download_database

# Ensure the database is downloaded
download_database()

# Correct database path
db_file = 'all_data_scaled.db'
engine = create_engine(f'sqlite:///{db_file}')

app = dash.Dash(__name__)
server = app.server

# Fetch unique dates from the features table
features = pd.read_sql('SELECT * FROM features', engine)
unique_dates = features['Date'].unique()

app.layout = html.Div([
    html.H1("R, T, N values for Magnetic Field for Out Board Sensor on Perihilon Dates with & without Machine Learning"),
    dcc.Dropdown(
        id='date-dropdown',
        options=[{'label': date, 'value': date} for date in unique_dates],
        value=['2023-10-07', '2023-04-10', '2022-06-26', '2022-10-12'],  # default dates
        multi=True
    ),
    dcc.Graph(id='magnetic-field-graph')
])

@app.callback(
    Output('magnetic-field-graph', 'figure'),
    Input('date-dropdown', 'value')
)
def update_graph(selected_dates):
    if not selected_dates:
        return go.Figure()

    fig = make_subplots(rows=2, cols=len(selected_dates), shared_xaxes=True, shared_yaxes=True)
    
    components = ['R', 'T', 'N']
    colors = ['red', 'green', 'orange']
    
    for i, date in enumerate(selected_dates):
        date_specific_data = features[features['Date'] == date]

        for row in date_specific_data.itertuples():
            # Query the required data from the database
            query = f"SELECT * FROM all_data_scaled WHERE hp_id = {row.Index}"
            selected_day = pd.read_sql(query, engine)
            break  # Assuming we plot only the first sample per date

        for j, component in enumerate(components):
            showlegend = i == 0  # Show legend only for the first column
            fig.add_trace(
                go.Scatter(x=selected_day['Time'], y=selected_day[f'{component}_orig'], name=component, line=dict(color=colors[j]), showlegend=showlegend),
                row=1, col=i+1
            )
            fig.add_trace(
                go.Scatter(x=selected_day['Time'], y=selected_day[f'{component}_pred_orig'], name=component, line=dict(color=colors[j]), showlegend=False),
                row=2, col=i+1
            )
        fig.update_xaxes(title_text="Time (seconds)", row=2, col=i+1)
    
    fig.update_yaxes(title_text="Real", row=1, col=1)
    fig.update_yaxes(title_text="Pred", row=2, col=1)
    fig.update_layout(height=600, title_text="R, T, N values for Magnetic Field")

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
