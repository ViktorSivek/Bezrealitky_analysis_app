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


    def create_layout(self):
        layout = html.Div([
            html.H1(children='Title of Dash App', style={'textAlign': 'center'}),

            html.Div([
                html.Label("X-axis:"),
                dcc.Dropdown(
                    id='xaxis-selection',
                    options=[{'label': i, 'value': i} for i in self.cleaned_df.columns],
                    value=self.cleaned_df.columns[0]
                ),
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.Label("Y-axis:"),
                dcc.Dropdown(
                    id='yaxis-selection',
                    options=[{'label': i, 'value': i} for i in self.cleaned_df.columns],
                    value=self.cleaned_df.columns[1]
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

            # Add input fields for the model features
            html.Div([
                html.Label("Feature 1"),
                dcc.Input(id="input-feature-1", type="number", placeholder="Enter feature 1"),
            ], style={'width': '48%', 'display': 'inline-block'}),

            html.Div([
                html.Label("Feature 2"),
                dcc.Input(id="input-feature-2", type="number", placeholder="Enter feature 2"),
            ], style={'width': '48%', 'display': 'inline-block'}),

            # Add more input fields for each feature in your dataset

            html.Br(),
            dbc.Button("Predict Rent", id="predict-button", color="primary", n_clicks=0),
            html.Br(),
            html.Br(),
            html.Div(id="prediction-output"),
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
            Output('bar-chart', 'figure'),
            # Output('heatmap', 'figure'),
            Output('pie-chart', 'figure'),
            Output('box-plot', 'figure'),
            Output('histogram', 'figure'),
            Output("prediction-output", "children"),
            Input('update-visualizations', 'n_clicks'),
            [Input("predict-button", "n_clicks")],
            [dash.dependencies.State("input-feature-1", "value"),
             dash.dependencies.State("input-feature-2", "value")]
        )

        def predict_rent(n_clicks, feature1, feature2):
            if n_clicks > 0:
                input_data = [feature1, feature2]  # Add more feature values as needed
                input_array = np.array(input_data).reshape(1, -1)
                input_array_imputed = self.imputer.transform(input_array)
                prediction = self.lin_reg_rent.predict(input_array_imputed)
                return f"Predicted rent: {prediction[0]:.2f}"
            return ""

        def update_new_visualizations(n_clicks=None):
            fig_bar = px.bar(self.cleaned_df.groupby('TYP BUDOVY').size().reset_index(name='count'), x='TYP BUDOVY', y='count')
            fig_pie = px.pie(self.cleaned_df, names='DISPOZICE')
            fig_box = px.box(self.cleaned_df, y='PLOCHA')
            fig_histogram = px.histogram(self.cleaned_df, x='PLOCHA', nbins=20)
            return fig_bar, fig_pie, fig_box, fig_histogram

    def run(self, debug=True):
        self.app.run_server(debug=debug)
