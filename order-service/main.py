from fastapi import FastAPI
import psycopg2
import os
import json

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "ordersdb")
DB_USER = os.getenv("DB_USER", "orderuser")
DB_PASS = os.getenv("DB_PASS", "orderpass")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/orders")
def get_orders():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM orders;")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    results = []
    for r in rows:
        try:
            items = json.loads(r[2]) if isinstance(r[2], str) else r[2]
        except Exception as e:
            items = []
        results.append({
            "order_id": r[0],
            "customer_name": r[1],
            "items": items,
            "total_price": float(r[3]),
            "order_date": str(r[4])
        })

    return results

@app.post("/orders")
def add_order(order: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (order_id, customer_name, items, total_price, order_date) VALUES (%s, %s, %s, %s, %s)",
        (
            order["order_id"],
            order["customer_name"],
            json.dumps(order["items"]),
            order["total_price"],
            order["order_date"]
        )
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Order saved"}

