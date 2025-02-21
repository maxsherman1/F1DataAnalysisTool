from pathlib import Path
from typing import Any

# Define save directory
PLOTS_DIR = Path(__file__).resolve().parent.parent.parent / "data/plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def save_plot(fig: Any, filename: str, plot_type: str = "static", file_format: str = "png"):
    # Construct full save path
    save_path = PLOTS_DIR / f"{filename}.{file_format}"

    # Save for static (matplotlib/seaborn)
    if plot_type == "static":
        fig.savefig(save_path, format=file_format, bbox_inches="tight")

    # Save for interactive (plotly)
    elif plot_type == "interactive":
        if file_format == "html":
            fig.write_html(save_path)
        else:
            fig.write_image(save_path, format=file_format)

def get_plots_directory() -> Path:
    return PLOTS_DIR