from pathlib import Path
import csv

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    date_format,
    to_timestamp,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw" / "olist"
BATCH_DIR = PROJECT_ROOT / "data" / "batches"


def create_spark_session():
    return (
        SparkSession.builder
        .appName("OlistBatchGenerator")
        .master("local[*]")
        .getOrCreate()
    )


def write_dataframe_to_csv(df, output_dir: Path):
    """
    Write a Spark DataFrame to a single CSV file using Python's
    CSV writer instead of Spark's Hadoop-based file writer.

    This avoids the Windows winutils.exe dependency.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "data.csv"

    columns = df.columns

    with output_file.open(
        mode="w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow(columns)

        for row in df.toLocalIterator():
            writer.writerow(
                [
                    None if value is None else value
                    for value in row
                ]
            )

    print(f"      Written: {output_file}")


def main():

    spark = create_spark_session()

    try:

        print("Reading Olist source data...")

        orders = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(RAW_DATA_DIR / "olist_orders_dataset.csv"))
        )

        order_items = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(RAW_DATA_DIR / "olist_order_items_dataset.csv"))
        )

        payments = (
            spark.read
            .option("header", True)
            .option("inferSchema", True)
            .csv(str(RAW_DATA_DIR / "olist_order_payments_dataset.csv"))
        )

        print("Source data loaded.")

        # ---------------------------------------------------------
        # Prepare order month
        # ---------------------------------------------------------

        orders = (
            orders
            .withColumn(
                "order_purchase_timestamp",
                to_timestamp(
                    col("order_purchase_timestamp")
                )
            )
            .withColumn(
                "batch_month",
                date_format(
                    col("order_purchase_timestamp"),
                    "yyyy-MM"
                )
            )
        )

        order_items = order_items.join(
            orders.select(
                "order_id",
                "batch_month"
            ),
            on="order_id",
            how="inner"
        )

        payments = payments.join(
            orders.select(
                "order_id",
                "batch_month"
            ),
            on="order_id",
            how="inner"
        )

        # ---------------------------------------------------------
        # Find chronological batches
        # ---------------------------------------------------------

        batch_months = [
            row["batch_month"]
            for row in (
                orders
                .select("batch_month")
                .distinct()
                .orderBy("batch_month")
                .collect()
            )
        ]

        print(f"Found {len(batch_months)} monthly batches.")

        # ---------------------------------------------------------
        # Generate each monthly batch
        # ---------------------------------------------------------

        for batch_month in batch_months:

            batch_id = f"batch_{batch_month.replace('-', '')}"

            print()
            print(f"Creating {batch_id}")

            batch_path = BATCH_DIR / batch_id

            # Filter this month's records
            batch_orders = (
                orders
                .filter(col("batch_month") == batch_month)
                .drop("batch_month")
            )

            order_ids = batch_orders.select("order_id")

            batch_items = (
                order_items
                .join(order_ids, on="order_id", how="inner")
                .drop("batch_month")
            )

            batch_payments = (
                payments
                .join(order_ids, on="order_id", how="inner")
                .drop("batch_month")
            )

            # -----------------------------------------------------
            # Write using Python instead of Spark .write.csv()
            # -----------------------------------------------------

            print("   Writing orders...")
            write_dataframe_to_csv(
                batch_orders,
                batch_path / "orders"
            )

            print("   Writing order items...")
            write_dataframe_to_csv(
                batch_items,
                batch_path / "order_items"
            )

            print("   Writing payments...")
            write_dataframe_to_csv(
                batch_payments,
                batch_path / "order_payments"
            )

            # -----------------------------------------------------
            # Counts
            # -----------------------------------------------------

            order_count = batch_orders.count()
            item_count = batch_items.count()
            payment_count = batch_payments.count()

            print(
                f"   Orders: {order_count}"
            )
            print(
                f"   Order items: {item_count}"
            )
            print(
                f"   Payments: {payment_count}"
            )

            print(f"   {batch_id} completed.")

        print()
        print("ALL BATCHES GENERATED SUCCESSFULLY.")

    finally:
        spark.stop()


if __name__ == "__main__":
    main()