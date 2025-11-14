# notification-service/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app

ENV SMTP_HOST=pro.turbo-smtp.com \
    SMTP_PORT=465 \
    FROM_EMAIL=noreply@example.com \
    TO_ADMIN=admin@example.com

EXPOSE 8080
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
