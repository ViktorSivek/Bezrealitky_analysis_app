import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from webscraper import WebScraper, configure_logging
from datahandler import DataHandler
import threading

chrome_driver_path = 'C:/Users/vsivek001/driver/chromedriver.exe'
url = "https://www.bezrealitky.cz/vypis/nabidka-pronajem/byt?page=151"
csv_file = 'listings_data.csv'

# Function to start the scraping process
def start_scraping():
    configure_logging()
    main_driver = WebScraper.init_driver(chrome_driver_path)
    scraper = WebScraper(main_driver)
    listings_data = scraper.scrape_listings(url)
    
    print("LLLLLLLLLLIIIIIIIIIISSSSSSSSTTTTTTTTTIIIIIIIIIIIINNNNNNNNNGGGGGGGGGGGG")
    print(listings_data)

# Function to start the scraping process and load data
def load_data():
    if not os.path.isfile(csv_file):
        configure_logging()
        main_driver = WebScraper.init_driver(chrome_driver_path)
        scraper = WebScraper(main_driver)
        listings_data = scraper.scrape_listings(url)
        
        # Save scraped data to the CSV file
        scraper.save_to_csv(csv_file)
        listings_data = pd.read_csv(csv_file)
    else:
        listings_data = pd.read_csv(csv_file)

    return listings_data

df = load_data()
data_handler = DataHandler(csv_file)
cleaned_df = data_handler.clean_data(df)
analysis_results = data_handler.analyze_data(cleaned_df)

# # Load data from CSV
# if os.path.exists(csv_file):
#     df = pd.read_csv(csv_file)
# else:
#     print(f"File not found: {csv_file}")

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1(children='Title of Dash App', style={'textAlign': 'center'}),

    html.Div([
        html.Label("X-axis:"),
        dcc.Dropdown(
            id='xaxis-selection',
            options=[{'label': i, 'value': i} for i in cleaned_df.columns],
            value=cleaned_df.columns[0]
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    html.Div([
        html.Label("Y-axis:"),
        dcc.Dropdown(
            id='yaxis-selection',
            options=[{'label': i, 'value': i} for i in cleaned_df.columns],
            value=cleaned_df.columns[1]
        ),
    ], style={'width': '48%', 'display': 'inline-block'}),

    dcc.Graph(id='graph-content'),

    # Add new visualizations here
    html.H2("Number of Properties by Building Type", style={'textAlign': 'center'}),
    dcc.Graph(id='bar-chart'),

    html.H2("Correlation Heatmap", style={'textAlign': 'center'}),
    dcc.Graph(id='heatmap'),

    html.H2("Distribution of Property Layouts", style={'textAlign': 'center'}),
    dcc.Graph(id='pie-chart'),

    html.H2("Area Distribution (Box plot)", style={'textAlign': 'center'}),
    dcc.Graph(id='box-plot'),

    html.H2("Area Distribution (Histogram)", style={'textAlign': 'center'}),
    dcc.Graph(id='histogram'),

    html.Button("Update Visualizations", id="update-visualizations"),
])

# Update the graph based on the selected column
@app.callback(
    Output('graph-content', 'figure'),
    Input('xaxis-selection', 'value'),
    Input('yaxis-selection', 'value')
)
def update_graph(x_value, y_value):
    return px.scatter(cleaned_df, x=x_value, y=y_value)

# Create a new column with numeric area values
# cleaned_df['PLOCHA_NUM'] = cleaned_df['PLOCHA'].str.extract('(\d+)').astype(float)
# cleaned_df['CENA_NUM'] = cleaned_df['CENA'].str.replace(' ', '').str.extract('(\d+)').astype(float)
cleaned_df['PLOCHA_NUM'] = cleaned_df['PLOCHA']
cleaned_df['CENA_NUM'] = cleaned_df['CENA']

# Create new visualizations
fig_bar = px.bar(cleaned_df.groupby('TYP BUDOVY').size().reset_index(name='count'), x='TYP BUDOVY', y='count')
# fig_heatmap = px.imshow(cleaned_df[['PLOCHA_NUM', 'PODLAŽÍ', 'CENA_NUM']].astype(float).corr())
fig_pie = px.pie(cleaned_df, names='DISPOZICE')
fig_box = px.box(cleaned_df, y='PLOCHA_NUM')
fig_histogram = px.histogram(cleaned_df, x='PLOCHA_NUM', nbins=20)

# Update the new visualizations
@app.callback(
    Output('bar-chart', 'figure'),
    # Output('heatmap', 'figure'),
    Output('pie-chart', 'figure'),
    Output('box-plot', 'figure'),
    Output('histogram', 'figure'),
    Input('update-visualizations', 'n_clicks')  # Add a new input for the update function
)
def update_new_visualizations(n_clicks=None):
    return fig_bar, fig_pie, fig_box, fig_histogram

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)