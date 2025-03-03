import numpy as np
from scipy import stats

def calculate_mean(df, column):
    return np.mean(df[column])

def calculate_median(df, column):
    return np.median(df[column])

def calculate_mode(df, column):
    values, counts = np.unique(df[column], return_counts=True)
    if np.all(counts == 1):
        return None
    return stats.mode(df[column], keepdims=True)[0][0]

def calculate_std_dev(df, column):
    return np.std(df[column], ddof=1)

def calculate_variance(df, column):
    return np.var(df[column], ddof=1)

def descriptive_statistics(df, column):
    return {
        'Mean': calculate_mean(df, column),
        'Median': calculate_median(df, column),
        'Mode': calculate_mode(df, column),
        'Standard Deviation': calculate_std_dev(df, column),
        'Variance': calculate_variance(df, column)
    }
