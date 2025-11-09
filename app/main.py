# app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from email.message import EmailMessage
from email.utils import formataddr
from threading import Thread
import smtplib
import ssl
import os

app = FastAPI()

class NotifyPayload(BaseModel):
    nombre: str
    # Aceptamos 'mail' o 'email' (cualquiera)
    mail: Optional[EmailStr] = None
    email: Optional[EmailStr] = Field(default=None, alias="email")
    telefono: Optional[str] = None

# Vars de entorno
SMTP_HOST = os.getenv("SMTP_HOST", "pro.turbo-smtp.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")
TO_ADMIN   = os.getenv("TO_ADMIN", "admin@example.com")

# Modo consola para pruebas (no envía correo real)
SEND_MODE_CONSOLE = os.getenv("SEND_MODE", "").lower() == "console"

def _build_message(nombre: str, correo: str, telefono: Optional[str]) -> EmailMessage:
    subject = "Nuevo usuario creado"
    body = (
        f"Se registró un usuario:\n"
        f"Nombre: {nombre}\n"
        f"Email: {correo}\n"
        f"Teléfono: {telefono or ''}\n"
    )
    msg = EmailMessage()
    msg["From"] = formataddr(("Notificaciones", FROM_EMAIL))
    msg["To"] = TO_ADMIN
    msg["Subject"] = subject
    msg.set_content(body, subtype="plain", charset="utf-8")
    return msg

def _send_email(msg: EmailMessage):
    if SEND_MODE_CONSOLE:
        print("[NOTIFY][console] Enviaría email:\n", msg)
        return

    try:
        if SMTP_PORT == 465:
            # Timeout defensivo para que no quede bloqueado
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=15) as server:
                if SMTP_USER:
                    server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                server.ehlo()
                try:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                except smtplib.SMTPException:
                    pass
                if SMTP_USER:
                    server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        print("[NOTIFY] Email enviado ✅")
    except Exception as e:
        # Logueamos el error, pero no afectamos la respuesta del endpoint
        print(f"[NOTIFY] SMTP error: {e}")

def _send_email_async(msg: EmailMessage):
    t = Thread(target=_send_email, args=(msg,), daemon=True)
    t.start()

@app.post("/notify")
def notify(payload: NotifyPayload):
    # Normalizar email
    correo = payload.mail or payload.email
    if not correo:
        raise HTTPException(status_code=422, detail="email/mail requerido")

    print("[NOTIFY] Payload normalizado:", {
        "nombre": payload.nombre, "mail": str(correo), "telefono": payload.telefono
    })

    # Construir mensaje y enviarlo en background
    msg = _build_message(payload.nombre, str(correo), payload.telefono)
    _send_email_async(msg)

    # Respondemos rápido para no hacer timeout en el caller
    return {"status": "queued"}
