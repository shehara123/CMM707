CREATE TABLE IF NOT EXISTS orders (
  order_id VARCHAR(20) PRIMARY KEY,
  customer_name VARCHAR(100),
  items JSON,
  total_price NUMERIC(10,2),
  order_date DATE
);

