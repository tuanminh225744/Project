from fastapi import FastAPI
from app.db.base import engine, Base
from app.api.routers.user_router import router as user_router
from app.api.routers.auth_router import router as auth_router
from app.api.routers.task_router import router as task_router

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Hello FastAPI"}

# Include user router
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(task_router)