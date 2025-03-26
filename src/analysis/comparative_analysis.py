import pandas as pd
import logging
from scipy.stats import ttest_rel, ttest_ind, f_oneway, spearmanr, pearsonr, wilcoxon, chi2_contingency

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def paired_t_test(df: pd.DataFrame, col1: str, col2: str) -> tuple[float, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    stat, p_value = ttest_rel(df[col1], df[col2])
    return stat, p_value


def unpaired_t_test(df: pd.DataFrame, col1: str, col2: str) -> tuple[float, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Column {col1} or {col2} not found in one of the DataFrames")
        raise KeyError(f"Column {col1} or {col2} not found in one of the DataFrames")

    stat, p_value = ttest_ind(df[col1], df[col2])
    return stat, p_value


def anova_test(df: pd.DataFrame, col: str, group_col: str) -> tuple[float, float]:
    if col not in df.columns or group_col not in df.columns:
        logging.error(f"Columns {col} or {group_col} not found in DataFrame")
        raise KeyError(f"Columns {col} or {group_col} not found in DataFrame")

    groups = [group[col].values for _, group in df.groupby(group_col)]
    stat, p_value = f_oneway(*groups)
    return stat, p_value

def perform_pearson_analysis(df: pd.DataFrame, col1: str, col2: str):
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    corr, p_value = pearsonr(df[col1], df[col2])
    return corr, p_value

def perform_spearman_analysis(df: pd.DataFrame, col1: str, col2: str):
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    corr, p_value = spearmanr(df[col1], df[col2])
    return corr, p_value

def wilcoxon_test(df: pd.DataFrame, col1: str, col2: str) -> tuple[float, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    stat, p_value = wilcoxon(df[col1], df[col2])
    return stat, p_value

def chi_square_test(df: pd.DataFrame, col1: str, col2: str) -> tuple[float, float]:
    if col1 not in df.columns or col2 not in df.columns:
        logging.error(f"Columns {col1} or {col2} not found in DataFrame")
        raise KeyError(f"Columns {col1} or {col2} not found in DataFrame")

    contingency_table = pd.crosstab(df[col1], df[col2])
    stat, p_value, _, _ = chi2_contingency(contingency_table)
    return stat, p_value
