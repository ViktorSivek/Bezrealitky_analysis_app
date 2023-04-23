import pandas as pd

class DataHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    

    def clean_data(self, df):

        # Remove duplicate rows based on the 'URL' column
        df.drop_duplicates(subset=['URL'], inplace=True)

        # Drop columns with all NaN values
        df.dropna(axis=1, how='all', inplace=True)

        # Drop the 'URL' column
        df = df.drop(labels='URL', axis=1)

        # Standardize location names
        locations = [
            ('Praha', 'Praha'),
            ('Moravskoslezský kraj', 'Moravskoslezský kraj'),
            ('Ústecký kraj', 'Ústecký kraj'),
            ('Pardubický kraj', 'Praha'),
            ('Jihomoravský kraj', 'Jihomoravský kraj'),
            ('Olomoucký kraj', 'Olomoucký kraj'),
            ('Liberecký kraj', 'Liberecký kraj'),
            ('Středočeský kraj', 'Středočeský kraj'),
            ('Bratislavský kraj', 'Bratislavský kraj'),
            ('Plzeňský kraj', 'Plzeňský kraj'),
            ('Královéhradecký kraj', 'Královéhradecký kraj'),
            ('Karlovarský kraj', 'Karlovarský kraj'),
            ('kraj Vysočina', 'kraj Vysočina'),
            ('Zlínský kraj', 'Zlínský kraj'),
            ('Jihočeský kraj', 'Jihočeský kraj')
        ]

        for old_name, new_name in locations:
            df.loc[df['LOKACE'].str.contains(old_name, case=False), 'LOKACE'] = new_name

        # Drop rows where 'LOKACE' is not in the location_values list
        df = df[df['LOKACE'].isin([new_name for _, new_name in locations])]

        # Convert columns to appropriate data types
        df['CENA'] = df['CENA'].replace('[^\d]', '', regex=True).astype(int)
        df['POPLATKY ZA SLUŽBY'] = df['POPLATKY ZA SLUŽBY'].replace('[^\d]', '', regex=True).fillna(0).astype(int)
        df['POPLATKY ZA ENERGIE'] = df['POPLATKY ZA ENERGIE'].replace('[^\d]', '', regex=True).fillna(0).astype(int)
        df['VRATNÁ KAUCE'] = df['VRATNÁ KAUCE'].replace('[^\d]', '', regex=True).fillna(0).astype(int)

        cols_boolean = ['Internet', 'Energie', 'Balkón', 'Terasa', 'Sklep', 'Lodžie',
                        'Bezbariérový přístup', 'Parkování', 'Výtah', 'Garáž']
        existing_cols_boolean = [col for col in cols_boolean if col in df.columns]
        df[existing_cols_boolean] = df[existing_cols_boolean].fillna(value=0).astype(int)

        # cols_boolean = ['Internet', 'Energie', 'Balkón', 'Terasa', 'Sklep', 'Lodžie',
        #                 'Bezbariérový přístup', 'Parkování', 'Výtah', 'Garáž']
        # existing_cols_boolean = [col for col in cols_boolean if col in df.columns]
        # df[existing_cols_boolean] = df[existing_cols_boolean].fillna(value=0).astype(int)
        # df[cols_boolean] = df[cols_boolean].fillna(value=0).astype(int)

        df['DOSTUPNÉ OD'] = pd.to_datetime(df['DOSTUPNÉ OD'], format='%d. %m. %Y', errors='coerce')

        cols_distance = ['MHD', 'Pošta', 'Obchod', 'Banka', 'Restaurace', 'Lékárna',
                        'Škola', 'Mateřská škola', 'Sportoviště', 'Hřiště']
        df[cols_distance] = df[cols_distance].applymap(lambda x: int(x.replace('m', '').replace(' ', '')) if pd.notna(x) else x)

        df = df.dropna(subset=['STAV'])

        # Replace NaN values with 'unknown' in specific columns
        columns_to_replace = ['DOSTUPNÉ OD', 'VLASTNICTVÍ', 'TYP BUDOVY', 'PLOCHA',
                            'VYBAVENO', 'PODLAŽÍ', 'PENB']

        for col in columns_to_replace:
            df[col].fillna(value='unknown', inplace=True)

        for col in cols_distance:
            df[col].fillna(value='unknown', inplace=True)

        # Remove non-digit characters and extra spaces, then convert the 'PLOCHA' column to int data type
        df['PLOCHA'] = df['PLOCHA'].replace('[^\d]', '', regex=True).astype(int)

        print("Cleaned DataFrame:")
        # print(df.head(n=10).to_string(index=False, justify='center')) # head method to print only the first 10 rows
        print(df.head())
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
