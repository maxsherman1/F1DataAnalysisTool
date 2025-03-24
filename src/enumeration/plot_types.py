from enum import Enum
import seaborn as sns
import plotly.express as px

class PlotMode(Enum):
    STATIC = "static"
    INTERACTIVE = "interactive"

class PlotType(Enum):
    LINE = "line"
    BAR = "bar"
    SCATTER = "scatter"
    BOX = "box"
    HIST = "hist"
    HEATMAP = "heatmap"
    PIE = "pie"

    @classmethod
    def get_all_names(cls):
        return [e.value for e in cls]

class PlotFunction(Enum):
    STATIC = {
        PlotType.LINE: sns.lineplot,
        PlotType.BAR: sns.barplot,
        PlotType.SCATTER: sns.scatterplot,
        PlotType.BOX: sns.boxplot,
        PlotType.HIST: sns.histplot,
        PlotType.HEATMAP: sns.heatmap,
        PlotType.PIE: "pie"  # Placeholder for pie charts in seaborn
    }
    INTERACTIVE = {
        PlotType.LINE: px.line,
        PlotType.BAR: px.bar,
        PlotType.SCATTER: px.scatter,
        PlotType.BOX: px.box,
        PlotType.HEATMAP: px.imshow,
        PlotType.HIST: px.histogram,
        PlotType.PIE: px.pie
    }

    @classmethod
    def get_plot_function(cls, plot_type: PlotType, mode: PlotMode):
        return cls[mode.name].value.get(plot_type, sns.lineplot if mode == PlotMode.STATIC else px.line)  # Default to lineplot