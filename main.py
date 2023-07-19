from typing import Optional
from fastapi import FastAPI
from pgml import Database
import os

local_pgml = "postgres://postgres@127.0.0.1:5433/pgml_development"

app = FastAPI()
database = Database(os.environ.get("PGML_DATABASE_URL", local_pgml))


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


@app.get("/healthcheck")
async def healthcheck():
    await database.create_or_get_collection("test")
    return {"message": "OK"}
