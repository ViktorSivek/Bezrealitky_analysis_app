import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
from webscraper import WebScraper, configure_logging
from datahandler import DataHandler
from dashapp import DashApp
import threading

# Define constants
chrome_driver_path = 'D:/chdriver/chromedriver.exe'
url = "https://www.bezrealitky.cz/vypis/nabidka-pronajem"
csv_file = 'listings_data.csv'

def start_scraping():
    """
    Function to start the scraping process.
    """
    configure_logging()
    main_driver = WebScraper.init_driver(chrome_driver_path)
    scraper = WebScraper(main_driver)
    listings_data = scraper.scrape_listings(url)
    print("Scraped listings data:")
    print(listings_data)

def load_data():
    """
    Function to load listings data from a CSV file or scrape it if the file doesn't exist.

    Returns:
        listings_data (pd.DataFrame): DataFrame containing the listings data.
    """
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

def main():
    """
    The main function that loads data, cleans it, analyzes it, and starts the Dash app.
    """
    # Load data
    df = load_data()

    # Clean and analyze data
    data_handler = DataHandler(df)  # Pass the loaded DataFrame instead of the CSV file name
    cleaned_df = data_handler.clean_data()
    lin_reg_rent, imputer, encoder = data_handler.analyze_data(cleaned_df)

    # Start the Dash app
    dash_app = DashApp(cleaned_df, encoder, imputer, lin_reg_rent)
    dash_app.run(debug=True)

if __name__ == "__main__":
    main()
