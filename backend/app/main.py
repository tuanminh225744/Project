from fastapi import FastAPI
from app.db.base import engine, Base
from app.api.routers.user_router import router as user_router
from app.api.routers.auth_router import router as auth_router
from app.api.routers.task_router import router as email_task_router
from app.api.routers.project_router import router as project_router
from app.api.routers.project_member_router import router as project_member_router
from app.api.routers.task_management_router import router as task_management_router
from app.api.routers.task_comment_router import router as task_comment_router
from app.core.exception_handlers import register_exception_handlers
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React Vite
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "Hello FastAPI"}

# Include routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(project_router)
app.include_router(project_member_router)
app.include_router(task_management_router)
app.include_router(task_comment_router)
app.include_router(email_task_router)
