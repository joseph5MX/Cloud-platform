from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import session
from .database import engine, Base, get_db
from . import models 

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Local Cloud Platform API", lifespan=lifespan)

@app.get("/health")
def health(db: session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connect"}
