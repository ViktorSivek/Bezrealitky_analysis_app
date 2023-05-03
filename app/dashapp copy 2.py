# dashapp.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.impute import SimpleImputer

class DashApp:
    def __init__(self, cleaned_df, lin_reg_rent: LinearRegression, imputer: SimpleImputer):
        self.cleaned_df = cleaned_df
        self.lin_reg_rent = lin_reg_rent
        self.imputer = imputer
        self.app = dash.Dash(__name__)
        self.layout = self.create_layout()
        self.app.layout = self.layout
        self.set_callbacks()


    def load_model(self, model_file):
        with open(model_file, 'rb') as file:
            model = pickle.load(file)
        return model

    def create_dropdown(self, id, label, options, value):
        return html.Div([
            html.Label(label),
            dcc.Dropdown(
                id=id,
                options=[{'label': i, 'value': i} for i in options],
                value=value
            ),
        ], style={'width': '48%', 'display': 'inline-block'})
    
    def create_visualization(self, title, id):
        return html.Div([
            html.H2(title, style={'textAlign': 'center'}),
            dcc.Graph(id=id),
        ])
    
    def create_input_field(self, id, label):
        return html.Div([
            html.Label(label),
            dcc.Input(id=id, type="number", placeholder=f"Enter {label.lower()}"),
        ], style={'width': '48%', 'display': 'inline-block'})
    
    def create_input_fields(self):
        return html.Div([
            html.H2('Predict House Price', style={'textAlign': 'center'}),
            dbc.Row([
                dbc.Col(dcc.Input(id="input-lokace", type="text", placeholder="Location")),
                dbc.Col(dcc.Input(id="input-dispozice", type="text", placeholder="Layout")),
                dbc.Col(dcc.Input(id="input-stav", type="text", placeholder="Condition")),
            ]),
            dbc.Row([
                dbc.Col(html.Button("Predict", id="predict-button", className="mt-2", n_clicks=0))
            ]),
        ])

    def create_prediction_output(self):
        return html.Div([
            dbc.Row([
                dbc.Col(html.H4("Predicted price:", className="mt-4"), width={"size": 4}),
                dbc.Col(html.H4(id="predicted-price", className="mt-4"), width={"size": 8})
            ])
        ])
    
    def make_prediction(self, n_clicks, lokace, dispozice, stav):
        if n_clicks == 0:
            return "N/A"

        # Map the input features to their corresponding numerical values
        lokace_encoded = self.cleaned_df[self.cleaned_df['LOKACE'] == lokace]['LOKACE'].unique()[0]
        dispozice_encoded = self.cleaned_df[self.cleaned_df['DISPOZICE'] == dispozice]['DISPOZICE'].unique()[0]
        stav_encoded = self.cleaned_df[self.cleaned_df['STAV'] == stav]['STAV'].unique()[0]

        input_features = np.array([[lokace_encoded, dispozice_encoded, stav_encoded]])

        # Use the trained model to make predictions
        prediction = self.lin_reg_rent.predict(input_features)

        # Display the prediction
        return f"${round(prediction[0], 2)}"
    
    def create_layout(self):
        layout = html.Div([
            html.H1(children='Title of Dash App', style={'textAlign': 'center'}),

            self.create_dropdown('xaxis-selection', 'X-axis:', self.cleaned_df.columns, self.cleaned_df.columns[0]),
            self.create_dropdown('yaxis-selection', 'Y-axis:', self.cleaned_df.columns, self.cleaned_df.columns[1]),

            dcc.Graph(id='graph-content'),

            self.create_input_fields(),
            self.create_prediction_output(),

            self.create_visualization('Number of Properties by Building Type', 'bar-chart'),
            self.create_visualization('Correlation Heatmap', 'heatmap'),
            self.create_visualization('Distribution of Property Layouts', 'pie-chart'),
            self.create_visualization('Area Distribution (Box plot)', 'box-plot'),
            self.create_visualization('Area Distribution (Histogram)', 'histogram'),

            # html.Button("Update Visualizations", id="update-visualizations"),

            # self.create_input_field("input-feature-1", "Feature 1"),
            # self.create_input_field("input-feature-2", "Feature 2"),

            # Add more input fields for each feature in your dataset

            # html.Br(),
            # dbc.Button("Predict Rent", id="predict-button", color="primary", n_clicks=0),
            # html.Br(),
            # html.Br(),
            # html.Div(id="prediction-output"),
        ])
        return layout
    
    def set_callbacks(self):
        @self.app.callback(
            Output('graph-content', 'figure'),
            Input('xaxis-selection', 'value'),
            Input('yaxis-selection', 'value')
        )
        def update_graph(x_value, y_value):
            return px.scatter(self.cleaned_df, x=x_value, y=y_value)

        # Add other callback definitions here

        @self.app.callback(
            [Output('bar-chart', 'figure'),
            Output('pie-chart', 'figure'),
            Output('box-plot', 'figure'),
            Output('histogram', 'figure')],
            Input('update-visualizations', 'n_clicks')
        )

        def update_new_visualizations(n_clicks=None):
            fig_bar = px.bar(self.cleaned_df.groupby('TYP BUDOVY').size().reset_index(name='count'), x='TYP BUDOVY', y='count')
            fig_pie = px.pie(self.cleaned_df, names='DISPOZICE')
            fig_box = px.box(self.cleaned_df, y='PLOCHA')
            fig_histogram = px.histogram(self.cleaned_df, x='PLOCHA', nbins=20)
            return fig_bar, fig_pie, fig_box, fig_histogram

        # @self.app.callback(
        #     Output("prediction-output", "children"),
        #     [Input("predict-button", "n_clicks")],
        #     [dash.dependencies.State("input-feature-1", "value"),
        #     dash.dependencies.State("input-feature-2", "value")]
        # )
        # def predict_rent(n_clicks, feature1, feature2):
        #     if n_clicks > 0:
        #         input_data = [feature1, feature2]  # Add more feature values as needed
        #         input_array = np.array(input_data).reshape(1, -1)
        #         input_array_imputed = self.imputer.transform(input_array)
        #         prediction = self.lin_reg_rent.predict(input_array_imputed)
        #         return f"Predicted rent: {prediction[0]:.2f}"
        #     return ""
        
        # Define the callback for making predictions
        @self.app.callback(
            Output("predicted-price", "children"),
            [Input("predict-button", "n_clicks"),
             Input("input-lokace", "value"),
             Input("input-dispozice", "value"),
             Input("input-stav", "value")],
        )
        def make_prediction_callback(n_clicks, lokace, dispozice, stav):
            if n_clicks > 0:
                return self.make_prediction(n_clicks, lokace, dispozice, stav)
            return "N/A"

    def run(self, debug=True):
        self.app.run_server(debug=debug)
