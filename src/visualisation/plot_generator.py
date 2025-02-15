import matplotlib.pyplot as plt
import seaborn as sns

def format_label(label):
    new_label = ""
    for char in label:
        if char.isupper() and new_label and new_label[-1] != ' ':
            new_label += ' '
        elif char == '.':
            new_label += ' '
            continue
        new_label += char.lower()
    return new_label.capitalize()

def configure_plot(title, x_label="", y_label=""):
    if x_label:
        x_label = format_label(x_label)
    if y_label:
        y_label = format_label(y_label)

    #Add title, labels, and a grid
    plt.title(title, fontsize=16, color='white')
    plt.xlabel(x_label, fontsize=12, color='white')
    plt.ylabel(y_label, fontsize=12, color='white')
    plt.yticks(color='white')
    plt.grid(color="gray", linestyle="--", linewidth=0.5)

    # Check length of x-axis labels and rotate 45 degrees if longer than length 5
    x_labels = [tick.get_text() for tick in plt.gca().get_xticklabels()]
    if any(len(label) > 5 for label in x_labels):
        plt.xticks(color='white', rotation=45, ha='right')
    else:
        plt.xticks(color='white')

    # Tidy the layout
    plt.tight_layout()

def plot_chart(df, x_col, y_col = None, title = "", plot_type="line", hue=None, figsize=(10, 5), flip_axis=None, theme="dark_background", **kwargs):
    # Style and size configuration
    plt.style.use(theme)
    plt.figure(figsize=figsize)

    # Axis flipping
    if flip_axis in ["y", "both"]:
        plt.gca().invert_yaxis()
    if flip_axis in ["x", "both"]:
        plt.gca().invert_xaxis()

    # Data configuration for heatmpa and histograms
    if plot_type == "heatmap":
        df = df.corr()
    elif plot_type == "hist":
        df = df[x_col]
        y_col="Frequency"

    # plotting the graph
    plot_func = {
        "line": sns.lineplot,
        "bar": sns.barplot,
        "scatter": sns.scatterplot,
        "box": sns.boxplot,
        "hist": sns.histplot,
        "heatmap": sns.heatmap,
    }
    if plot_type == "pie":
        df[x_col].value_counts().plot.pie(autopct='%1.1f%%', **kwargs)
    else:
        plot_func[plot_type](data=df, x=x_col, y=y_col, hue=hue, **kwargs)

    # Add legend if hue has been specified
    if hue:
        plt.legend(title=hue, bbox_to_anchor=(1, 1), loc="upper left", fontsize=10)

    # Configure and show plot
    configure_plot(title, x_label=x_col, y_label=y_col)
    plt.show()
