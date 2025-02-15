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

def plot_chart(df, x_col, y_col = None, title = "", plot_type="line", hue=None, figsize=(10, 5), flip_axis=None, **kwargs):
    plt.style.use("dark_background")
    plt.figure(figsize=figsize)
    if flip_axis in ["y", "both"]:
        plt.gca().invert_yaxis()
    if flip_axis in ["x", "both"]:
        plt.gca().invert_xaxis()
    plot_func = {
        "line": sns.lineplot,
        "bar": sns.barplot,
        "scatter": sns.scatterplot,
        "box": sns.boxplot,
        "hist": sns.histplot,
        "heatmap": sns.heatmap,
    }
    if plot_type == "heatmap":
        plot_func[plot_type](df.corr(), annot=kwargs.get("annot", True), cmap=kwargs.get("cmap", "coolwarm"), fmt=kwargs.get("fmt", ".2f"))
    elif plot_type == "hist":
        plot_func[plot_type](df[x_col], bins=kwargs.get("bins", 20), kde=kwargs.get("kde", True))
        y_col="Frequency"
    elif plot_type == "pie":
        df[x_col].value_counts().plot.pie(autopct='%1.1f%%', **kwargs)
    else:
        plot_func[plot_type](data=df, x=x_col, y=y_col, hue=hue, **kwargs)
    if hue:
        plt.legend(title=hue, bbox_to_anchor=(1, 1), loc="upper left", fontsize=10)
    configure_plot(title, x_label=x_col, y_label=y_col)
    plt.show()
