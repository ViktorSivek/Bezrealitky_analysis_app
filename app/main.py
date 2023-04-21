import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from webscraper import WebScraper, configure_logging
import threading

chrome_driver_path = 'D:/chdriver/chromedriver.exe'
url = "https://www.bezrealitky.cz/vypis/nabidka-prodej/byt"
csv_file = 'listings_data.csv'

# Function to start the scraping process
def start_scraping():
    configure_logging()
    main_driver = WebScraper.init_driver(chrome_driver_path)
    scraper = WebScraper(main_driver)
    listings_data = scraper.scrape_listings(url)

# If the CSV file doesn't exist, start the scraping process in a separate thread
if not os.path.isfile(csv_file):
    scrape_thread = threading.Thread(target=start_scraping)
    scrape_thread.start()
    scrape_thread.join()  # Wait for the scraping process to complete

# Load data from CSV
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    print(f"File not found: {csv_file}")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),
    html.Div([
        html.Label("X-axis:"),
        dcc.Dropdown(
            id='xaxis-selection',
            options=[{'label': i, 'value': i} for i in df.columns],
            value=df.columns[0]
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Y-axis:"),
        dcc.Dropdown(
            id='yaxis-selection',
            options=[{'label': i, 'value': i} for i in df.columns],
            value=df.columns[1]
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    dcc.Graph(id='graph-content')
])

# Update the graph based on the selected column
@app.callback(
    Output('graph-content', 'figure'),
    Input('xaxis-selection', 'value'),
    Input('yaxis-selection', 'value')
)
def update_graph(x_value, y_value):
    return px.scatter(df, x=x_value, y=y_value)

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)