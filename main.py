"""Entry point for the Starbucks vs McDonald's Snack Analysis project."""

import os
import sys
from pathlib import Path

from pyspark.sql import SparkSession

from src.analysis import (
    calculate_findings,
    compare_restaurants,
    data_quality_summary,
    descriptive_statistics,
    item_data,
    relationship_summary,
    summarize_categories,
)
from src.data_cleaning import standardize_datasets
from src.data_loader import load_csv_if_present
from src.visualization import create_comparison_charts, create_relationship_chart


ROOT = Path(__file__).resolve().parent


def create_spark_session() -> SparkSession:
    """Create a local Spark session."""
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)
    return (
        SparkSession.builder
        .appName("Starbucks_McDonalds_Snack_Analysis")
        .master("local[*]")
        .config("spark.pyspark.python", sys.executable)
        .getOrCreate()
    )


def main() -> None:
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    print("=" * 55)
    print("Starbucks vs McDonald's Snack Analysis")
    print("=" * 55)
    print(f"Spark version: {spark.version}")

    # Smoke test: illustrative data only, not actual restaurant nutrition data.
    sample_data = [
        ("Starbucks", "Sample sandwich", 350, 15, 30),
        ("McDonalds", "Sample burger", 500, 25, 45),
        ("Starbucks", "Sample salad", 250, 10, 20),
        ("McDonalds", "Sample fries", 320, 16, 40),
    ]
    sample_columns = ["Restaurant", "Food_Item", "Calories", "Fat", "Carbohydrates"]
    sample_df = spark.createDataFrame(sample_data, sample_columns)

    print("\nPySpark smoke test (illustrative rows only):")
    sample_df.show(truncate=False)

    print("\nChecking for your actual CSV datasets...")
    starbucks_df = load_csv_if_present(
        spark, str(ROOT / "dataset/raw/starbucks_drinkMenu_expanded.csv"), "Starbucks"
    )
    mcdonalds_df = load_csv_if_present(
        spark, str(ROOT / "dataset/raw/menu.csv"), "McDonald's"
    )

    if starbucks_df is None or mcdonalds_df is None:
        print(
            "\nDataset files not found yet. Put the CSV files in dataset/raw/ "
            "using the filenames shown in README.md."
        )
        return

    standardized_df = standardize_datasets(starbucks_df, mcdonalds_df).cache()
    summary_df = compare_restaurants(standardized_df)
    category_df = summarize_categories(standardized_df)
    items_df = item_data(standardized_df)
    statistics_df = descriptive_statistics(standardized_df)
    quality_df = data_quality_summary(standardized_df)
    relationships_df = relationship_summary(standardized_df)

    output_dir = ROOT / "output"
    charts = create_comparison_charts(summary_df, str(output_dir / "charts"))
    charts.append(create_relationship_chart(items_df, str(output_dir / "charts")))
    summary_df.to_csv(output_dir / "restaurant_summary.csv", index=False)
    category_df.to_csv(output_dir / "category_summary.csv", index=False)
    statistics_df.to_csv(output_dir / "descriptive_statistics.csv", index=False)
    quality_df.to_csv(output_dir / "data_quality_summary.csv", index=False)
    relationships_df.to_csv(output_dir / "relationship_summary.csv", index=False)
    items_df.to_csv(ROOT / "dataset/processed/standardized_nutrition.csv", index=False)

    findings = calculate_findings(summary_df)
    starbucks_items = int(
        summary_df.loc[summary_df.restaurant == "Starbucks", "items"].iloc[0]
    )
    mcdonalds_items = int(
        summary_df.loc[summary_df.restaurant == "McDonald's", "items"].iloc[0]
    )
    report_lines = [
        "# Starbucks vs McDonald's Nutrition Analysis",
        "",
        "## Executive summary",
        "",
        "This analysis standardizes nutrition fields from Starbucks drinks and the McDonald's menu",
        "and compares their descriptive nutrition profiles. McDonald's items have higher average",
        "calories, fat, and sodium in this sample, while Starbucks drinks have slightly higher",
        "average sugars. These results should not be interpreted as causal or like-for-like product",
        "comparisons because the source menus represent different product types and serving formats.",
        "",
        "## Methodology",
        "",
        "CSV files were loaded with PySpark, mapped to a shared schema, and numeric fields were",
        "explicitly converted to doubles. Dashes and non-numeric markers were treated as missing.",
        "All averages, medians, ranges, correlations, and category summaries were calculated from",
        "the standardized Spark dataset; only small result tables were converted to pandas for export",
        "and visualization.",
        "",
        "## Scope",
        "",
        "This report compares the expanded Starbucks drinks dataset with the McDonald's menu dataset.",
        "The source datasets contain different product types and serving conventions, so results are",
        "descriptive averages rather than like-for-like product comparisons.",
        "",
        "## Dataset coverage",
        "",
        f"- Starbucks items analyzed: {starbucks_items}",
        f"- McDonald's items analyzed: {mcdonalds_items}",
        "- Numeric values shown are averages across available, non-missing values.",
        "",
        "## Restaurant summary",
        "",
        "```text",
        summary_df.to_string(index=False),
        "```",
        "",
        "## Descriptive statistics",
        "",
        "```text",
        statistics_df.to_string(index=False),
        "```",
        "",
        "## Data quality checks",
        "",
        "```text",
        quality_df.to_string(index=False),
        "```",
        "",
        "## Relationship analysis",
        "",
        "Pearson correlation describes linear association only; it does not establish causation.",
        "",
        "```text",
        relationships_df.to_string(index=False),
        "```",
        "",
        "## Charts",
        "",
        "![Average calories](../output/charts/average_calories.png)",
        "",
        "![Average fat](../output/charts/average_fat.png)",
        "",
        "![Average sugars](../output/charts/average_sugars.png)",
        "",
        "![Average sodium](../output/charts/average_sodium.png)",
        "",
        "![Calories versus fat](../output/charts/calories_vs_fat.png)",
        "",
        "## Key findings",
        "",
    ]
    report_lines.extend(f"- {finding}" for finding in findings.values())
    report_lines.extend(
        [
            "",
            "## Outputs",
            "",
            "- [Restaurant summary](../output/restaurant_summary.csv)",
            "- [Category summary](../output/category_summary.csv)",
            "- [Descriptive statistics](../output/descriptive_statistics.csv)",
            "- [Relationship summary](../output/relationship_summary.csv)",
            "- [Standardized item data](../dataset/processed/standardized_nutrition.csv)",
            "",
            "## Challenges and resolutions",
            "",
            "- The supplied files used different column names and structures; a shared Spark schema was created.",
            "- Starbucks data contained dash markers and mixed numeric/string fields; these were converted to numeric values with invalid markers becoming null.",
            "- On Windows, Spark initially selected the wrong Python worker. The application now pins Spark workers to the active Python interpreter.",
            "",
            "## Limitations",
            "",
            "- The sample is a menu snapshot and may not represent every current product or serving configuration.",
            "- Starbucks drinks and the McDonald's menu are not matched by equivalent product or serving size.",
            "- Missing nutrient values are excluded from metric-specific averages.",
            "- Descriptive statistics and correlations show association in this dataset and cannot establish causation.",
        ]
    )
    report_path = ROOT / "reports" / "nutrition_analysis_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print("\nAnalysis complete.")
    print(f"Report: {report_path}")
    print(f"Charts created: {len(charts)}")

    spark.stop()


if __name__ == "__main__":
    main()
