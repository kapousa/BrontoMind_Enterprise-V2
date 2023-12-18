import numpy as np
import pandas as pd

from app.src.backend.core.engine.processors.WordProcessor import WordProcessor


class ChatControllerHelper:
    #   Common data words dictionary
    _data_exploration_mapping = {
        # Identifying data
        "what": {
            "general": ".describe()",
            "specific": {
                "columns": ".columns",
                "index": ".index",
                "data": ".head()",
                "tail": ".tail()",
            },
        },
        "which": {
            "specific": {
                "values": ".loc",
                "conditions": ".query()",
                "matches": ".isin()",
            },
        },
        "where": {
            "specific": {
                "conditions": ".query()",
                "matches": ".isin()",
            },
        },
        "who": {
            "specific": {
                "conditions": ".query()",
                "matches": ".isin()",
                "groups": ".groupby()",
            },
        },

        # Understanding data
        "describe": ".describe()",
        "summarize": {
            "general": ".describe()",
            "counts": ".count()",
            "uniques": ".value_counts()",
            "statistics": ".agg()",
            "groups": ".groupby() + aggregations",
        },
        "analyze": {
            "relationships": ".corr()",
            "patterns": ".groupby() + pivot_table(), .get_dummies(), .clustermap()",
            "trends": ".rolling_mean(), .rolling_median(), .diff()",
        },

        # Comparing data
        "compare": {
            "differences": ".diff(), .pct_change()",
            "groups": ".groupby() + comparisons",
            "merge": ".merge()",
        },
        "contrast": {
            "groups": ".groupby() + comparisons",
            "visualizations": ".boxplot(), .violinplot()",
        },
        "difference": {
            "values": ".diff(), .pct_change()",
            "groups": ".groupby() + comparisons",
        },

        # Predicting with data
        "predict": ".fit() + .predict() (machine learning)",
        "forecast": ".arima(), .Prophet() (time series)",
        "estimate": {
            "central tendency": ".mean(), .median(), .mode()",
            "regression": ".OLS()"
        },

        # Additional common words
        "trend": ".rolling_mean(), .rolling_median(), .diff(), .plot() (time series)",
        "pattern": ".groupby() + pivot_table(), .get_dummies(), .clustermap()",
        "correlation": ".corr(), .cov(), .heatmap()",
        "relationship": ".groupby() + corr(), .scatter_plot(), .plot() (regression)",
        "filter": ".loc, .iloc, .query(), .isin()",
        "sort": ".sort_values(), .rank(), .nlargest(), .nsmallest()",
        "group by": ".groupby(), .pivot_table()",
        "why": "hypothesis testing, statistical analysis",
        "how": "specific data manipulation methods (e.g., .fillna(), .dropna())",
    }

    data_exploration_mapping = {
        # Identifying data
        "what": "pivot_table",
        "where": ".isin()",
        "who": ".query()",
        "describe": "_get_description",
        "summarize": "_get_description",
        "analyze": ".corr()",
        "compare": ".diff()",
        "contrast": ".boxplot()",
        "difference": ".diff()",
        "predict": ".fit()",
        "average": "_get_averages", #".mean( par )",
        "trend": ".rolling_mean(), .rolling_median(), .diff(), .plot() (time series)",
        "pattern": ".groupby() + pivot_table(), .get_dummies(), .clustermap()",
        "correlation": ".corr(), .cov(), .heatmap()",
        "relationship": ".groupby() + corr(), .scatter_plot(), .plot() (regression)",
        "filter": ".loc, .iloc, .query(), .isin()",
        "sort": ".sort_values(), .rank(), .nlargest(), .nsmallest()",
        "group by": ".groupby(), .pivot_table()",
        "why": "hypothesis testing, statistical analysis",
        "how": "specific data manipulation methods (e.g., .fillna(), .dropna())",
    }

    mentioned_columns =[]

    @staticmethod
    def connect_to_bot():
        return 0

    def generate_response(self, df, input_text):
        ''' Generates AI data analysis response to user input regarding his input data '''
        response_text = []

        # Check each key using a loop and string methods
        found_keys = []

        # Get mentioned columns
        word_processor = WordProcessor()
        mentioned_columns = []
        input_text_array = input_text.split(' ')
        entered_columns = word_processor.get_closest_words(df.columns, input_text_array)
        entered_keys = word_processor.get_closest_words(self.data_exploration_mapping.keys(), input_text_array)
        for string_item in input_text_array:
            if string_item.lower() in entered_columns:
                mentioned_columns.append(string_item.lower())

        # Call required function
        for key in self.data_exploration_mapping:
            if key.lower() in entered_keys:
                found_keys.append(key)
                df_response = getattr(self, self.data_exploration_mapping[key])(df, mentioned_columns)
                response_text.append(df_response)

        response_text = np.array(response_text)
        return response_text.flatten()

    def _get_averages(self, df, cols_name):
        ''' Calculates the average of given columns '''
        try:
            averages = []
            for col_name in cols_name:
                if pd.api.types.is_numeric_dtype(df[col_name]):
                    averages.append(f"Average of {col_name} : {df[col_name].mean()}")
                else:
                    averages.append(f"{col_name} is not a numeric column")

            return averages

        except Exception as e:
            print(e)

    def _get_description(self, df, cols_name):
        ''' Calculates the average of given columns '''
        try:
            return str(df.describe())

        except Exception as e:
            print(e)
