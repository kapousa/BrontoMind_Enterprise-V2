# Import libraries
import os

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import logging
from flask import abort
from pandas_profiling import ProfileReport
from wordcloud import WordCloud

from app.src.backend.constants.BM_CONSTANTS import html_reports_location, short_html_reports_location, html_reports


class ReportsControllerHelper:

    @staticmethod
    def generatecharts(user_id, dataset_id, df):
        try:
            # Show distributions
            label = df.columns[-1]
            target_columns = df.loc[:, df.columns != label]
            reports_path = f"{html_reports_location}{user_id}/{dataset_id}/"
            os.makedirs(f"{html_reports_location}{user_id}", exist_ok=True)
            os.makedirs(reports_path, exist_ok=True)

            y_range = df[label]
            html_file_locations = []

            for col in target_columns:
                html_file_location = f"{reports_path}{col}.html"
                short_html_file_location = f"{short_html_reports_location}{user_id}/{dataset_id}/{col}.html"
                x_range = df[col]
                fig = px.scatter(x=x_range, y=y_range, labels={"x": col, "y": label}, opacity=0.65, trendline="ols",
                                 trendline_color_override="red") if pd.api.types.is_numeric_dtype(
                    df[col]) and pd.api.types.is_numeric_dtype(df[label]) else px.scatter(x=x_range, y=y_range,
                                                                                          labels={"x": col, "y": label},
                                                                                          opacity=0.65)
                fig.update_layout(
                    title=f'{label} vs. {col}',  # Set plot title
                    showlegend=False,  # Display legend
                    legend_title='Color Legend',  # Set legend title
                    legend=dict(
                        x=0.5,
                        y=1.0,
                        xanchor='center',
                        yanchor='top',
                        bgcolor='lightgray',
                        bordercolor='black',
                        borderwidth=2,
                        font=dict(
                            family='Arial',
                            size=12,
                            color='black'
                        )
                    ),
                    autosize=True # Set background color
                )
                plotly.offline.plot(fig, filename=html_file_location, config={'displayModeBar': False},
                                    auto_open=False)
                html_file_locations.append(short_html_file_location)
                break

            return html_file_locations

        except FileNotFoundError as e:
            print(f"Parent directory doesn't exist: {e}")
            print(e)
            logging.error(e)
            abort(500)
        except PermissionError as e:
            print(f"Insufficient permission to create folder: {e}")
            print(e)
            logging.error(e)
            abort(500)
        except OSError as e:
            print(f"Unexpected OSError: {e}")
            print(e)
            logging.error(e)
            abort(500)
        except Exception as e:
            print(e)
            logging.error(e)
            abort(500)

    @staticmethod
    def generateinforeport(user_id, dataset_id, df):
        try:
            # Data profiling
            # Create a pandas profile report
            profile = ProfileReport(df, title='Dataset Descriptive Report', explorative=True)

            # Save the report to a file (HTML format)
            os.makedirs(f"{html_reports_location}{user_id}", exist_ok=True)
            os.makedirs(f"{html_reports_location}{user_id}/{dataset_id}", exist_ok=True)
            report_path = f"{html_reports_location}{user_id}/{dataset_id}/stats.html"
            if not os.path.isfile(report_path):
                profile.to_file(report_path)

            return report_path

        except Exception as e:
            print(e)
            logging.error(e)
            abort(500)
