import pandas as pd

class DataHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    def clean_data(self, df):
        # Perform data cleaning tasks here
        # For example, you can remove duplicates, fill missing values, etc.
        
        # Remove duplicates
        df.drop_duplicates(inplace=True)

        # Fill missing values
        df.fillna('Unknown', inplace=True)

        # Perform other data cleaning tasks as needed

        return df

    def analyze_data(self, df):
        # Perform data analysis tasks here
        # For example, you can compute average price, count property types, etc.

        # Compute average price
        average_price = df['CENA'].mean()

        # Count property types
        property_type_counts = df['TYP NABÍDKY'].value_counts()

        # Perform other data analysis tasks as needed

        return average_price, property_type_counts
