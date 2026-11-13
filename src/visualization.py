"""Visualization functions for the nutrition comparison."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def create_comparison_charts(
    summary_df: pd.DataFrame, output_dir: str = "output/charts"
) -> list[str]:
    """Create comparison charts and return their file paths."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    chart_specs = [
        ("avg_calories", "Average calories", "average_calories.png"),
        ("avg_fat_g", "Average fat (g)", "average_fat.png"),
        ("avg_sugars_g", "Average sugars (g)", "average_sugars.png"),
        ("avg_sodium_mg", "Average sodium (mg)", "average_sodium.png"),
    ]
    paths = []
    for column, title, filename in chart_specs:
        figure, axis = plt.subplots(figsize=(7, 4))
        axis.bar(summary_df["restaurant"], summary_df[column], color=["#006241", "#d62828"])
        axis.set_title(title)
        axis.set_ylabel(title.removeprefix("Average "))
        axis.tick_params(axis="x", rotation=15)
        figure.tight_layout()
        chart_path = output_path / filename
        figure.savefig(chart_path, dpi=150)
        plt.close(figure)
        paths.append(str(chart_path))
    return paths


def create_relationship_chart(
    items_df: pd.DataFrame, output_dir: str = "output/charts"
) -> str:
    """Create a calorie-to-fat relationship scatter plot."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    figure, axis = plt.subplots(figsize=(7, 4))
    for restaurant, color in (("Starbucks", "#006241"), ("McDonald's", "#d62828")):
        subset = items_df[items_df["restaurant"] == restaurant]
        axis.scatter(
            subset["calories"],
            subset["fat_g"],
            alpha=0.55,
            label=restaurant,
            color=color,
        )
    axis.set_title("Calories and fat relationship")
    axis.set_xlabel("Calories")
    axis.set_ylabel("Fat (g)")
    axis.legend()
    figure.tight_layout()
    chart_path = output_path / "calories_vs_fat.png"
    figure.savefig(chart_path, dpi=150)
    plt.close(figure)
    return str(chart_path)
