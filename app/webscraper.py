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
    log_directory = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(log_directory, "webscraper.log")
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='a')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)
    LOGGER.setLevel(logging.WARNING)
    logging.getLogger("selenium").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

class WebScraper:
    def __init__(self, driver, sleep_time=5):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30)
        self.listings_data = []
        self.sleep_time = sleep_time

    def init_driver(driver_path):
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
        # chrome_options.add_argument("--headless")  Disable view of browser
        chrome_options.add_argument("--disable-images")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")

        driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)
        return driver

    def extract_info(self, url):
        """Extracts the required information from the given URL."""
        self.driver.get(url)

        logging.info(f"Visiting URL: {url}")

        try:
            data = {}

            data["URL"] = url
            data["LOKACE"] = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/span/span[1]/span[2]/a')
            data["TYP NABÍDKY"] = self.try_extract_element(By.XPATH, '//*[@id="__next"]/main/div[1]/div/div[1]/nav/ol/li[3]/a')
            
            if data["TYP NABÍDKY"] != "PRODEJ":
                
                
                try:
                    data["CENA"] = self.try_extract_element(By.XPATH, '/html/body/div[3]/main/div[2]/section/div/div[2]/div/div/div[1]/div/div[1]/span[2]/strong')
                    divs = table.find_elements(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div')
                    for div in divs:
                        try:
                            title = div.find_element(By.XPATH, 'div[2]/span[1]/span').text.strip().replace('\n', '').replace('+', '')  # Parameter's title
                            value_element = div.find_element(By.XPATH, 'span[2]/strong')
                            value = value_element.text.strip().replace('\n', '').replace(u'\xa0', u' ')  # Parameter's value

                            data.update({title: value})  # Add title:value to listing details
                        except:
                            continue
                    # data["POPLATKY ZA SLUŽBY"] = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div/div[2]/span[2]/strong')
                    # data["POPLATKY ZA ENERGII"] = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div/div[3]/span[2]/strong')
                    # data["VRATNÁ KAUCE"] = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div/div[4]/span[2]/strong')
                except:
                    data["CENA"] = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[2]/div/div/div[1]/div/span[2]/strong')
            else:
                pass

            parameters_area1 = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/div[4]/div')
            parameters_area2 = self.try_extract_element(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/section[1]/div/div[2]')

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
                            data.update({title: value})  # Add title:value to listing details
                        else:
                            title = value
                            data.update({title: 1})  # Add title:value to listing details

            if parameters_area2:
                tables3 = self.driver.find_elements(By.XPATH, '/html/body/div[1]/main/div[2]/section/div/div[1]/section[1]/div/div[2]/div[1]')

                for table in tables3:
                    divs = table.find_elements(By.XPATH, './/div[@class="Poi_poiItem__o_ASS poiItem"]')

                    for div in divs:
                        try:
                            title = div.find_element(By.XPATH, './/span[@class="Poi_poiItemContentType__N5P4D poiItemContentType"]').text.strip().replace('\n', '')  # Parameter's title
                            value_element = div.find_element(By.XPATH, './/div[@class="Poi_poiItemTimes__5AhQ0 poiItemTimes"]/strong')
                            value = value_element.text.strip().replace('\n', '').replace(u'\xa0', u' ')  # Parameter's value

                            data.update({title: value})  # Add title:value to listing details
                        except:
                            continue


            logging.info(f"Data extracted: {data}")

            return data
        except Exception as e:
            logging.error(f"An error occurred while scraping the page: {str(e)}")
            return None
        
    def try_extract_element(self, by, locator):
        try:
            return self.wait.until(EC.presence_of_element_located((by, locator))).text
        except TimeoutException:
            logging.warning(f"Unable to find the element in locaiton '{locator}' on the page.")
            return None

    def save_to_csv(self, file_name):
        df = pd.DataFrame(self.listings_data)
        df.insert(0, 'Index', range(1, len(df) + 1))

        # Rename columns that contain 'URL' to 'URL'
        for col in df.columns:
            if 'Balkón' in col:
                df.rename(columns={col: 'Balkón'}, inplace=True)
            if 'Terasa' in col:
                df.rename(columns={col: 'Terasa'}, inplace=True)
            if 'Sklep' in col:
                df.rename(columns={col: 'Sklep'}, inplace=True)
            if 'Lodžie' in col:
                df.rename(columns={col: 'Lodžie'}, inplace=True)
            if 'Bezbariérový přístup' in col:
                df.rename(columns={col: 'Bezbariérový přístup'}, inplace=True)
            if 'Parkování' in col:
                df.rename(columns={col: 'Parkování'}, inplace=True)
            if 'Výtah' in col:
                df.rename(columns={col: 'Výtah'}, inplace=True)
            if 'Garáž' in col:
                df.rename(columns={col: 'Garáž'}, inplace=True)
            if 'Poplatky za služby' in col:
                df.rename(columns={col: 'POPLATKY ZA SLUŽBY'}, inplace=True)
            if 'Poplatky za energii' in col:
                df.rename(columns={col: 'POPLATKY ZA ENERGII'}, inplace=True)
            if 'Vratná kauce' in col:
                df.rename(columns={col: 'VRATNÁ KAUCE'}, inplace=True)


        # Define the fixed schema with the columns you want to include
        columns = ['URL', 'CENA', 'POPLATKY ZA SLUŽBY', 'POPLATKY ZA ENERGII', 'VRATNÁ KAUCE', 'TYP NABÍDKY', 'LOKACE', 'ČÍSLO INZERÁTU', 'DISPOZICE', 'STAV', 'DOSTUPNÉ OD', 'VLASTNICTVÍ', 'TYP BUDOVY', 'PLOCHA', 'VYBAVENO', 'PODLAŽÍ', 'PENB', 'Internet', 'Energie', 'Balkón', 'Terasa', 'Sklep', 'Lodžie', 'Bezbariérový přístup', 'Parkování', 'Výtah', 'Garáž', 'MHD', 'Pošta', 'Obchod', 'Banka', 'Restaurace', 'Lékárna', 'Škola', 'Mateřská škola', 'Sportoviště', 'Hřiště']
        fixed_schema_df = pd.DataFrame(columns=columns)
        fixed_schema_df.insert(0, 'Index', range(1, len(fixed_schema_df) + 1))

        # Reset the index for both DataFrames before concatenating
        fixed_schema_df.reset_index(drop=True, inplace=True)
        df.reset_index(drop=True, inplace=True)

        print("fixed_schema_df:")
        print(fixed_schema_df.head())
        print(fixed_schema_df.info())

        print("df:")
        print(df.head())
        print(df.info())

        # Merge the scraped DataFrame into the fixed schema DataFrame, filling missing values with 'NaN'
        # combined_df = pd.concat([fixed_schema_df, df], axis=0, ignore_index=True, sort=False).fillna('NaN')[columns]
        # combined_df = pd.concat([fixed_schema_df.reset_index(drop=True), df.reset_index(drop=True)], axis=0, ignore_index=True, sort=False).fillna('NaN')[columns]
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index.values.tolist()] = [dup + '_' + str(i) if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols
        combined_df = pd.concat([fixed_schema_df, df], axis=0, ignore_index=True, sort=False).fillna('NaN')[columns]




        # Add the 'Index' column with a range of values from 1 to the length of the DataFrame
        combined_df.reset_index(drop=True, inplace=True)
        combined_df.insert(0, 'Index', range(1, len(combined_df) + 1))

        # Save the data to a CSV file
        file_exists = os.path.isfile(file_name)
        with open(file_name, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=combined_df.columns)

            if not file_exists:
                writer.writeheader()

            for _, row in combined_df.iterrows():
                writer.writerow(row.to_dict())

        return combined_df

    def accept_cookies(self):
        try:
            accept_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@id='CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll']")))
            accept_button.click()
        except TimeoutException:
            logging.warning("Could not find the accept cookies button or it took too long to load.")
    


    def scrape_listings(self, url):
        main_url = url  # Store the main URL
        self.driver.get(main_url)
        self.accept_cookies()
        logging.info(f"Starting to scrape listings from {main_url}")

        page_counter = 1
        max_pages = 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 

        while page_counter <= max_pages:
            time.sleep(self.sleep_time)
            listing_links = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//*[@id="__next"]/main/section/div/div[2]/div/div[5]/section/article//div[2]/h2')))

            try:
                urls = [link.find_element_by_css_selector('a').get_attribute("href") for link in listing_links]
            except NoSuchElementException as e: # Use specific exception
                logging.error(f"Error extracting listing URLs: {e}")

            for listing_url in urls:
                try:
                    listing_data = self.extract_info(listing_url)
                    if listing_data is not None:
                        self.listings_data.append(listing_data)
                except Exception as e:
                    logging.error(f"Error extracting data from {listing_url}: {e}")

            try:
                self.driver.get(main_url)  # Go back to the main URL after processing each listing
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

        # Save the data to a CSV file
        output = self.save_to_csv('listings_data.csv')

        data_row = self.listings_data

        return output

