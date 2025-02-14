import matplotlib.pyplot as plt
import seaborn as sns

def configure_plot(title, x_label="", y_label=""):
    plt.title(title, fontsize=16, color='white')
    plt.xlabel(x_label, fontsize=12, color='white')
    plt.ylabel(y_label, fontsize=12, color='white')
    plt.xticks(color='white', rotation=45, ha='right')
    plt.yticks(color='white')
    plt.grid(color="gray", linestyle="--", linewidth=0.5)
    plt.tight_layout()

def plot_line_chart(df, x_col, y_col, title, hue=None, linewidth=2, alpha=1, linestyle='-', marker='o', figsize=(10, 5), flip_axis=None):
    plt.style.use("dark_background")
    plt.figure(figsize=figsize)
    sns.lineplot(data=df, x=x_col, y=y_col, hue=hue, linewidth=linewidth, marker=marker, alpha=alpha, linestyle=linestyle)
    if hue:
        plt.legend(title=hue, bbox_to_anchor=(1, 1), loc='upper left', fontsize=10)
    configure_plot(title, x_col, y_col)
    if flip_axis in ["y", "both"]:
        plt.gca().invert_yaxis()
    if flip_axis in ["x", "both"]:
        plt.gca().invert_xaxis()
    plt.show()

def plot_bar_chart(df, x_col, y_col, title, hue=None, dodge=True, color='darkblue'):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df, x=x_col, y=y_col, hue=hue, dodge=dodge, errcolor='white', color=color)
    configure_plot(title, x_col, y_col)
    plt.show()

def plot_scatter_chart(df, x_col, y_col, title, hue=None, alpha=1, marker='o', figsize=(10, 5)):
    plt.style.use("dark_background")
    plt.figure(figsize=figsize)
    sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue, alpha=alpha, marker=marker)
    if hue:
        plt.legend(title=hue, bbox_to_anchor=(1, 1), loc='upper left', fontsize=10)
    configure_plot(title, x_col, y_col)
    plt.show()

def plot_box_chart(df, x_col, title, y_col=None, hue=None, dodge=True, whis=1.5, color=None):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df, x=x_col, y=y_col, hue=hue, dodge=dodge, whis=whis, color=color)
    configure_plot(title, x_col, y_col)
    plt.show()

def plot_pie_chart(df, col, title, explode=None, startangle=90, colors=None):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=(8, 8))
    df[col].value_counts().plot.pie(autopct='%1.1f%%', explode=explode, startangle=startangle, colors=colors)
    configure_plot(title)
    plt.ylabel('')  # Hide y-label
    plt.show()

def plot_heatmap(df, title, figsize=(10, 6), cmap='coolwarm', annot=True, fmt='.2f'):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=figsize)
    sns.heatmap(df.corr(), annot=annot, cmap=cmap, fmt=fmt)
    configure_plot(title)
    plt.show()

def plot_histogram(df, col, title):
    plt.figure(figsize=(10, 5))
    sns.histplot(df[col], bins=20, kde=True)
    plt.title(title)
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.show()