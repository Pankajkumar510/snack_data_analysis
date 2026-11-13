"""Data-cleaning and schema-standardization functions."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def _numeric(column):
    """Convert numeric-looking strings, percentages, and dashes to doubles."""
    return F.regexp_replace(F.trim(F.col(column).cast("string")), "[^0-9.-]", "").cast(
        "double"
    )


def standardize_datasets(starbucks_df: DataFrame, mcdonalds_df: DataFrame) -> DataFrame:
    """Map both source schemas to a shared nutrition schema."""
    starbucks = starbucks_df.select(
        F.lit("Starbucks").alias("restaurant"),
        F.col("Beverage").alias("item"),
        F.col("Beverage_category").alias("category"),
        F.col("Beverage_prep").alias("serving_size"),
        _numeric("Calories").alias("calories"),
        _numeric("Total Fat (g)").alias("fat_g"),
        _numeric("Total Carbohydrates (g)").alias("carbs_g"),
        _numeric("Protein (g)").alias("protein_g"),
        _numeric("Sodium (mg)").alias("sodium_mg"),
        _numeric("Sugars (g)").alias("sugars_g"),
    )
    mcdonalds = mcdonalds_df.select(
        F.lit("McDonald's").alias("restaurant"),
        F.col("Item").alias("item"),
        F.col("Category").alias("category"),
        F.col("Serving Size").alias("serving_size"),
        _numeric("Calories").alias("calories"),
        _numeric("Total Fat").alias("fat_g"),
        _numeric("Carbohydrates").alias("carbs_g"),
        _numeric("Protein").alias("protein_g"),
        _numeric("Sodium").alias("sodium_mg"),
        _numeric("Sugars").alias("sugars_g"),
    )
    return starbucks.unionByName(mcdonalds)
