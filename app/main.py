from fastapi import FastAPI
from app.db.base import engine, Base
from app.api.routers.users import router as user_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello FastAPI"}

# Include user router
app.include_router(user_router)