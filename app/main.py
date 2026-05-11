from fastapi import FastAPI
from app.db.base import engine, Base
from app.api.routers.user_router import router as user_router
from app.api.routers.auth_router import router as auth_router

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Hello FastAPI"}

# Include user router
app.include_router(user_router)
app.include_router(auth_router)