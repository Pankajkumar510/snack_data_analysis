"""Nutritional comparison and profiling functions."""

import math
from typing import Dict

import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql import functions as F


METRICS = ["calories", "fat_g", "carbs_g", "protein_g", "sodium_mg", "sugars_g"]


def compare_restaurants(standardized_df: DataFrame) -> pd.DataFrame:
    """Return item counts and average nutrition values by restaurant."""
    summary = (
        standardized_df.groupBy("restaurant")
        .agg(
            F.count("*").alias("items"),
            *[F.round(F.avg(metric), 2).alias(f"avg_{metric}") for metric in METRICS],
        )
        .orderBy("restaurant")
    )
    return summary.toPandas()


def summarize_categories(standardized_df: DataFrame) -> pd.DataFrame:
    """Return item counts and average calories by source category."""
    return (
        standardized_df.groupBy("restaurant", "category")
        .agg(
            F.count("*").alias("items"),
            F.round(F.avg("calories"), 2).alias("avg_calories"),
            F.round(F.avg("fat_g"), 2).alias("avg_fat_g"),
            F.round(F.avg("sugars_g"), 2).alias("avg_sugars_g"),
        )
        .orderBy("restaurant", F.desc("items"))
        .toPandas()
    )


def item_data(standardized_df: DataFrame) -> pd.DataFrame:
    """Return the cleaned item-level data for export."""
    return standardized_df.orderBy("restaurant", "calories", "item").toPandas()


def descriptive_statistics(standardized_df: DataFrame) -> pd.DataFrame:
    """Return count, mean, median, standard deviation, minimum, and maximum."""
    rows = []
    for restaurant in ("Starbucks", "McDonald's"):
        restaurant_df = standardized_df.filter(F.col("restaurant") == restaurant)
        for metric in METRICS:
            result = restaurant_df.select(metric).where(F.col(metric).isNotNull()).agg(
                F.count(metric).alias("count"),
                F.round(F.avg(metric), 2).alias("mean"),
                F.round(F.expr(f"percentile_approx({metric}, 0.5)"), 2).alias("median"),
                F.round(F.stddev(metric), 2).alias("stddev"),
                F.round(F.min(metric), 2).alias("min"),
                F.round(F.max(metric), 2).alias("max"),
            ).first()
            rows.append(
                {
                    "restaurant": restaurant,
                    "metric": metric,
                    "count": result["count"],
                    "mean": result["mean"],
                    "median": result["median"],
                    "stddev": result["stddev"],
                    "min": result["min"],
                    "max": result["max"],
                }
            )
    return pd.DataFrame(rows)


def data_quality_summary(standardized_df: DataFrame) -> pd.DataFrame:
    """Return null and duplicate checks for the standardized data."""
    rows = []
    for restaurant in ("Starbucks", "McDonald's"):
        restaurant_df = standardized_df.filter(F.col("restaurant") == restaurant)
        total_rows = restaurant_df.count()
        distinct_rows = restaurant_df.dropDuplicates().count()
        null_values = sum(
            restaurant_df.filter(F.col(column).isNull()).count()
            for column in ["item", "category", *METRICS]
        )
        rows.append(
            {
                "restaurant": restaurant,
                "rows": total_rows,
                "duplicate_rows": total_rows - distinct_rows,
                "null_values": null_values,
            }
        )
    return pd.DataFrame(rows)


def relationship_summary(standardized_df: DataFrame) -> pd.DataFrame:
    """Return Pearson correlations between calories and other nutrition measures."""
    rows = []
    for restaurant in ("Starbucks", "McDonald's"):
        restaurant_df = standardized_df.filter(F.col("restaurant") == restaurant)
        for metric in ["fat_g", "carbs_g", "protein_g", "sodium_mg", "sugars_g"]:
            correlation = restaurant_df.stat.corr("calories", metric)
            rows.append(
                {
                    "restaurant": restaurant,
                    "relationship": f"calories vs {metric}",
                    "pearson_correlation": (
                        None if math.isnan(correlation) else round(correlation, 3)
                    ),
                }
            )
    return pd.DataFrame(rows)


def calculate_findings(summary: pd.DataFrame) -> Dict[str, str]:
    """Create concise findings from the restaurant summary."""
    indexed = summary.set_index("restaurant")
    findings = {}
    metric_labels = {
        "avg_calories": "calories",
        "avg_fat_g": "fat",
        "avg_sugars_g": "sugars",
        "avg_sodium_mg": "sodium",
    }
    for metric, label in metric_labels.items():
        higher = indexed[metric].idxmax()
        lower = indexed[metric].idxmin()
        findings[label] = (
            f"{higher} has the higher average {label} "
            f"({indexed.loc[higher, metric]:.2f}), while {lower} is lower "
            f"({indexed.loc[lower, metric]:.2f})."
        )
    return findings
