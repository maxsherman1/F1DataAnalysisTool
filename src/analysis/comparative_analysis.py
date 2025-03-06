import pandas as pd
import logging
from scipy.stats import ttest_rel, ttest_ind, f_oneway, spearmanr, pearsonr, wilcoxon

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def paired_t_test(df: pd.DataFrame, col1: str, col2: str) -> tuple[float, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    stat, p_value = ttest_rel(df[col1], df[col2])
    return stat, p_value


def unpaired_t_test(df1: pd.DataFrame, df2: pd.DataFrame, col: str) -> tuple[float, float]:
    if col not in df1.columns or col not in df2.columns:
        logging.error(f"Column {col} not found in one of the DataFrames")
        raise KeyError(f"Column {col} not found in one of the DataFrames")

    stat, p_value = ttest_ind(df1[col], df2[col])
    return stat, p_value


def anova_test(df: pd.DataFrame, col: str, group_col: str) -> tuple[float, float]:
    if col not in df.columns or group_col not in df.columns:
        logging.error(f"Columns {col} or {group_col} not found in DataFrame")
        raise KeyError(f"Columns {col} or {group_col} not found in DataFrame")

    groups = [group[col].values for _, group in df.groupby(group_col)]
    stat, p_value = f_oneway(*groups)
    return stat, p_value


def perform_correlation_analysis(df: pd.DataFrame, col1: str, col2: str, method: str = 'pearson'):
    logging.info(f"Performing {method} correlation analysis between {col1} and {col2}.")

    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    if method == 'pearson':
        corr, p_value = pearsonr(df[col1], df[col2])
    elif method == 'spearman':
        corr, p_value = spearmanr(df[col1], df[col2])
    else:
        raise ValueError("Unsupported method. Use 'pearson' or 'spearman'.")

    logging.info(f"Correlation coefficient: {corr}, p-value: {p_value}")
    return corr, p_value

def wilcoxon_test(df: pd.DataFrame, col1: str, col2: str) -> tuple[float, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    stat, p_value = wilcoxon(df[col1], df[col2])
    return stat, p_value