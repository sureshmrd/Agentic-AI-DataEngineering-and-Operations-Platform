import mysql.connector

from .config import MYSQL_CONFIG


def get_connection():
    return mysql.connector.connect(**MYSQL_CONFIG)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    statements = [

        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id VARCHAR(50) PRIMARY KEY,
            customer_unique_id VARCHAR(50),
            customer_zip_code_prefix INT,
            customer_city VARCHAR(100),
            customer_state CHAR(2),
            created_at DATETIME,
            batch_id VARCHAR(50)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id VARCHAR(50) PRIMARY KEY,
            customer_id VARCHAR(50),
            order_status VARCHAR(30),
            order_purchase_timestamp DATETIME,
            order_approved_at DATETIME,
            order_delivered_carrier_date DATETIME,
            order_delivered_customer_date DATETIME,
            order_estimated_delivery_date DATETIME,
            created_at DATETIME,
            batch_id VARCHAR(50)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS order_items (
            order_id VARCHAR(50),
            order_item_id INT,
            product_id VARCHAR(50),
            seller_id VARCHAR(50),
            shipping_limit_date DATETIME,
            price DECIMAL(12,2),
            freight_value DECIMAL(12,2),
            created_at DATETIME,
            batch_id VARCHAR(50),
            PRIMARY KEY (order_id, order_item_id)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(50) PRIMARY KEY,
            product_category_name VARCHAR(150),
            product_name_length INT,
            product_description_length INT,
            product_photos_qty INT,
            product_weight_g INT,
            product_length_cm INT,
            product_height_cm INT,
            product_width_cm INT,
            created_at DATETIME,
            batch_id VARCHAR(50)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS sellers (
            seller_id VARCHAR(50) PRIMARY KEY,
            seller_zip_code_prefix INT,
            seller_city VARCHAR(100),
            seller_state CHAR(2),
            created_at DATETIME,
            batch_id VARCHAR(50)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS order_payments (
            order_id VARCHAR(50),
            payment_sequential INT,
            payment_type VARCHAR(30),
            payment_installments INT,
            payment_value DECIMAL(12,2),
            created_at DATETIME,
            batch_id VARCHAR(50),
            PRIMARY KEY (order_id, payment_sequential)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS product_category_translation (
            product_category_name VARCHAR(150) PRIMARY KEY,
            product_category_name_english VARCHAR(150)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS pipeline_batches (
            batch_id VARCHAR(50) PRIMARY KEY,
            source_name VARCHAR(100),
            batch_date DATE,
            min_event_date DATETIME,
            max_event_date DATETIME,
            records_received INT,
            records_processed INT,
            records_failed INT,
            status VARCHAR(30),
            started_at DATETIME,
            completed_at DATETIME,
            error_message TEXT
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS pipeline_watermarks (
            pipeline_name VARCHAR(100) PRIMARY KEY,
            source_name VARCHAR(100),
            watermark_column VARCHAR(100),
            last_processed_value DATETIME,
            updated_at DATETIME
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS monthly_sales_summary (
            month VARCHAR(7) PRIMARY KEY,
            total_orders INT,
            total_items INT,
            gross_revenue DECIMAL(14,2),
            total_freight DECIMAL(14,2),
            average_order_value DECIMAL(14,2)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS category_performance (
            category VARCHAR(150) PRIMARY KEY,
            total_orders INT,
            total_items INT,
            gross_revenue DECIMAL(14,2),
            average_item_price DECIMAL(14,2)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS seller_performance (
            seller_id VARCHAR(50) PRIMARY KEY,
            total_orders INT,
            total_items INT,
            gross_revenue DECIMAL(14,2),
            average_order_value DECIMAL(14,2)
        )
        """,
    ]

    for statement in statements:
        cursor.execute(statement)

    connection.commit()
    cursor.close()
    connection.close()

    print("MySQL tables initialized.")


def dataframe_to_mysql(df, table_name, columns):

    connection = get_connection()
    cursor = connection.cursor()

    rows = df.select(columns).collect()

    if not rows:
        cursor.close()
        connection.close()
        return 0

    placeholders = ", ".join(["%s"] * len(columns))

    column_names = ", ".join(columns)

    query = f"""
        INSERT IGNORE INTO {table_name}
        ({column_names})
        VALUES ({placeholders})
    """

    values = []

    for row in rows:
        values.append(
            tuple(row[col] for col in columns)
        )

    cursor.executemany(query, values)

    connection.commit()

    processed = cursor.rowcount

    cursor.close()
    connection.close()

    print(f"{table_name}: {processed:,} rows loaded")

    return processed


def create_batch_record(
    batch_id,
    min_event_date,
    max_event_date,
    records_received,
):
    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO pipeline_batches (
            batch_id,
            source_name,
            batch_date,
            min_event_date,
            max_event_date,
            records_received,
            records_processed,
            records_failed,
            status,
            started_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            0,
            0,
            'RUNNING',
            NOW()
        )
        ON DUPLICATE KEY UPDATE
            status = 'RUNNING',
            started_at = NOW(),
            error_message = NULL
    """

    batch_date = min_event_date.date()

    cursor.execute(
        query,
        (
            batch_id,
            "olist",
            batch_date,
            min_event_date,
            max_event_date,
            records_received,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()


def mark_batch_success(
    batch_id,
    records_processed,
):
    connection = get_connection()

    cursor = connection.cursor()

    query = """
        UPDATE pipeline_batches
        SET
            status = 'SUCCESS',
            records_processed = %s,
            completed_at = NOW(),
            error_message = NULL
        WHERE batch_id = %s
    """

    cursor.execute(
        query,
        (
            records_processed,
            batch_id,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()


def mark_batch_failed(
    batch_id,
    error_message,
):
    connection = get_connection()

    cursor = connection.cursor()

    query = """
        UPDATE pipeline_batches
        SET
            status = 'FAILED',
            records_failed = records_received,
            completed_at = NOW(),
            error_message = %s
        WHERE batch_id = %s
    """

    cursor.execute(
        query,
        (
            error_message[:1000],
            batch_id,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()


def update_watermark(
    pipeline_name,
    watermark_value,
):
    connection = get_connection()

    cursor = connection.cursor()

    query = """
        INSERT INTO pipeline_watermarks (
            pipeline_name,
            source_name,
            watermark_column,
            last_processed_value,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            NOW()
        )
        ON DUPLICATE KEY UPDATE
            last_processed_value = %s,
            updated_at = NOW()
    """

    cursor.execute(
        query,
        (
            pipeline_name,
            "olist",
            "order_purchase_timestamp",
            watermark_value,
            watermark_value,
        ),
    )

    connection.commit()

    cursor.close()
    connection.close()


def refresh_analytics():
    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Monthly Sales Summary
    # -----------------------------
    cursor.execute("DELETE FROM monthly_sales_summary")

    cursor.execute("""
        INSERT INTO monthly_sales_summary (
            month,
            total_orders,
            total_items,
            gross_revenue,
            total_freight,
            average_order_value
        )
        SELECT
            DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
            COUNT(DISTINCT o.order_id) AS total_orders,
            COUNT(oi.order_item_id) AS total_items,
            COALESCE(SUM(oi.price), 0) AS gross_revenue,
            COALESCE(SUM(oi.freight_value), 0) AS total_freight,
            COALESCE(
                SUM(oi.price) / NULLIF(COUNT(DISTINCT o.order_id), 0),
                0
            ) AS average_order_value
        FROM orders o
        JOIN order_items oi
            ON o.order_id = oi.order_id
        GROUP BY DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m')
        ORDER BY month
    """)

    # -----------------------------
    # Category Performance
    # -----------------------------
    cursor.execute("DELETE FROM category_performance")

    cursor.execute("""
        INSERT INTO category_performance (
            category,
            total_orders,
            total_items,
            gross_revenue,
            average_item_price
        )
        SELECT
            COALESCE(p.product_category_name, 'unknown') AS category,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            COUNT(oi.order_item_id) AS total_items,
            COALESCE(SUM(oi.price), 0) AS gross_revenue,
            COALESCE(AVG(oi.price), 0) AS average_item_price
        FROM order_items oi
        LEFT JOIN products p
            ON oi.product_id = p.product_id
        GROUP BY COALESCE(p.product_category_name, 'unknown')
    """)

    # -----------------------------
    # Seller Performance
    # -----------------------------
    cursor.execute("DELETE FROM seller_performance")

    cursor.execute("""
        INSERT INTO seller_performance (
            seller_id,
            total_orders,
            total_items,
            gross_revenue,
            average_order_value
        )
        SELECT
            oi.seller_id,
            COUNT(DISTINCT oi.order_id) AS total_orders,
            COUNT(oi.order_item_id) AS total_items,
            COALESCE(SUM(oi.price), 0) AS gross_revenue,
            COALESCE(
                SUM(oi.price) / NULLIF(COUNT(DISTINCT oi.order_id), 0),
                0
            ) AS average_order_value
        FROM order_items oi
        GROUP BY oi.seller_id
    """)

    connection.commit()

    cursor.close()
    connection.close()

    print("Analytics tables refreshed successfully.")