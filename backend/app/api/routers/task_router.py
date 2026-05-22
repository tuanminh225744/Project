from fastapi import APIRouter, BackgroundTasks
from app.tasks.email_tasks import send_email_task
from app.schemas.task import SendEmailRequest, SendEmailResponse

router = APIRouter(prefix="/email-tasks", tags=["email-tasks"])

# Endpoint để gửi email bằng Celery
@router.post("/send-email", response_model=SendEmailResponse)
async def send_email(request: SendEmailRequest):
    # Gọi task Celery để gửi email
    send_email_task.delay(request.to_email, request.subject, request.body)
    return SendEmailResponse(message="Email is being sent in the background")

# Endpoint gửi email sử dụng BackgroundTasks
@router.post("/send-email-background", response_model=SendEmailResponse)
async def send_email_background(request: SendEmailRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_email_task.delay, request.to_email, request.subject, request.body)
    return SendEmailResponse(message="Email is being sent in the background")

# file này chỉ là file học, không phải file dự án