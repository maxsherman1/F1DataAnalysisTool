from enum import Enum
import analysis.descriptive_analysis as descriptive_analysis
import analysis.comparative_analysis as comparative_analysis
import analysis.trend_analysis as trend_analysis


class AnalysisFunction(Enum):
    # Descriptive Analysis
    MEAN = {"label": "Mean Calculation", "function": descriptive_analysis.calculate_mean}
    MEDIAN = {"label": "Median Calculation", "function": descriptive_analysis.calculate_median}
    MODE = {"label": "Mode Calculation", "function": descriptive_analysis.calculate_mode}
    STD_DEV = {"label": "Standard Deviation", "function": descriptive_analysis.calculate_std_dev}
    VARIANCE = {"label": "Variance", "function": descriptive_analysis.calculate_variance}

    # Comparative Analysis
    PAIRED_T_TEST = {"label": "Paired t-Test", "function": comparative_analysis.paired_t_test}
    UNPAIRED_T_TEST = {"label": "Unpaired t-Test", "function": comparative_analysis.unpaired_t_test}
    ANOVA_TEST = {"label": "ANOVA Test", "function": comparative_analysis.anova_test}
    SPEARMAN_CORR = {"label": "Spearman Correlation", "function": comparative_analysis.perform_spearman_analysis}
    PEARSON_CORR = {"label": "Pearson Correlation", "function": comparative_analysis.perform_pearson_analysis}
    WILCOXON_TEST = {"label": "Wilcoxon Test", "function": comparative_analysis.wilcoxon_test}
    CHI_SQUARE_TEST = {"label": "Chi-Square Test", "function": comparative_analysis.chi_square_test}

    # Trend Analysis
    SIMPLE_MOVING_AVG = {"label": "Simple Moving Average", "function": trend_analysis.simple_moving_average}
    EXPONENTIAL_MOVING_AVG = {"label": "Exponential Moving Average",
                              "function": trend_analysis.exponential_moving_average}
    LINEAR_REGRESSION = {"label": "Linear Regression", "function": trend_analysis.linear_regression}
    ARIMA_MODEL = {"label": "ARIMA Model", "function": trend_analysis.arima_model}
    HOLT_WINTERS = {"label": "Holt-Winters Model", "function": trend_analysis.holt_winters}

    @classmethod
    def get_function(cls, function_name):
        # This method will return the corresponding function based on the function_name
        for item in cls:
            if item.value["label"] == function_name:
                return item.value["function"]
        raise ValueError(f"Analysis function {function_name} not found.")

    @classmethod
    def get_all_functions(cls):
        # Returns a dictionary of all analysis function names and their corresponding function
        return {item.value["label"]: item.value["function"] for item in cls}
