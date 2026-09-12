from pyspark.sql import functions as F


def add_metadata(df, batch_id):
    return (
        df
        .withColumn("created_at", F.current_timestamp())
        .withColumn("batch_id", F.lit(batch_id))
    )


def transform_data(data, batch_id):

    customers = add_metadata(data["customers"], batch_id)

    orders = add_metadata(data["orders"], batch_id)

    order_items = add_metadata(
        data["order_items"],
        batch_id
    )

    products = add_metadata(
        data["products"],
        batch_id
    )

    sellers = add_metadata(
        data["sellers"],
        batch_id
    )

    order_payments = add_metadata(
        data["order_payments"],
        batch_id
    )

    category_translation = data[
        "product_category_translation"
    ]

    return {
        "customers": customers,
        "orders": orders,
        "order_items": order_items,
        "products": products,
        "sellers": sellers,
        "order_payments": order_payments,
        "product_category_translation": category_translation,
    }


def create_analytics(data):

    orders = data["orders"]
    items = data["order_items"]

    monthly_sales = (
        orders
        .join(items, "order_id", "inner")
        .withColumn(
            "month",
            F.date_format(
                "order_purchase_timestamp",
                "yyyy-MM"
            )
        )
        .groupBy("month")
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.count("*").alias("total_items"),
            F.round(F.sum("price"), 2).alias("gross_revenue"),
            F.round(F.sum("freight_value"), 2).alias("total_freight"),
        )
        .withColumn(
            "average_order_value",
            F.round(
                F.col("gross_revenue") /
                F.col("total_orders"),
                2
            )
        )
    )

    category_performance = (
        items
        .join(
            data["products"],
            "product_id",
            "left"
        )
        .groupBy(
            F.coalesce(
                F.col("product_category_name"),
                F.lit("unknown")
            ).alias("category")
        )
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.count("*").alias("total_items"),
            F.round(F.sum("price"), 2).alias("gross_revenue"),
            F.round(F.avg("price"), 2).alias("average_item_price"),
        )
    )

    seller_performance = (
        items
        .groupBy("seller_id")
        .agg(
            F.countDistinct("order_id").alias("total_orders"),
            F.count("*").alias("total_items"),
            F.round(F.sum("price"), 2).alias("gross_revenue"),
            F.round(
                F.sum("price") /
                F.countDistinct("order_id"),
                2
            ).alias("average_order_value"),
        )
    )

    return {
        "monthly_sales_summary": monthly_sales,
        "category_performance": category_performance,
        "seller_performance": seller_performance,
    }