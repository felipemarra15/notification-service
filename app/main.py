from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import smtplib, ssl, os

app = FastAPI()

class NotifyPayload(BaseModel):
    nombre: str
    mail: EmailStr
    telefono: str

SMTP_HOST = os.getenv("SMTP_HOST", "pro.turbo-smtp.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")
TO_ADMIN   = os.getenv("TO_ADMIN", "admin@example.com")  # destinatario de notificaciones

@app.post("/notify")
def notify(payload: NotifyPayload):
    subject = "Nuevo usuario creado"
    body = (
        f"Se registró un usuario:\n"
        f"Nombre: {payload.nombre}\n"
        f"Email: {payload.mail}\n"
        f"Teléfono: {payload.telefono}\n"
    )
    msg = f"Subject: {subject}\r\nFrom: {FROM_EMAIL}\r\nTo: {TO_ADMIN}\r\n\r\n{body}"

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, [TO_ADMIN], msg)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"SMTP error: {e}")

    return {"status": "ok"}
