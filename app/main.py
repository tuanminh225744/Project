from fastapi import FastAPI
from app.db.base import engine, Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello FastAPI"}