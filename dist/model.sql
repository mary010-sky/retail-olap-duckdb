-- Reproducible synthetic star schema. Monetary values use exact decimals.
CREATE TABLE dim_region AS SELECT * FROM (VALUES
 (0,'Peru'),(1,'Chile'),(2,'Colombia'),(3,'Mexico'),(4,'Argentina')) t(region_id,region);
CREATE TABLE dim_product AS SELECT * FROM (VALUES
 (0,'Electronics'),(1,'Home'),(2,'Sports'),(3,'Books')) t(product_id,category);
CREATE TABLE dim_date AS SELECT CAST(d AS DATE) AS sale_date,
 year(d) AS year, quarter(d) AS quarter, month(d) AS month
 FROM generate_series(DATE '2024-01-01',DATE '2025-12-31',INTERVAL 1 DAY) t(d);
CREATE TABLE fact_sales AS
 SELECT n AS sale_id, DATE '2024-01-01' + CAST((n * 19) % 731 AS INTEGER) AS sale_date,
 CAST((n * 7) % 5 AS INTEGER) AS region_id,
 CAST((n // 5) % 4 AS INTEGER) AS product_id,
 CAST(1 + (n // 20) % 5 AS INTEGER) AS quantity,
 CAST((1000 + (n * 37) % 49000) / 100.0 AS DECIMAL(12,2)) AS unit_price
 FROM generate_series(1,100000) t(n);
CREATE VIEW sales AS SELECT f.*, r.region,p.category,d.year,d.quarter,d.month,
 CAST(f.quantity*f.unit_price AS DECIMAL(14,2)) AS revenue
 FROM fact_sales f JOIN dim_region r USING(region_id)
 JOIN dim_product p USING(product_id) JOIN dim_date d USING(sale_date);
