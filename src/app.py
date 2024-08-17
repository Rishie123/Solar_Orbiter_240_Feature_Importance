import pandas as pd  # Pandas for data manipulation
import dash  # Dash library for creating web applications
from dash import dcc, html, dash_table  # Components for building layout
from dash.dependencies import Input, Output  # Callbacks to update layout based on user input
import plotly.express as px  # Plotly Express for creating interactive visualizations
import plotly.graph_objects as go  # Plotly Graph Objects for more control over visualizations
from sklearn.preprocessing import MinMaxScaler

# Load the dataset
data_path = "Solar_Orbiter_with_anomalies.csv"  # Path to dataset file
data_path2 = "Solar_Orbiter_with_anomalies2.csv"
solar_data = pd.read_csv(data_path)  # Read dataset into DataFrame
solar_data2 = pd.read_csv(data_path2)   

# Convert the 'Date' column to datetime format
solar_data['Date'] = pd.to_datetime(solar_data['Date'])
solar_data2['Date'] = pd.to_datetime(solar_data2['Date'])

# Filter out data from May 5 to May 11
start_exclude = pd.to_datetime('2021-05-05')
end_exclude = pd.to_datetime('2021-05-11')
solar_data = solar_data[~((solar_data['Date'] >= start_exclude) & (solar_data['Date'] <= end_exclude))]
solar_data2 = solar_data2[~((solar_data2['Date'] >= start_exclude) & (solar_data2['Date'] <= end_exclude))]

# Load the SHAP values data
shap_values_path = "shap_values.csv"  # Update with the correct path to your SHAP values CSV
shap_data = pd.read_csv(shap_values_path)

# Create the feature importance figure
feature_importance_fig = px.line(shap_data, x='Date', y=shap_data.columns[:-1],
                                 title='Feature Importance for Predicting Anomalies On Different Dates',
                                 labels={'value': 'SHAP Value', 'Date': 'Date'},
                                 template='plotly')
feature_importance_fig.update_layout(
    title_font_size=28,  # Decrease title font size
    xaxis_title_font_size=22,  # Decrease x-axis title font size
    yaxis_title_font_size=22,  # Decrease y-axis title font size
    legend_font_size=22,  # Decrease legend font size
    xaxis=dict(tickfont=dict(size=18)),  # Set x-axis tick labels size to 18
    yaxis=dict(tickfont=dict(size=18))   # Set y-axis tick labels size to 18
)

# Initialize the Dash app
app = dash.Dash(__name__, title="Solar Orbiter Data Visualization")  # Title of the Dash app which is showed in the browser tab
server = app.server

# Remove the 'Date' and 'anomaly_score' columns from the checklist options
checklist_options = [{'label': col, 'value': col} for col in solar_data.columns if col not in ['Date', 'anomaly_score']]

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Solar Orbiter Instrument Data Visualization", style={'text-align': 'center'}),  # Title
    # Checklist to select instruments
    dcc.Checklist(
        id='instrument-checklist',  # Component ID
        options=checklist_options,  # Options for checklist
        value=[solar_data.columns[1]],  # Default selected value (first instrument)
        inline=True
    ),
    # Date range picker
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=solar_data['Date'].min(),  # Minimum date allowed
        max_date_allowed=solar_data['Date'].max(),  # Maximum date allowed
        start_date=solar_data['Date'].min(),  # Default start date
        end_date=solar_data['Date'].max()  # Default end date
    ),
    # Three rows, each containing graphs
    html.Div([
        html.Div([dcc.Graph(id='time-series-chart')], className="six columns"),  # Time Series Chart
        html.Div([dcc.Graph(id='correlation-heatmap')], className="six columns"),  # Correlation Heatmap
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='scaled-time-series-chart')], className="six columns"),  # Scaled Time Series Chart
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='anomaly-score-chart')], className="six columns"),  # Anomaly Score Chart
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='rolling-mean-heatmap')], className="six columns"),  # Rolling Mean Heatmap
    ], className="row"),
    html.Div(id='anomaly-stats', style={'margin-top': '20px', 'text-align': 'center'}),  # Anomaly Stats
    html.Iframe(
        srcDoc=open("shap_values_plot.html").read(),
        style={"height": "500px", "width": "100%"}
    ),
    # Add the feature importance graph at the bottom
    html.Div([
        dcc.Graph(figure=feature_importance_fig, id='feature-importance-chart')
    ])
])

# Callbacks to update graphs
@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('scaled-time-series-chart', 'figure'),
     Output('anomaly-score-chart', 'figure'),
     Output('rolling-mean-heatmap', 'figure')],
    [Input('instrument-checklist', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(selected_instruments, start_date, end_date):
    """
    Callback function to update graphs based on user input.
    Args:
    selected_instruments (list): List of selected instruments.
    start_date (str): Start date selected by the user.
    end_date (str): End date selected by the user.
    Returns:
    figs (list): List of figures for each graph.
    """
    filtered_data = solar_data[(solar_data['Date'] >= start_date) & (solar_data['Date'] <= end_date)]  # Filtering data based on selected date range
    filtered_data2 = solar_data2[(solar_data2['Date'] >= start_date) & (solar_data2['Date'] <= end_date)]  # Filtering data based on selected date range

    # Normalize the data
    scaler = MinMaxScaler(feature_range=(-1, 1))
    scaled_data = filtered_data.copy()
    columns_to_scale = [col for col in selected_instruments if col not in ['IBS_R', 'IBS_T', 'IBS_N', 'OBS_R', 'OBS_T', 'OBS_N']]
    scaled_data[columns_to_scale] = scaler.fit_transform(filtered_data[columns_to_scale])

    # Time Series Chart
    time_series_fig = go.Figure()  # Creating a new figure for time series chart
    for instrument in selected_instruments:
        time_series_fig.add_trace(
            go.Scatter(
                x=filtered_data['Date'],  # X-axis data
                y=filtered_data[instrument],  # Y-axis data
                mode='lines+markers',  # Display mode
                name=instrument  # Instrument name
            )
        )
    time_series_fig.update_layout(
        title="Time Series of Selected Instruments",
        title_font_size=28,  # Decrease title font size
        xaxis_title_font_size=22,  # Decrease x-axis title font size
        yaxis_title_font_size=22,  # Decrease y-axis title font size
        legend_font_size=22,  # Decrease legend font size
        xaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22)),  # Set x-axis tick labels size to 18
        yaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22))   # Set y-axis tick labels size to 18
    )  # Updating layout of time series chart
    
    # Correlation Heatmap
    correlation_fig = go.Figure(
        go.Heatmap(
            z=scaled_data[selected_instruments].corr(),  # Calculating correlation matrix on scaled data
            x=selected_instruments,  # X-axis labels
            y=selected_instruments,  # Y-axis labels
            colorscale='Viridis'  # Color scale
        )
    )
    correlation_fig.update_layout(
        title="Correlation Heatmap",
        title_font_size=28,  # Decrease title font size
        xaxis_title_font_size=22,  # Decrease x-axis title font size
        yaxis_title_font_size=22,  # Decrease y-axis title font size
        legend_font_size=22,  # Decrease legend font size
        xaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22)),  # Set x-axis tick labels size to 18
        yaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22))   # Set y-axis tick labels size to 18
    )  # Updating layout of correlation heatmap

    # Scaled Time Series Chart
    scaled_time_series_fig = go.Figure()  # Creating a new figure for scaled time series chart
    for instrument in selected_instruments:
        scaled_time_series_fig.add_trace(
            go.Scatter(
                x=scaled_data['Date'],  # X-axis data
                y=scaled_data[instrument],  # Y-axis data
                mode='lines+markers',  # Display mode
                name=instrument  # Instrument name
            )
        )
    scaled_time_series_fig.update_layout(
        title="Scaled Time Series Plot between -1 and 1",
        title_font_size=28,  # Decrease title font size
        xaxis_title_font_size=22,  # Decrease x-axis title font size
        yaxis_title_font_size=22,  # Decrease y-axis title font size
        legend_font_size=22,  # Decrease legend font size
        xaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22)),  # Set x-axis tick labels size to 18
        yaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22))   # Set y-axis tick labels size to 18
    )  # Updating layout of scaled time series chart

    # Anomaly Score Chart
    anomaly_score_fig = go.Figure()  # Create a new figure for the anomaly score chart
    anomaly_score_fig.add_trace(go.Scatter(
        x=filtered_data2['Date'],  # Set the x-axis as the Date column of the filtered data
        y=filtered_data2['anomaly_score'],  # Set the y-axis as the anomaly_score column of the filtered data
        mode='lines+markers',  # Display both lines and markers on the graph
        name='Anomaly Score',  # Name the trace, which will appear in the legend
        marker=dict(
            color=[ 'red' if val < 0 else 'blue' for val in filtered_data2['anomaly_score'] ],  # Use list comprehension to assign colors conditionally
            # Markers will be red if the anomaly score is below 0, otherwise blue
            size=5,  # Set the size of the markers
            line=dict(
                color='DarkSlateGrey',  # Color of the line around each marker
                width=2  # Width of the line around each marker
            )
        )
    ))
    anomaly_score_fig.update_layout(
        title="Anomaly Scores Over Time (Lower the scores, higher chances of anomaly, negative score means definitely anomaly)",  # Main title of the chart
        xaxis_title='Date',  # Title for the x-axis
        yaxis_title='Anomaly Score',  # Title for the y-axis
        title_font_size=28,  # Decrease title font size
        xaxis_title_font_size=22,  # Decrease x-axis title font size
        yaxis_title_font_size=22,  # Decrease y-axis title font size
        legend_font_size=22,  # Decrease legend font size
        xaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22)),  # Set x-axis tick labels size to 18
        yaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22))   # Set y-axis tick labels size to 18
    )
    
    # 5-Day Rolling Mean Heatmap
    rolling_mean_data = scaled_data[selected_instruments].rolling(window=5).mean()
    rolling_mean_fig = go.Figure(
        go.Heatmap(
            z=rolling_mean_data.corr(),  # Correlation of rolling mean data on scaled data
            x=selected_instruments,  # X-axis labels
            y=selected_instruments,  # Y-axis labels
            colorscale='Viridis'  # Color scale
        )
    )
    rolling_mean_fig.update_layout(
        title="5-Day Rolling Mean Correlation Heatmap",
        title_font_size=28,  # Decrease title font size
        xaxis_title_font_size=22,  # Decrease x-axis title font size
        yaxis_title_font_size=22,  # Decrease y-axis title font size
        legend_font_size=22,  # Decrease legend font size
        xaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22)),  # Set x-axis tick labels size to 18
        yaxis=dict(tickfont=dict(size=18), titlefont=dict(size=22))   # Set y-axis tick labels size to 18
    )  # Updating layout of rolling mean heatmap
    
    return time_series_fig, correlation_fig, scaled_time_series_fig, anomaly_score_fig, rolling_mean_fig  # Return updated figures

"""References:
1. https://dash.plotly.com/ - Dash Documentation
2. https://dash.plotly.com/layout - Dash Layout (HTML Components)
3. https://dash.plotly.com/dash-core-components - Dash Core Components ( DatePickerRange, Checklist)
4. https://dash.plotly.com/dash-html-components - Dash HTML Components (Div, H1 , Iframe)
5. https://plotly.com/python/plotly-express/ - Plotly Express ( px.line, px.scatter, px.bar)
6. https://plotly.com/python/graph-objects/ - Plotly Graph Objects ( go.Scatter, go.Heatmap, go.Figure)
7. https://www.coursera.org/projects/interactive-dashboards-plotly-dash?tab=guided-projects - Coursera Project
"""

if __name__ == "__main__":
    app.run_server(debug=True)  # Start the Dash server in debug mode
