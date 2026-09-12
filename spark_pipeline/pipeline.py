import argparse
from datetime import datetime
from pathlib import Path

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp

from .load import (
    initialize_database,
    dataframe_to_mysql,
    create_batch_record,
    mark_batch_success,
    mark_batch_failed,
    update_watermark,
    refresh_analytics,
)

from .config import BATCH_DIR


def create_spark_session():
    return (
        SparkSession.builder
        .appName("OlistIncrementalPipeline")
        .master("local[*]")
        .getOrCreate()
    )


def read_batch(spark, batch_id):
    batch_path = BATCH_DIR / batch_id

    if not batch_path.exists():
        raise FileNotFoundError(
            f"Batch does not exist: {batch_path}"
        )

    orders_path = batch_path / "orders" / "data.csv"
    items_path = batch_path / "order_items" / "data.csv"
    payments_path = batch_path / "order_payments" / "data.csv"

    orders = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(orders_path))
    )

    order_items = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(items_path))
    )

    payments = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(str(payments_path))
    )

    return orders, order_items, payments


def process_batch(batch_id):

    spark = create_spark_session()

    try:
        print("=" * 60)
        print(f"PROCESSING BATCH: {batch_id}")
        print("=" * 60)

        initialize_database()

        orders, order_items, payments = read_batch(
            spark,
            batch_id
        )

        # Normalize timestamps
        timestamp_columns = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]

        for column_name in timestamp_columns:
            if column_name in orders.columns:
                orders = orders.withColumn(
                    column_name,
                    to_timestamp(col(column_name))
                )

        if "shipping_limit_date" in order_items.columns:
            order_items = order_items.withColumn(
                "shipping_limit_date",
                to_timestamp(col("shipping_limit_date"))
            )

        # Add metadata
        orders = orders.withColumn(
            "created_at",
            col("order_purchase_timestamp")
        )

        orders = orders.withColumn(
            "batch_id",
            col("order_purchase_timestamp").cast("string")
        )

        orders = orders.withColumn(
            "batch_id",
            col("batch_id")
        )

        # Use the actual batch ID
        from pyspark.sql.functions import lit

        orders = orders.withColumn(
            "batch_id",
            lit(batch_id)
        )

        order_items = order_items.withColumn(
            "created_at",
            lit(datetime.now())
        )

        order_items = order_items.withColumn(
            "batch_id",
            lit(batch_id)
        )

        payments = payments.withColumn(
            "created_at",
            lit(datetime.now())
        )

        payments = payments.withColumn(
            "batch_id",
            lit(batch_id)
        )

        # ------------------------------------------------------
        # Validation
        # ------------------------------------------------------

        order_count = orders.count()
        item_count = order_items.count()
        payment_count = payments.count()

        print(f"Orders received:       {order_count}")
        print(f"Order items received:  {item_count}")
        print(f"Payments received:     {payment_count}")

        if order_count == 0:
            raise ValueError(
                f"{batch_id} contains no orders."
            )

        null_order_ids = orders.filter(
            col("order_id").isNull()
        ).count()

        if null_order_ids > 0:
            raise ValueError(
                f"{batch_id} contains {null_order_ids} "
                "orders with NULL order_id."
            )

        # ------------------------------------------------------
        # Batch metadata
        # ------------------------------------------------------

        min_event = orders.select(
            "order_purchase_timestamp"
        ).first()[0]

        max_event = orders.select(
            "order_purchase_timestamp"
        ).first()[0]

        min_event = orders.agg(
            {"order_purchase_timestamp": "min"}
        ).first()[0]

        max_event = orders.agg(
            {"order_purchase_timestamp": "max"}
        ).first()[0]

        create_batch_record(
            batch_id=batch_id,
            min_event_date=min_event,
            max_event_date=max_event,
            records_received=order_count
            + item_count
            + payment_count,
        )

        # ------------------------------------------------------
        # Load MySQL
        # ------------------------------------------------------

        print("Loading orders...")
        dataframe_to_mysql(
            orders,
            "orders",
            orders.columns
        )

        print("Loading order items...")
        dataframe_to_mysql(
            order_items,
            "order_items",
            order_items.columns
        )

        print("Loading payments...")
        dataframe_to_mysql(
            payments,
            "order_payments",
            payments.columns
        )

        # Refresh analytics AFTER core data is loaded
        print("Refreshing analytics...")
        refresh_analytics()

        # ------------------------------------------------------
        # Success
        # ------------------------------------------------------

        mark_batch_success(
            batch_id=batch_id,
            records_processed=(
                order_count
                + item_count
                + payment_count
            ),
        )

        update_watermark(
            pipeline_name="olist_incremental",
            watermark_value=max_event,
        )

        print()
        print("=" * 60)
        print(f"{batch_id} COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as exc:

        print()
        print(f"ERROR: {exc}")

        try:
            mark_batch_failed(
                batch_id=batch_id,
                error_message=str(exc),
            )
        except Exception:
            pass

        raise

    finally:
        spark.stop()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Process one Olist incremental batch."
    )

    parser.add_argument(
        "--batch-id",
        required=True,
        help="Example: batch_201609"
    )

    args = parser.parse_args()

    process_batch(args.batch_id)