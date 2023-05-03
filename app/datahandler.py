import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder

class DataHandler:
    def __init__(self, df):
        self.df = df

    def clean_data(self):
        """
        Args:
            df (pd.DataFrame): The input DataFrame to clean.

        Returns:
            pd.DataFrame: The cleaned DataFrame.
        """
        df = self.df


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

        # Drop the columns
        df.drop(labels='URL', axis=1, inplace=True)
        df = df.drop(labels='Index', axis=1)
        df = df.drop(labels='ČÍSLO INZERÁTU', axis=1)
        df = df.drop(labels='DOSTUPNÉ OD', axis=1)

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

        # df['DOSTUPNÉ OD'] = pd.to_datetime(df['DOSTUPNÉ OD'], format='%d. %m. %Y', errors='coerce')

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
        columns_to_replace = ['VLASTNICTVÍ', 'TYP BUDOVY', 'PLOCHA',
                            'VYBAVENO', 'PODLAŽÍ', 'PENB']

        for col in columns_to_replace:
            df[col].fillna(value='unknown', inplace=True)

        cols_distance = ['MHD', 'Pošta', 'Obchod', 'Banka', 'Restaurace', 'Lékárna',
                        'Škola', 'Mateřská škola', 'Sportoviště', 'Hřiště']

        for col in cols_distance:
            df[col].fillna(value='unknown', inplace=True)

        # Remove non-digit characters and extra spaces, then convert the 'PLOCHA' column to int data type
        df['PLOCHA'] = df['PLOCHA'].replace('[^\d]', '', regex=True).astype(int)

        # Replace 'unknown' values with np.nan
        df = df.replace('unknown', np.nan)

        # Fill missing values with the mean value of the corresponding column
        df = df.fillna('0') 



    def analyze_data(self, df):
        # List of categorical columns
        cat_cols = ['TYP NABÍDKY', 'LOKACE', 'DISPOZICE', 'STAV', 'VLASTNICTVÍ', 'TYP BUDOVY', 'VYBAVENO', 'PENB']

        # Filter data and split into features and target
        print("Unique values in TYP NABÍDKY column:", df['TYP NABÍDKY'].unique())
        df_rent = df[df['TYP NABÍDKY'] == 'PRONÁJEM']
        df_rent = df_rent.copy()
        df_rent.drop(['TYP NABÍDKY'], axis=1, inplace=True)

        # One-hot encode the categorical columns
        df_rent = pd.get_dummies(df_rent, columns=['LOKACE', 'DISPOZICE', 'STAV'], prefix=['LOKALITA', 'DISPOZICE', 'STAV'])

        print("df_rent shape:", df_rent.shape)
        print("df_rent head:\n", df_rent.head())

        X_rent = df_rent.drop('CENA', axis=1)
        Y_rent = df_rent['CENA']

        print("X_rent shape:", X_rent.shape)
        print("X_rent head:\n", X_rent.head())

        # Select only numeric columns
        X_rent_numeric = X_rent.select_dtypes(include=np.number)

        # Create an instance of the SimpleImputer
        imputer = SimpleImputer(missing_values=np.nan, strategy='mean')

        # Impute the numeric dataset
        X_rent_imputed = imputer.fit_transform(X_rent_numeric)

        # Split the data into training and test sets
        x_rent_train, x_rent_test, y_rent_train, y_rent_test = train_test_split(X_rent_imputed, Y_rent, test_size=0.2, random_state=12)

        # Model training
        # --------------
        # Fit the linear regression model using the imputed data
        lin_reg_rent = LinearRegression()
        lin_reg_rent.fit(x_rent_train, y_rent_train)

        # Model evaluation
        # ----------------
        # Make predictions on the test data
        y_rent_prediction = lin_reg_rent.predict(x_rent_test)

        # Print the evaluation metrics for the model
        self.printRegMetrics(y_rent_test, y_rent_prediction)

        # Calculate and print the adjusted R2 score using the imputed dataset
        adjusted_r2 = 1 - (1 - lin_reg_rent.score(X_rent_imputed, Y_rent)) * (len(Y_rent) - 1) / (len(Y_rent) - X_rent_numeric.shape[1] - 1)
        print(f"Adjusted R2 score: {adjusted_r2}")

        # Perform 5-fold cross-validation to get the cross-validated R2 scores
        cv_r2_scores = cross_val_score(lin_reg_rent, X_rent_imputed, Y_rent, cv=5, scoring='r2')

        # Calculate the mean R2 score from the cross-validated R2 scores
        mean_cv_r2_score = np.mean(cv_r2_scores)

        # Print the mean R2 score
        print(f"Mean R2 score based on 5-fold cross-validation: {mean_cv_r2_score:.3f} ({mean_cv_r2_score*100:.0f}%)")

        return lin_reg_rent, imputer, X_rent.columns

    
    def printRegMetrics(self, y_test: pd.Series, y_pred: np.ndarray) -> None:
        """
        Prints out basic evaluation metrics of regression models.
        """
        
        score = r2_score(y_test, y_pred)
        
        print(f'R2 -------------------------- {round(score, 3)} ({int(round(score * 100, 0))} %)')
        print(f'Mean squared error ---------- {round(mean_squared_error(y_test, y_pred), 1)}')
        print(f'Root mean squared error ----- {round(np.sqrt(mean_squared_error(y_test, y_pred)), 1)}')
