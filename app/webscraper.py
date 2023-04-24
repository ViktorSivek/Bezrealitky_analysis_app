import csv
import logging
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def configure_logging():
    # Set up the main logging configuration
    setup_logging_configuration()
    
    # Silence third-party logger output
    silence_third_party_loggers()


def setup_logging_configuration():
    # Create a log file and set logging format
    log_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(log_directory, "webscraper.log")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=log_file_path, filemode='a')
    
    # Add console handler for displaying logs in the console
    add_console_handler()


def add_console_handler():
    # Create and configure a console handler for logging
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)


def silence_third_party_loggers():
    # Set log levels for third-party loggers to suppress their output
    LOGGER.setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

class WebScraper:
    def __init__(self, driver, sleep_time=5):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30)
        self.listings_data = []
        self.sleep_time = sleep_time

        
    @classmethod
    def init_driver(cls, driver_path):
        # Configure Chrome options and create a new webdriver instance
        chrome_options = cls.configure_chrome_options()
        driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        return driver

    @staticmethod
    def configure_chrome_options():
        # Set up Chrome options for the webdriver
        chrome_options = Options()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-fonts")
        chrome_options.add_argument("--disable-popup-blocking")
        # chrome_options.add_argument("--headless")  # Disable view of browser
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
        
        return chrome_options

    def extract_info(self, url):
        """
        Extracts the required information from the given URL and returns the extracted data.

        Args:
            url (str): The URL to extract information from.

        Returns:
            dict: The extracted data, or None if an error occurred.
        """
        self.driver.get(url)
        logging.info(f"Visiting URL: {url}")

        try:
            data = self.extract_data(url)
            logging.info(f"Data extracted: {data}")
            return data
        except Exception as e:
            logging.error(f"An error occurred while scraping the page: {str(e)}")
            return None

    def extract_data(self, url):
        """
        Extracts and organizes data from the current page.

        Args:
            url (str): The URL to extract information from.

        Returns:
            dict: The extracted data.
        """
        data = {"URL": url}
        data.update(self.extract_basic_data())
        data.update(self.extract_table_data())
        data.update(self.extract_poi_data())
        return data

    def extract_basic_data(self):
        """
        Extracts basic data from the current page.

        Returns:
            dict: The extracted basic data.
        """
        data = {
            "LOKACE": self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/span/span[1]/span[2]/a'),
            "TYP NABÍDKY": self.try_extract_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/div[1]/nav/ol/li[3]/a'),
        }

        cena_xpath = '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div/div[1]/span[2]/strong'
        if data["TYP NABÍDKY"] != "PRODEJ":
            data["CENA"] = self.try_extract_element(By.XPATH, cena_xpath)
            data.update(self.extract_extra_data())
        else:
            data["CENA"] = self.try_extract_element(By.XPATH, cena_xpath)

        return data

    def extract_extra_data(self):
        """
        Extracts extra data from the current page when the listing type is not "PRODEJ".

        Returns:
            dict: The extracted extra data.
        """
        data = {}
        divs = self.driver.find_elements(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div/div')

        for div in divs:
            try:
                title_element = div.find_element(By.XPATH, './span[1]/span')
                value_element = div.find_element(By.XPATH, './span[2]/strong')
            except NoSuchElementException:
                continue

            title = title_element.text.strip().replace('\n', '').replace('+', '')
            value = value_element.text.strip().replace('\n', '')

            data[title] = value

        return data
    
    def extract_table_data(self):
        """
        Extracts table data from the current page.

        Returns:
            dict: The extracted table data.
        """
        data = {}
        parameters_area1 = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/div[4]/div')

        if parameters_area1:
            tables1 = self.driver.find_elements(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/div[4]/div/section')
            for table in tables1:
                rows = table.find_elements(By.TAG_NAME, 'tr')

                for row in rows:
                    try:
                        title = row.find_element(By.XPATH, './th').text.strip().replace('\n', '')  # Parameter's title
                    except:
                        title = "title"
                    try:
                        value = row.find_element(By.XPATH, './td').text.strip().replace('\n', '')  # Parameter's value
                    except:
                        value = row.find_element(By.XPATH, './td/div/a/span/span[1]').text.strip().replace('\n', '')  # Parameter's title

                    if title != "":
                        data[title] = value
                    else:
                        title = value
                        data[title] = 1

        return data
                
    def extract_poi_data(self):
        """
        Extracts points of interest (POI) data from the current page.

        Returns:
            dict: The extracted POI data.
        """
        data = {}
        parameters_area2 = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/section[1]/div/div[2]')

        if parameters_area2:
            tables3 = self.driver.find_elements(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/section[1]/div/div[2]/div[1]')

            for table in tables3:
                divs = table.find_elements(By.XPATH, './/div[@class="Poi_poiItem__o_ASS poiItem"]')

                for div in divs:
                    try:
                        title = div.find_element(By.XPATH, './/span[@class="Poi_poiItemContentType__N5P4D poiItemContentType"]').text.strip().replace('\n', '')  # Parameter's title
                        value_element = div.find_element(By.XPATH, './/div[@class="Poi_poiItemTimes__5AhQ0 poiItemTimes"]/strong')
                        value = value_element.text.strip().replace('\n', '').replace(u'\xa0', u' ')  # Parameter's value

                        data[title] = value
                    except:
                        continue

        return data
        
    def try_extract_element(self, by, locator):
        """
        Tries to extract an element's text from the page using the given locator.

        Args:
            by (By): The method to locate the element (e.g., By.XPATH, By.ID, etc.).
            locator (str): The locator to find the element.

        Returns:
            str: The element's text if found, or None if not found.
        """
        try:
            return self.wait.until(EC.presence_of_element_located((by, locator))).text
        except TimeoutException:
            logging.warning(f"Unable to find the element in locaiton '{locator}' on the page.")
            return None
        
    def save_to_csv(self, file_name):
        """
        Save the listings_data to a CSV file with a specified schema.

        Args:
        file_name (str): The name of the CSV file to save the data.

        Returns:
        combined_df (pd.DataFrame): The DataFrame containing the data saved to the CSV file.
        """

        # Convert the listings_data to a DataFrame
        df = pd.DataFrame(self.listings_data)

        # Add 'Index' column with range 1 to length of DataFrame
        df.insert(0, 'Index', range(1, len(df) + 1))

        # Define a dictionary to map old column names to new column names
        column_mapping = {
            'Balkón': 'Balkón',
            'Terasa': 'Terasa',
            'Sklep': 'Sklep',
            'Lodžie': 'Lodžie',
            'Bezbariérový přístup': 'Bezbariérový přístup',
            'Parkování': 'Parkování',
            'Výtah': 'Výtah',
            'Garáž': 'Garáž',
            'Poplatky za energie': 'POPLATKY ZA ENERGIE',
            'Poplatky za služby': 'POPLATKY ZA SLUŽBY',
            'Vratná kauce': 'VRATNÁ KAUCE'
        }

        # Rename the columns in the DataFrame using the dictionary
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns:
                df.rename(columns={old_col: new_col}, inplace=True)

        # Define the fixed schema with the columns to include
        columns = ['URL', 'CENA', 'POPLATKY ZA SLUŽBY', 'POPLATKY ZA ENERGIE', 'VRATNÁ KAUCE', 'TYP NABÍDKY', 'LOKACE', 'ČÍSLO INZERÁTU', 'DISPOZICE', 'STAV', 'DOSTUPNÉ OD', 'VLASTNICTVÍ', 'TYP BUDOVY', 'PLOCHA', 'VYBAVENO', 'PODLAŽÍ', 'PENB', 'Internet', 'Energie', 'Balkón', 'Terasa', 'Sklep', 'Lodžie', 'Bezbariérový přístup', 'Parkování', 'Výtah', 'Garáž', 'MHD', 'Pošta', 'Obchod', 'Banka', 'Restaurace', 'Lékárna', 'Škola', 'Mateřská škola', 'Sportoviště', 'Hřiště']  # List of column names
        fixed_schema_df = pd.DataFrame(columns=columns)
        fixed_schema_df.insert(0, 'Index', range(1, len(fixed_schema_df) + 1))

        # Reset the index for both DataFrames before concatenating
        fixed_schema_df.reset_index(drop=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        # Handle duplicate column names by adding suffixes
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols

        # Combine the DataFrames, filling missing values with 'NaN'
        combined_df = pd.concat([fixed_schema_df, df], axis=0, ignore_index=True, sort=False).fillna('NaN')[columns]

        # Reset index and add 'Index' column with range 1 to length of combined_df
        combined_df.reset_index(drop=True, inplace=True)
        combined_df.insert(0, 'Index', range(1, len(combined_df) + 1))

        # Save the data to a CSV file
        file_exists = os.path.isfile(file_name)
        with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=combined_df.columns)

            # Write the header if the file does not exist
            if not file_exists:
                writer.writeheader()

            # Write the data to the CSV file
            for _, row in combined_df.iterrows():
                writer.writerow(row.to_dict())

        return combined_df

    def accept_cookies(self):
        """
        Accept cookies on the website if the cookies banner is present.
        """
        try:
            # Find the 'accept cookies' button and click it
            accept_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']")))
            accept_button.click()
        except TimeoutException:
            logging.warning("Could not find the accept cookies button or it took too long to load.") 

    # def scrape_listings(self, url):
    #     main_url = url  # Store the main URL
    #     self.driver.get(main_url)
    #     self.accept_cookies()
    #     logging.info(f"Starting to scrape listings from {main_url}")

    #     page_counter = 1
    #     max_pages = 1

    #     while page_counter <= max_pages:
    #         time.sleep(self.sleep_time)
    #         listing_links = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/section/div/div[2]/div/div[5]/section/article//div[2]/h2')))

    #         try:
    #             urls = [link.find_element_by_css_selector('a').get_attribute("href") for link in listing_links]
    #         except NoSuchElementException as e: # Use specific exception
    #             logging.error(f"Error extracting listing URLs: {e}")

    #         for listing_url in urls:
    #             try:
    #                 listing_data = self.extract_info(listing_url)
    #                 if listing_data is not None:
    #                     self.listings_data.append(listing_data)
    #             except Exception as e:
    #                 logging.error(f"Error extracting data from {listing_url}: {e}")

    #         try:
    #             self.driver.get(main_url)  # Go back to the main URL after processing each listing
    #             link_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//li[@class='page-item']/a[@class='page-link'][span[contains(text(), 'Další')]]")))
    #             self.wait.until_not(EC.staleness_of(link_button))
    #             link_url = link_button.get_attribute("href")
    #             self.driver.get(link_url)
    #             main_url = link_url  # Update the main URL
    #             page_counter += 1
    #         except TimeoutException:
    #             logging.info("No more pages to scrape, exiting.")
    #             break

    #     logging.info(f"Web scraping completed. Collected {len(self.listings_data)} listings.")

    #     # Close the driver
    #     self.driver.quit()

    #     # Save the data to a CSV file
    #     # output = self.save_to_csv('listings_data.csv')

    #     data = self.listings_data

    #     return data

    def scrape_listings(self, url):
        """
        Scrape listing data from the given URL and return the data.

        Args:
            url (str): The URL to scrape listings from.

        Returns:
            list: A list of dictionaries containing the scraped listing data.
        """
        main_url = url  # Store the main URL
        self.driver.get(main_url)
        self.accept_cookies()
        logging.info(f"Starting to scrape listings from {main_url}")

        page_counter = 1
        max_pages = 1

        while page_counter <= max_pages:
            time.sleep(self.sleep_time)
            # Find all listing links on the current page
            listing_links = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/section/div/div[2]/div/div[5]/section/article//div[2]/h2')))

            try:
                # Extract URLs from the listing links
                urls = [link.find_element_by_css_selector('a').get_attribute("href") for link in listing_links]
            except NoSuchElementException as e:
                logging.error(f"Error extracting listing URLs: {e}")

            # Extract data from each listing URL
            for listing_url in urls:
                try:
                    listing_data = self.extract_info(listing_url)
                    if listing_data is not None:
                        self.listings_data.append(listing_data)
                except Exception as e:
                    logging.error(f"Error extracting data from {listing_url}: {e}")

            # Go to the next page of listings
            try:
                self.driver.get(main_url)  # Go back to the main URL after processing each listing
                # Find the 'next' button and click it
                link_button = self.wait.until(EC.presence_of_element_located((By.XPATH, "//li[@class='page-item']/a[@class='page-link'][span[contains(text(), 'Další')]]")))
                self.wait.until_not(EC.staleness_of(link_button))
                link_url = link_button.get_attribute("href")
                self.driver.get(link_url)
                main_url = link_url  # Update the main URL
                page_counter += 1
            except TimeoutException:
                logging.info("No more pages to scrape, exiting.")
                break

        logging.info(f"Web scraping completed. Collected {len(self.listings_data)} listings.")

        # Close the driver
        self.driver.quit()

        data = self.listings_data

        return data

