import os

from fastapi import FastAPI

app = FastAPI()
APP_ENV = os.getenv("APP_ENV", "local")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"status": "ready"}


@app.get("/")
def root():
    return {"service": "sre-platform", "environment": APP_ENV}