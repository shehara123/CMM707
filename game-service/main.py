from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

# DB connection settings from environment variables
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "gamesdb")
DB_USER = os.getenv("DB_USER", "gameuser")
DB_PASS = os.getenv("DB_PASS", "gamepass")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.get("/games")
def get_games():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1], "category": r[2], "price": r[3], "release_date": r[4]} for r in rows]

@app.post("/games")
def add_game(game: dict):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO games (name, category, price, release_date) VALUES (%s, %s, %s, %s)",
                (game["name"], game["category"], game["price"], game["release_date"]))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Game added successfully"}

