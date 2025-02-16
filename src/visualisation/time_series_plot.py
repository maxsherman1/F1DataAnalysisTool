import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def plot_time_series(data: pd.DataFrame, time_column: str, value_column: str):
    """
    Plot a time series graph.

    :param data: DataFrame containing the time series data.
    :param time_column: Column containing time data.
    :param value_column: Column containing values to plot over time.
    """
    logging.info(f"Plotting time series for {value_column} over {time_column}.")

    plt.figure(figsize=(12, 6))
    plt.plot(data[time_column], data[value_column], marker='o', linestyle='-', color='blue', alpha=0.8)
    plt.title(f'Time Series Plot: {value_column} over {time_column}')
    plt.xlabel(time_column)
    plt.ylabel(value_column)
    plt.grid(True)
    plt.show()


def plot_interactive_time_series(data: pd.DataFrame, time_column: str, value_column: str):
    """
    Plot an interactive time series graph using Plotly.

    :param data: DataFrame containing the time series data.
    :param time_column: Column containing time data.
    :param value_column: Column containing values to plot over time.
    """
    logging.info(f"Generating interactive time series plot for {value_column} over {time_column}.")

    fig = px.line(data, x=time_column, y=value_column, title=f'Time Series Plot: {value_column} over {time_column}')
    fig.show()
