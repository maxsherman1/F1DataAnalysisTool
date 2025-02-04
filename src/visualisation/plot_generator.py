import matplotlib.pyplot as plt
import seaborn as sns

def plot_line_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x=x_col, y=y_col, marker='o')
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid()
    plt.show()


def plot_bar_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df, x=x_col, y=y_col)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.xticks(rotation=45)
    plt.show()


def plot_scatter_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 5))
    sns.scatterplot(data=df, x=x_col, y=y_col)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.show()


def plot_box_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df, x=x_col, y=y_col)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.xticks(rotation=45)
    plt.show()


def plot_histogram(df, col, title):
    plt.figure(figsize=(10, 5))
    sns.histplot(df[col], bins=20, kde=True)
    plt.title(title)
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.show()


def plot_pie_chart(df, col, title):
    plt.figure(figsize=(8, 8))
    df[col].value_counts().plot.pie(autopct='%1.1f%%')
    plt.title(title)
    plt.ylabel('')  # Hide y-label
    plt.show()