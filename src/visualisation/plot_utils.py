import seaborn as sns
import plotly.express as px

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

def apply_axis_flip(fig, flip_axis: list = None, plot_type: str = "static"):

    if flip_axis is None:
        flip_axis=[]

    flip_methods = {
        "static": {
            "x": lambda f: f.invert_xaxis(),
            "y": lambda f: f.invert_yaxis()
        },
        "interactive": {
            "x": lambda f: f.update_layout(xaxis=dict(autorange="reversed")),
            "y": lambda f: f.update_layout(yaxis=dict(autorange="reversed"))
        }
    }

    for axis in flip_axis:
        flip_methods[plot_type][axis](fig)

def get_plot_function(plot_type: str, mode: str = "static"):
    plot_mapping = {
        "static": {
            "line": sns.lineplot,
            "bar": sns.barplot,
            "scatter": sns.scatterplot,
            "box": sns.boxplot,
            "hist": sns.histplot,
            "heatmap": sns.heatmap,
            "pie": "pie"  # Placeholder for pie charts in seaborn
        },
        "interactive": {
            "line": px.line,
            "bar": px.bar,
            "scatter": px.scatter,
            "box": px.box,
            "heatmap": px.imshow,
            "hist": px.histogram,
            "pie": px.pie
        }
    }
    return plot_mapping.get(mode, {}).get(plot_type, sns.lineplot if mode == "static" else px.line)  # Default to lineplot