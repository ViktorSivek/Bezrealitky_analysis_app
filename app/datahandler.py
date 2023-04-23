import pandas as pd

class DataHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    

    def clean_data(self, df):
        # For example, you can remove duplicates, fill missing values, etc.
        df.drop_duplicates(subset=['URL'], inplace=True)
        df.dropna(axis=1, how='all', inplace=True)
        df = df.drop(labels='URL', axis=1)

        # Rename locaiton
        df.loc[df['LOKACE'].str.contains('Praha', case=False), 'LOKACE'] = 'Praha'
        df.loc[df['LOKACE'].str.contains('Moravskoslezský kraj', case=False), 'LOKACE'] = 'Moravskoslezský kraj'
        df.loc[df['LOKACE'].str.contains('Ústecký kraj', case=False), 'LOKACE'] = 'Ústecký kraj'
        df.loc[df['LOKACE'].str.contains('Pardubický kraj', case=False), 'LOKACE'] = 'Praha'
        df.loc[df['LOKACE'].str.contains('Jihomoravský kraj', case=False), 'LOKACE'] = 'Jihomoravský kraj'
        df.loc[df['LOKACE'].str.contains('Olomoucký kraj', case=False), 'LOKACE'] = 'Olomoucký kraj'
        df.loc[df['LOKACE'].str.contains('Liberecký kraj', case=False), 'LOKACE'] = 'Liberecký kraj'
        df.loc[df['LOKACE'].str.contains('Středočeský kraj', case=False), 'LOKACE'] = 'Středočeský kraj'
        df.loc[df['LOKACE'].str.contains('Bratislavský kraj', case=False), 'LOKACE'] = 'Bratislavský kraj'
        df.loc[df['LOKACE'].str.contains('Plzeňský kraj', case=False), 'LOKACE'] = 'Plzeňský kraj'
        df.loc[df['LOKACE'].str.contains('Královéhradecký kraj', case=False), 'LOKACE'] = 'Královéhradecký kraj'
        df.loc[df['LOKACE'].str.contains('Karlovarský kraj', case=False), 'LOKACE'] = 'Karlovarský kraj'
        df.loc[df['LOKACE'].str.contains('kraj Vysočina', case=False), 'LOKACE'] = 'kraj Vysočina'
        df.loc[df['LOKACE'].str.contains('Zlínský kraj', case=False), 'LOKACE'] = 'Zlínský kraj'
        df.loc[df['LOKACE'].str.contains('Jihočeský kraj', case=False), 'LOKACE'] = 'Jihočeský kraj'
        df.loc[df['LOKACE'].str.contains('Zlínský kraj', case=False), 'LOKACE'] = 'Zlínský kraj'


        # df.drop_duplicates(inplace=True)

        # # Fill missing values
        # df.fillna('Unknown', inplace=True)

        # Perform other data cleaning tasks as needed

        print("Cleaned DataFrame:")
        print(df.head(n=10).to_string(index=False, justify='center')) # head method to print only the first 10 rows
        return df

    def analyze_data(self, df):
        # Perform data analysis tasks here
        # For example, you can compute average price, count property types, etc.

        # Compute average price
        # average_price = df['CENA'].mean()

        # # Count property types
        # property_type_counts = df['TYP NABÍDKY'].value_counts()

        # Perform other data analysis tasks as needed

        return df
