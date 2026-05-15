from app.celery_app import celery_app
import time


@celery_app.task
def send_email_task(to_email: str, subject: str, body: str):
    time.sleep(2)  # Giả lập độ trễ khi gửi email
    print(f"Sending email to {to_email} with subject '{subject}' and body '{body}'")
    return True