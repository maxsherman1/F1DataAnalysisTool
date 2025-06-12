from pathlib import Path
from typing import Any
import matplotlib.pyplot as plt
import plotly.io as pio

# Define save directory
PLOTS_DIR = Path(__file__).resolve().parent.parent.parent / "data/plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)

def save_plot(fig: Any, filename: str, plot_type: str = "static", file_format: str = "png") -> None:
    # Construct full save path
    save_path = PLOTS_DIR / f"{filename}.{file_format}"

    try:
        if plot_type == "static":
            if isinstance(fig, plt.Figure):
                fig.savefig(save_path, format=file_format, bbox_inches="tight")
            else:
                raise ValueError("Invalid figure type for static plot.")
        elif plot_type == "interactive":
            if file_format == "html":
                pio.write_html(fig, save_path)
            else:
                pio.write_image(fig, save_path, format=file_format)
        else:
            raise ValueError("Unsupported plot type. Choose 'static' or 'interactive'.")
    except Exception as e:
        raise RuntimeError(f"Failed to save plot: {e}")

def get_plots_directory() -> Path:
    return PLOTS_DIR