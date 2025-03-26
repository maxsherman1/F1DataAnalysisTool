from enumeration.analysis_functions import AnalysisFunction

def run_analysis(df, analysis_type, column_1, column_2, additional_param):
    try:
        # Get the corresponding analysis function using the analysis_type
        analysis_func = AnalysisFunction.get_function(analysis_type)

        # Handle Descriptive Analysis functions (e.g., mean, median)
        if analysis_type in [AnalysisFunction.MEAN.value["label"],
                             AnalysisFunction.MEDIAN.value["label"],
                             AnalysisFunction.MODE.value["label"],
                             AnalysisFunction.STD_DEV.value["label"],
                             AnalysisFunction.VARIANCE.value["label"]]:
            result = analysis_func(df, column_1)
            return {"result": result, "method": analysis_type}

        # Handle Comparative Analysis (e.g., paired t-test, ANOVA)
        elif analysis_type in [AnalysisFunction.PAIRED_T_TEST.value["label"],
                               AnalysisFunction.UNPAIRED_T_TEST.value["label"],
                               AnalysisFunction.ANOVA_TEST.value["label"],
                               AnalysisFunction.SPEARMAN_CORR.value["label"],
                               AnalysisFunction.PEARSON_CORR.value["label"],
                               AnalysisFunction.WILCOXON_TEST.value["label"],
                               AnalysisFunction.CHI_SQUARE_TEST.value["label"]]:
            if not column_2:
                raise ValueError("Column 2 is required for comparative analysis")
            result = analysis_func(df, column_1, column_2)
            return {"statistic": result[0], "p_value": result[1], "test": analysis_type}

        # Handle Trend Analysis (e.g., moving average, regression, ARIMA)
        elif analysis_type in [AnalysisFunction.SIMPLE_MOVING_AVG.value["label"],
                               AnalysisFunction.EXPONENTIAL_MOVING_AVG.value["label"],
                               AnalysisFunction.LINEAR_REGRESSION.value["label"],
                               AnalysisFunction.ARIMA_MODEL.value["label"],
                               AnalysisFunction.HOLT_WINTERS.value["label"]]:
            result = analysis_func(df, column_1)
            return {"result": result.tolist(), "method": analysis_type}

        else:
            raise ValueError(f"Analysis type '{analysis_type}' is not supported.")

    except Exception as e:
        return {"error": str(e)}
