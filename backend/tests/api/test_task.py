import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_send_email_task(client: AsyncClient):
    response = await client.post("/email-tasks/send-email", json={
        "to_email": "test@example.com",
        "subject": "Test Email",
        "body": "This is a test email."
    })
    print("Response:", response.json())
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_send_email_background_task(client: AsyncClient):
    response = await client.post("/email-tasks/send-email-background", json={
        "to_email": "test@example.com",
        "subject": "Test Email",
        "body": "This is a test email."
    })
    print("Response:", response.json())
    assert response.status_code == 200