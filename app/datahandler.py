import pandas as pd

class DataHandler:
    def __init__(self, file_name):
        self.file_name = file_name

    def clean_data(self, df):
        """
        Args:
            df (pd.DataFrame): The input DataFrame to clean.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """

        # Remove duplicate rows
        self._remove_duplicates(df)

        # Drop unnecessary columns
        self._drop_unneeded_columns(df)

        # Standardize location names
        self._standardize_location_names(df)

        # Convert columns to appropriate data types
        self._convert_columns_to_appropriate_data_types(df)

        # Fill NaN values and clean column values
        self._fill_na_and_clean_columns(df)

        print("Cleaned DataFrame:")
        print(df.head())
        return df
    
    def _remove_duplicates(self, df):
        """
        Args:
            df (pd.DataFrame): The input DataFrame to remove duplicates from.
        """
        # Remove duplicate rows based on the 'URL' column
        df.drop_duplicates(subset=['URL'], inplace=True)

    def _drop_unneeded_columns(self, df):
        """
        Args:
            df (pd.DataFrame): The input DataFrame to drop unneeded columns from.
        """
        # Drop columns with all NaN values
        df.dropna(axis=1, how='all', inplace=True)

        # Drop the 'URL' column
        df.drop(labels='URL', axis=1, inplace=True)

    def _standardize_location_names(self, df):
        """
        Args:
            df (pd.DataFrame): The input DataFrame to standardize location names in.
        """
        # Define the list of locations for standardization
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

        # Drop NaN values in the 'LOKACE' column
        df.dropna(subset=['LOKACE'], inplace=True)

        for old_name, new_name in locations:
            df.loc[df['LOKACE'].str.contains(old_name, case=False), 'LOKACE'] = new_name

        # Drop rows where 'LOKACE' is not in the location_values list
        df = df[df['LOKACE'].isin([new_name for _, new_name in locations])]

    def _convert_columns_to_appropriate_data_types(self, df):
        """
        Args:
            df (pd.DataFrame): The input DataFrame to convert columns to appropriate data types in.
        """
        df.dropna(subset=['CENA'], inplace=True)
        df['CENA'] = df['CENA'].replace('[^\d]', '', regex=True).astype(int)

        # Replace and convert other columns if present
        if 'POPLATKY ZA SLUŽBY' in df.columns:
            df['POPLATKY ZA SLUŽBY'] = df['POPLATKY ZA SLUŽBY'].replace('[^\d]', '', regex=True).fillna(0).astype(int)
        if 'POPLATKY ZA ENERGIE' in df.columns:
            df['POPLATKY ZA ENERGIE'] = df['POPLATKY ZA ENERGIE'].replace('[^\d]', '', regex=True).fillna(0).astype(int)
        if 'VRATNÁ KAUCE' in df.columns:
            df['VRATNÁ KAUCE'] = df['VRATNÁ KAUCE'].replace('[^\d]', '', regex=True).fillna(0).astype(int)

        cols_boolean = ['Internet', 'Energie', 'Balkón', 'Terasa', 'Sklep', 'Lodžie',
                        'Bezbariérový přístup', 'Parkování', 'Výtah', 'Garáž']
        existing_cols_boolean = [col for col in cols_boolean if col in df.columns]
        df[existing_cols_boolean] = df[existing_cols_boolean].fillna(value=0).astype(int)

        df['DOSTUPNÉ OD'] = pd.to_datetime(df['DOSTUPNÉ OD'], format='%d. %m. %Y', errors='coerce')

        cols_distance = ['MHD', 'Pošta', 'Obchod', 'Banka', 'Restaurace', 'Lékárna',
                        'Škola', 'Mateřská škola', 'Sportoviště', 'Hřiště']
        df[cols_distance] = df[cols_distance].applymap(lambda x: int(x.replace('m', '').replace(' ', '')) if pd.notna(x) else x)
        
    def _fill_na_and_clean_columns(self, df):
        """
        Args:
            df (pd.DataFrame): The input DataFrame fill na values and clean columns in.
        """
        df.dropna(subset=['STAV'], inplace=True)

        # Replace NaN values with 'unknown' in specific columns
        columns_to_replace = ['DOSTUPNÉ OD', 'VLASTNICTVÍ', 'TYP BUDOVY', 'PLOCHA',
                            'VYBAVENO', 'PODLAŽÍ', 'PENB']

        for col in columns_to_replace:
            df[col].fillna(value='unknown', inplace=True)

        cols_distance = ['MHD', 'Pošta', 'Obchod', 'Banka', 'Restaurace', 'Lékárna',
                        'Škola', 'Mateřská škola', 'Sportoviště', 'Hřiště']

        for col in cols_distance:
            df[col].fillna(value='unknown', inplace=True)

        # Remove non-digit characters and extra spaces, then convert the 'PLOCHA' column to int data type
        df['PLOCHA'] = df['PLOCHA'].replace('[^\d]', '', regex=True).astype(int)



    def analyze_data(self, df):
        # Perform data analysis tasks here

        return df
