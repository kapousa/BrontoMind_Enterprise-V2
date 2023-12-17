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

    _data_exploration_mapping = {
        # Identifying data
        "what": "pivot_table",
        "where": ".isin()",
        "who": ".query()",
        "describe": ".describe()",
        "summarize": ".agg()",
        "analyze": ".corr()",
        "compare": ".diff()",
        "contrast": ".boxplot()",
        "difference": ".diff()",
        "predict": ".fit()",
        "forecast": ".mean()",
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

    @staticmethod
    def connect_to_bot():
        return 0

    def generate_response(self, df, input_text):
        ''' Generates AI data analysis response to user input regarding his input data '''
        response_text = []

        # Check each key using a loop and string methods
        found_keys = []
        for key in self._data_exploration_mapping:
            if key.lower() in input_text.lower():
                found_keys.append(key)
                df_response = getattr(df, self._data_exploration_mapping[key])()
                response_text.append(df_response)

        return response_text