# Notification Service

Microservicio de notificaciones por correo electrónico. Proporciona una API REST interna para envío de emails mediante SMTP.

## Descripción

Este servicio implementa un sistema de notificaciones por email desarrollado en Python con FastAPI. Es consumido internamente por `users-api` para enviar notificaciones cuando se registra un nuevo usuario.

## Características

- **API REST interna**: Endpoint `/notify` para envío de notificaciones
- **SMTP con Gmail**: Configurado con Gmail SMTP (smtp.gmail.com:587)
- **Health Check**: Endpoint `/health` para monitoreo
- **Logs detallados**: Seguimiento completo del proceso de envío

## Tecnologías

- **Python 3.11**: Lenguaje base
- **FastAPI**: Framework web asíncrono
- **smtplib**: Librería estándar para envío de emails
- **Uvicorn**: Servidor ASGI

## Configuración

El servicio utiliza las siguientes variables de entorno:

- `SMTP_HOST`: Servidor SMTP (smtp.gmail.com)
- `SMTP_PORT`: Puerto SMTP (587)
- `SMTP_USER`: Usuario de Gmail
- `SMTP_PASS`: Contraseña de aplicación de Gmail
- `FROM_EMAIL`: Email remitente
- `TO_ADMIN`: Email destinatario de notificaciones

Las credenciales SMTP se almacenan en un Secret de Kubernetes, mientras que otras configuraciones están en un ConfigMap.

## Despliegue

La aplicación se despliega en AWS EKS con:
- **Servicio**: ClusterIP (solo acceso interno)
- **Puerto**: 9000
- **Namespace**: app
- **Health Checks**: Deshabilitados para depuración
