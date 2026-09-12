from pyspark.sql import SparkSession
from .config import RAW_DATA_DIR
from .schemas import (
    CUSTOMERS_SCHEMA,
    ORDERS_SCHEMA,
    ORDER_ITEMS_SCHEMA,
    PRODUCTS_SCHEMA,
    SELLERS_SCHEMA,
    ORDER_PAYMENTS_SCHEMA,
    CATEGORY_TRANSLATION_SCHEMA,
)


def create_spark_session():
    return (
        SparkSession.builder
        .appName("OlistDataPipeline")
        .master("local[*]")
        .getOrCreate()
    )


def read_csv(spark, filename, schema):
    path = str(RAW_DATA_DIR / filename)

    return (
        spark.read
        .option("header", True)
        .option("inferSchema", False)
        .schema(schema)
        .csv(path)
    )


def extract_data(spark):
    return {
        "customers": read_csv(
            spark,
            "olist_customers_dataset.csv",
            CUSTOMERS_SCHEMA,
        ),
        "orders": read_csv(
            spark,
            "olist_orders_dataset.csv",
            ORDERS_SCHEMA,
        ),
        "order_items": read_csv(
            spark,
            "olist_order_items_dataset.csv",
            ORDER_ITEMS_SCHEMA,
        ),
        "products": read_csv(
            spark,
            "olist_products_dataset.csv",
            PRODUCTS_SCHEMA,
        ),
        "sellers": read_csv(
            spark,
            "olist_sellers_dataset.csv",
            SELLERS_SCHEMA,
        ),
        "order_payments": read_csv(
            spark,
            "olist_order_payments_dataset.csv",
            ORDER_PAYMENTS_SCHEMA,
        ),
        "product_category_translation": read_csv(
            spark,
            "product_category_name_translation.csv",
            CATEGORY_TRANSLATION_SCHEMA,
        ),
    }