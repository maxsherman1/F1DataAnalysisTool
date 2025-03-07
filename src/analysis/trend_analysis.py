import logging
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def simple_moving_average(df: pd.DataFrame, column: str, window: int) -> pd.Series:
    if column not in df.columns:
        logging.error(f"Column {column} not found in DataFrame")
        raise KeyError(f"Column {column} not found in DataFrame")
    if window <= 0:
        logging.error("Window size must be positive")
        raise ValueError("Window size must be positive")


    logging.info(f"Calculating simple moving average for {column} with window size {window}")
    return df[column].rolling(window=window).mean()


def exponential_moving_average(df: pd.DataFrame, column: str, span: int) -> pd.Series:
    if column not in df.columns:
        logging.error(f"Column {column} not found in DataFrame")
        raise KeyError(f"Column {column} not found in DataFrame")
    if span <= 0:
        logging.error("Span must be positive")
        raise ValueError("Span must be positive")

    logging.info(f"Calculating exponential moving average for {column} with span {span}")
    return df[column].ewm(span=span, adjust=False).mean()


def linear_regression(df: pd.DataFrame, target_column: str, feature_columns: list[str] = None) -> np.ndarray:
    if target_column not in df.columns:
        logging.error(f"Column '{target_column}' not found in DataFrame")
        raise KeyError(f"Column '{target_column}' not found in DataFrame")

        # If no feature columns are provided, use the DataFrame index (assumes sequential data)
    if feature_columns is None:
        logging.info(f"No feature columns provided. Using DataFrame index as independent variable.")
        X = np.arange(len(df)).reshape(-1, 1)
    else:
        missing_cols = [col for col in feature_columns if col not in df.columns]
        if missing_cols:
            logging.error(f"Columns {missing_cols} not found in DataFrame")
            raise KeyError(f"Columns {missing_cols} not found in DataFrame")
        X = df[feature_columns].values

        # Extract the target variable
    y = df[target_column].values.reshape(-1, 1)

    logging.info(
        f"Fitting linear regression model for {target_column} using {feature_columns or 'index'} as independent variable(s).")

    # Train the Linear Regression model
    model = LinearRegression()
    model.fit(X, y)

    # Return predicted values
    return model.predict(X).flatten()


def arima_model(df: pd.DataFrame, column: str, order: tuple[int, int, int]) -> np.ndarray:
    if column not in df.columns:
        logging.error(f"Column {column} not found in DataFrame")
        raise KeyError(f"Column {column} not found in DataFrame")

    logging.info(f"Fitting ARIMA model for {column} with order {order}")
    model = ARIMA(df[column], order=order)
    fitted_model = model.fit()
    return fitted_model.fittedvalues


def holt_winters(df: pd.DataFrame, column: str, trend: str = 'add', seasonal: str = 'add',
                 seasonal_periods: int = 12) -> np.ndarray:
    if column not in df.columns:
        logging.error(f"Column {column} not found in DataFrame")
        raise KeyError(f"Column {column} not found in DataFrame")

    logging.info(
        f"Fitting Holt-Winters model for {column} with trend {trend}, seasonal {seasonal}, and seasonal periods {seasonal_periods}")
    model = ExponentialSmoothing(df[column], trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods)
    fitted_model = model.fit()
    return fitted_model.fittedvalues

