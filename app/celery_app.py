from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("REDIS_URL"),
    backend=os.getenv("REDIS_URL"),
    include=["app.tasks.email_tasks"]
)

celery_app.conf.update(
    task_serializer="json",     # Sử dụng JSON để serialize task
    accept_content=["json"],    # Chỉ chấp nhận định dạng JSON
    result_serializer="json",   # Sử dụng JSON để serialize kết quả
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,            
)