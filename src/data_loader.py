"""Helpers for loading restaurant nutrition datasets."""

from pathlib import Path
from typing import Optional

import pandas as pd
from pyspark.sql import DataFrame, SparkSession


def load_csv_if_present(
    spark: SparkSession, file_path: str, dataset_label: str
) -> Optional[DataFrame]:
    """Load a CSV with a header if it exists; otherwise return None."""
    path = Path(file_path)

    if not path.exists():
        print(f"{dataset_label} dataset not found: {path}")
        return None

    pandas_df = pd.read_csv(path)
    df = spark.createDataFrame(pandas_df)

    print(f"\n{dataset_label} dataset")
    print(f"Rows: {df.count()}")
    print(f"Columns: {len(df.columns)}")
    df.printSchema()
    df.show(5, truncate=False)
    return df
