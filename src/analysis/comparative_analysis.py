import pandas as pd
import logging
from scipy.stats import ttest_rel, ttest_ind, f_oneway, spearmanr, pearsonr, wilcoxon

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def paired_t_test(df: pd.DataFrame, col1: str, col2: str) -> dict[str, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    stat, p_value = ttest_rel(df[col1], df[col2])
    return {"t-statistic": stat, "p-value": p_value}


def unpaired_t_test(df1: pd.DataFrame, df2: pd.DataFrame, col: str) -> dict[str, float]:
    if col not in df1.columns or col not in df2.columns:
        logging.error(f"Column {col} not found in one of the DataFrames")
        raise KeyError(f"Column {col} not found in one of the DataFrames")

    stat, p_value = ttest_ind(df1[col], df2[col])
    return {"t-statistic": stat, "p-value": p_value}


def anova_test(df: pd.DataFrame, col: str, group_col: str) -> dict[str, float]:
    if col not in df.columns or group_col not in df.columns:
        logging.error(f"Columns {col} or {group_col} not found in DataFrame")
        raise KeyError(f"Columns {col} or {group_col} not found in DataFrame")

    groups = [group[col].values for _, group in df.groupby(group_col)]
    stat, p_value = f_oneway(*groups)
    return {"F-statistic": stat, "p-value": p_value}


def spearman_correlation_analysis(df: pd.DataFrame, col1: str, col2: str) -> dict[str, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    correlation, p_value = spearmanr(df[col1], df[col2])
    return {"Spearman Correlation": correlation, "p-value": p_value}

def pearson_correlation_analysis(df: pd.DataFrame, col1: str, col2: str) -> dict[str, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    correlation, p_value = pearsonr(df[col1], df[col2])
    return {"Pearson Correlation": correlation, "p-value": p_value}

def wilcoxon_test(df: pd.DataFrame, col1: str, col2: str) -> dict[str, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    stat, p_value = wilcoxon(df[col1], df[col2])
    return {"Wilcoxon statistic": stat, "p-value": p_value}