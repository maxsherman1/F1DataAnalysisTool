import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_line_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x=x_col, y=y_col, marker='o')
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.grid()
    plt.show()

# plots a line chart lap vs position grouped by driver, requires lap data argument
def plot_position_chart(df, title="F1 Race Lap Chart"):

    # Data filtering retrieves lap number, position, and driver
    lap_data = []
    for i in range(1, 21):  # Assuming 20 drivers
        driver_col = f"Timings.{i}.driverId"
        position_col = f"Timings.{i}.position"
        # Data validation
        if driver_col in df.columns and position_col in df.columns:
            for lap in range(len(df)):
                lap_data.append({
                    "lap": df.loc[lap, "number"],  # Lap number
                    "driver": df.loc[lap, driver_col],  # Driver name
                    "position": df.loc[lap, position_col]  # Position on that lap
                })
    df = pd.DataFrame(lap_data)

    plt.figure(figsize=(14, 8))
    plt.style.use("dark_background")  # Set dark theme

    # Sort to ensure correct plotting
    df = df.sort_values(by=["driver", "lap"])

    # Plot each driver's position over time
    sns.lineplot(x=df["lap"], y=df["position"], hue=df["driver"], linewidth=2, marker="o", alpha=1)

    # Formatting
    plt.xlabel("Lap Number", fontsize=12, color="black", fontweight="bold")
    plt.ylabel("Position (Lower is Better)", fontsize=12, color="black", fontweight="bold")
    plt.title(title, fontsize=16, color="black", fontweight="bold")
    plt.legend(title="Driver", bbox_to_anchor=(1, 1), loc='upper left', fontsize=10)

    plt.gca().invert_yaxis()  # Flip to show P1 at the top
    plt.grid(color="gray", linestyle="--", linewidth=0.5)  # Light grid
    plt.show()


def plot_bar_chart(df, x_col, y_col, title, hue=None, dodge=True, color='darkblue'):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=(10, 5))
    sns.barplot(data=df, x=x_col, y=y_col, hue=hue, dodge=dodge, errcolor='white', color=color)
    plt.title(title, fontsize=16, color='white')
    plt.xlabel(x_col, fontsize=12, color='white')
    plt.ylabel(y_col, fontsize=12, color='white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.grid(color="gray", linestyle="--", linewidth=0.5)
    plt.show()


def plot_scatter_chart(df, x_col, y_col, title):
    plt.figure(figsize=(10, 5))
    sns.scatterplot(data=df, x=x_col, y=y_col)
    plt.title(title)
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.show()


def plot_box_chart(df, x_col, title, y_col=None, hue=None, dodge=True, whis=1.5, color=None):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=(10, 5))
    sns.boxplot(data=df, x=x_col, y=y_col, hue=hue, dodge=dodge, whis=whis, color=color)
    plt.title(title, fontsize=16, color='white')
    plt.xlabel(x_col, fontsize=12, color='white')
    plt.ylabel(y_col if y_col else '', fontsize=12, color='white')
    plt.xticks(rotation=45, color='white')
    plt.yticks(color='white')
    plt.grid(color="gray", linestyle="--", linewidth=0.5)
    plt.show()


def plot_histogram(df, col, title):
    plt.figure(figsize=(10, 5))
    sns.histplot(df[col], bins=20, kde=True)
    plt.title(title)
    plt.xlabel(col)
    plt.ylabel('Frequency')
    plt.show()


def plot_pie_chart(df, col, title, explode=None, startangle=90, colors=None):
    plt.style.use("dark_background")  # Set dark background
    plt.figure(figsize=(8, 8))
    df[col].value_counts().plot.pie(autopct='%1.1f%%', explode=explode, startangle=startangle, colors=colors)
    plt.title(title, fontsize=16, color='white')
    plt.ylabel('')  # Hide y-label
    plt.show()