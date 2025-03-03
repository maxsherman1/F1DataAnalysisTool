import numpy as np
import pandas as pd
from scipy import stats

def calculate_mean(df: pd.DataFrame, column: str) -> float:
    return np.mean(df[column])

def calculate_median(df: pd.DataFrame, column: str) -> float:
    return np.median(df[column])

def calculate_mode(df: pd.DataFrame, column: str) -> float | None:
    values, counts = np.unique(df[column], return_counts=True)
    if np.all(counts == 1):
        return None
    return float(stats.mode(df[column], keepdims=True)[0][0])

def calculate_std_dev(df: pd.DataFrame, column: str) -> float:
    return np.std(df[column], ddof=1)

def calculate_variance(df: pd.DataFrame, column: str) -> float:
    return np.var(df[column], ddof=1)

def descriptive_statistics(df: pd.DataFrame, column: str) -> dict[str, float | None]:
    return {
        'Mean': calculate_mean(df, column),
        'Median': calculate_median(df, column),
        'Mode': calculate_mode(df, column),
        'Standard Deviation': calculate_std_dev(df, column),
        'Variance': calculate_variance(df, column)
    }
