def validate_data(data):

    required = [
        "customers",
        "orders",
        "order_items",
        "products",
        "sellers",
        "order_payments",
        "product_category_translation",
    ]

    for name in required:
        if name not in data:
            raise ValueError(f"Missing dataset: {name}")

        count = data[name].count()

        if count == 0:
            raise ValueError(
                f"Dataset contains no records: {name}"
            )

        print(f"{name}: {count:,} records")

    orders = data["orders"]
    items = data["order_items"]

    null_order_ids = (
        orders
        .filter("order_id IS NULL")
        .count()
    )

    if null_order_ids > 0:
        raise ValueError(
            f"Orders contains {null_order_ids} null order IDs"
        )

    null_item_order_ids = (
        items
        .filter("order_id IS NULL")
        .count()
    )

    if null_item_order_ids > 0:
        raise ValueError(
            f"Order items contains {null_item_order_ids} null order IDs"
        )

    print("Validation passed.")