import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

APP_ENV = os.getenv("APP_ENV", "local")
DATABASE_URL = os.getenv("DATABASE_URL")  # no default: credentials never live in code


def get_connection():
    # connect_timeout stops a request hanging forever if the database is down
    return psycopg.connect(DATABASE_URL, connect_timeout=2)


class ItemIn(BaseModel):
    # the shape of data a client must send to create an item
    name: str


@app.get("/health")
def health():
    # liveness: is the process alive? never checks the database
    return {"status": "ok"}


@app.get("/ready")
def ready():
    # readiness: can we actually serve traffic? check the database
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
    except Exception:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ready"}


@app.get("/")
def root():
    return {"service": "sre-platform", "environment": APP_ENV}


@app.post("/items", status_code=201)
def create_item(item: ItemIn):
    with get_connection() as conn:
        row = conn.execute(
            "INSERT INTO items (name) VALUES (%s) RETURNING id, name, created_at",
            (item.name,),
        ).fetchone()
    return {"id": row[0], "name": row[1], "created_at": row[2]}


@app.get("/items")
def list_items():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, created_at FROM items ORDER BY id"
        ).fetchall()

    items = []
    for row in rows:
        items.append({"id": row[0], "name": row[1], "created_at": row[2]})
    return items