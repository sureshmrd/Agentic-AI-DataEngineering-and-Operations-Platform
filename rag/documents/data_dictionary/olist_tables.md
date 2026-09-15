# Olist Data Dictionary

## customers

The customers table represents customers associated with Olist orders.

It contains customer-level identifiers and customer location information.

## orders

The orders table represents customer orders.

An order contains information about its lifecycle, including timestamps and
order status.

## order_items

The order_items table represents items associated with customer orders.

An order can contain multiple order items.

Item-level commercial information includes product and seller references,
price, and freight value.

## products

The products table represents products sold through the marketplace.

It contains product-related attributes.

## sellers

The sellers table represents marketplace sellers.

Seller information is used when analyzing seller performance.

## order_payments

The order_payments table represents payment information associated with
orders.

## product_category_translation

The product_category_translation table contains translated product category
names.