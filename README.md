# Notification Service - Microservicio de Notificaciones

Microservicio independiente de notificaciones por correo electrónico. Desarrollado con FastAPI, forma parte de la arquitectura de microservicios desplegada en AWS EKS.

## 📋 Descripción del Proyecto

Este servicio implementa el **microservicio de notificaciones** como parte del **Ejercicio 2 y 3** del trabajo práctico de Administración de Infraestructuras, demostrando el desacoplamiento y comunicación interna entre microservicios.

### Funcionalidades Principales

- ✅ **API REST interna**: Endpoint `/notify` para recibir eventos de otros servicios
- ✅ **Envío de emails**: Notificación por SMTP cuando se crea un usuario
- ✅ **Comunicación asíncrona**: Procesamiento no bloqueante de notificaciones
- ✅ **Health Check**: Endpoint `/health` para monitoreo de Kubernetes
- ✅ **Logs detallados**: Trazabilidad completa del proceso de envío
- ✅ **Configuración externa**: Credenciales SMTP en Kubernetes Secrets

## 🏗️ Arquitectura de Microservicios

```
users-api (ClusterIP) → notification-service (ClusterIP) → Gmail SMTP
                                    ↓
                            Email al Administrador
```

### Rol en la Arquitectura

| Aspecto                  | Descripción                                                 |
| ------------------------ | ----------------------------------------------------------- |
| **Tipo de servicio**     | Microservicio interno (ClusterIP)                          |
| **Comunicación**         | Solo accesible desde dentro del cluster Kubernetes        |
| **Protocolo**            | HTTP REST (puerto 9000)                                     |
| **Consumidores**         | users-api-service                                           |
| **Servicios externos**   | Gmail SMTP (smtp.gmail.com:587)                             |

### Ventajas del Desacoplamiento

1. **Independencia**: El servicio de notificaciones puede actualizarse sin afectar users-api
2. **Escalabilidad**: Puede escalar independientemente según la carga de notificaciones
3. **Resiliencia**: Si falla el envío de email, no afecta el registro del usuario
4. **Reutilización**: Otros servicios pueden consumir este microservicio
5. **Mantenibilidad**: Código más limpio y fácil de mantener

## 🔧 Tecnologías y Dependencias

### Stack Tecnológico

| Tecnología       | Versión   | Descripción                                           |
| ---------------- | --------- | ----------------------------------------------------- |
| **Python**       | 3.11      | Lenguaje base                                         |
| **FastAPI**      | 0.104.1   | Framework web asíncrono y rápido                     |
| **Uvicorn**      | 0.24.0    | Servidor ASGI para FastAPI                           |
| **smtplib**      | stdlib    | Librería estándar para envío de emails              |
| **email**        | stdlib    | Manejo de mensajes de email                          |

### Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Contenido de `requirements.txt`:**
```
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
```

## 🌐 API Endpoints

### 1. Enviar Notificación

**Endpoint:**
```http
POST /notify
Content-Type: application/json

{
  "event": "user_created",
  "user_name": "Juan Pérez",
  "user_email": "juan@example.com"
}
```

**Parámetros:**

| Campo        | Tipo   | Descripción                          | Requerido |
| ------------ | ------ | ------------------------------------ | --------- |
| event        | string | Tipo de evento (user_created)       | Sí        |
| user_name    | string | Nombre del usuario registrado        | Sí        |
| user_email   | string | Email del usuario registrado         | Sí        |

**Respuesta exitosa:**
```json
{
  "status": "success",
  "message": "Notificación enviada correctamente",
  "recipient": "admin@example.com"
}
```

**Respuesta con error:**
```json
{
  "status": "error",
  "message": "Error al enviar email: Connection refused"
}
```

### 2. Health Check

**Endpoint:**
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "service": "notification-service",
  "smtp_configured": true
}
```

## ⚙️ Configuración

### Variables de Entorno

#### Configuración SMTP (desde Kubernetes Secret)
```bash
SMTP_HOST=smtp.gmail.com           # Servidor SMTP
SMTP_PORT=587                      # Puerto TLS
SMTP_USER=notificaciones@gmail.com # Usuario Gmail
SMTP_PASS=<APP_PASSWORD>           # Contraseña de aplicación
```

#### Configuración de Notificaciones (desde ConfigMap)
```bash
FROM_EMAIL=notificaciones@gmail.com        # Email remitente
TO_ADMIN=admin@example.com                 # Email destinatario
SERVICE_NAME=Notification Service          # Nombre del servicio
LOG_LEVEL=INFO                             # Nivel de logs
```

### Archivos de Configuración Kubernetes

**`k8s/smtp-secret.yaml`** - Credenciales SMTP:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: smtp-secret
  namespace: app
type: Opaque
stringData:
  SMTP_HOST: smtp.gmail.com
  SMTP_PORT: "587"
  SMTP_USER: notificaciones@gmail.com
  SMTP_PASS: abcd efgh ijkl mnop  # App Password de Gmail
```

**⚠️ Importante**: Para Gmail, debes generar una "Contraseña de aplicación" en tu cuenta de Google:
1. Ir a https://myaccount.google.com/security
2. Habilitar verificación en 2 pasos
3. Ir a "Contraseñas de aplicaciones"
4. Generar nueva contraseña para "Correo"

**`k8s/notification-service-configmap.yaml`:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: notification-service-config
  namespace: app
data:
  FROM_EMAIL: "notificaciones@gmail.com"
  TO_ADMIN: "admin@example.com"
  SERVICE_NAME: "Notification Service"
  LOG_LEVEL: "INFO"
```

## 📧 Implementación del Envío de Email

**`app/main.py` - Lógica de envío:**
```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email_notification(user_name: str, user_email: str):
    """Envía email de notificación al administrador"""
    
    # Configuración SMTP desde variables de entorno
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    from_email = os.getenv('FROM_EMAIL')
    to_admin = os.getenv('TO_ADMIN')
    
    # Crear mensaje
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'Nuevo usuario registrado: {user_name}'
    msg['From'] = from_email
    msg['To'] = to_admin
    
    # Cuerpo del email
    html = f"""
    <html>
      <body>
        <h2>Nuevo Usuario Registrado</h2>
        <p><strong>Nombre:</strong> {user_name}</p>
        <p><strong>Email:</strong> {user_email}</p>
        <p>Este email fue generado automáticamente por el sistema.</p>
      </body>
    </html>
    """
    
    msg.attach(MIMEText(html, 'html'))
    
    # Enviar email
    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)
```

## 🐳 Containerización

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY app/ ./app/

# Exponer puerto
EXPOSE 8080

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Construcción y Push a ECR

```bash
# 1. Autenticarse en ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 757054385635.dkr.ecr.us-east-1.amazonaws.com

# 2. Construir imagen
docker build -t notification-service .

# 3. Etiquetar
docker tag notification-service:latest 757054385635.dkr.ecr.us-east-1.amazonaws.com/notification-service:latest

# 4. Subir a ECR
docker push 757054385635.dkr.ecr.us-east-1.amazonaws.com/notification-service:latest
```

## ☸️ Despliegue en AWS EKS

### Arquitectura de Despliegue

- **Cluster**: cluster-eks (AWS EKS)
- **Namespace**: app
- **Replicas**: 1 pod
- **Service Type**: ClusterIP (solo acceso interno)
- **Puerto interno**: 9000
- **Puerto del contenedor**: 8080
- **DNS interno**: `notification-service.app.svc.cluster.local:9000`

### Deployment y Service

**`k8s/notification-service-deployment.yaml`:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: notification-service-deployment
  namespace: app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: notification-service
  template:
    metadata:
      labels:
        app: notification-service
    spec:
      containers:
      - name: notification-service
        image: 757054385635.dkr.ecr.us-east-1.amazonaws.com/notification-service:latest
        ports:
        - containerPort: 8080
        env:
        - name: SMTP_HOST
          valueFrom:
            secretKeyRef:
              name: smtp-secret
              key: SMTP_HOST
        - name: SMTP_PORT
          valueFrom:
            secretKeyRef:
              name: smtp-secret
              key: SMTP_PORT
        - name: SMTP_USER
          valueFrom:
            secretKeyRef:
              name: smtp-secret
              key: SMTP_USER
        - name: SMTP_PASS
          valueFrom:
            secretKeyRef:
              name: smtp-secret
              key: SMTP_PASS
        - name: FROM_EMAIL
          valueFrom:
            configMapKeyRef:
              name: notification-service-config
              key: FROM_EMAIL
        - name: TO_ADMIN
          valueFrom:
            configMapKeyRef:
              name: notification-service-config
              key: TO_ADMIN
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "200m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: notification-service
  namespace: app
spec:
  type: ClusterIP
  selector:
    app: notification-service
  ports:
  - port: 9000
    targetPort: 8080
    protocol: TCP
```

### Aplicar Manifiestos

```bash
# 1. Crear namespace
kubectl apply -f ../k8s/00-namespace.yaml

# 2. Aplicar secrets y configmaps
kubectl apply -f k8s/smtp-secret.yaml
kubectl apply -f k8s/notification-service-configmap.yaml

# 3. Desplegar aplicación
kubectl apply -f k8s/notification-service-deployment.yaml

# 4. Verificar estado
kubectl get pods -n app -l app=notification-service
kubectl get svc -n app notification-service
kubectl logs -n app -l app=notification-service
```

## 🔐 Seguridad

### Buenas Prácticas Implementadas

- ✅ **Credenciales en Secrets**: SMTP user/password nunca en código
- ✅ **Servicio interno**: ClusterIP, no expuesto a Internet
- ✅ **TLS para SMTP**: Conexión cifrada con Gmail (puerto 587)
- ✅ **Resource limits**: CPU y memoria limitados
- ✅ **Logs sin datos sensibles**: No se registran contraseñas
- ✅ **Validación de entrada**: Pydantic valida payloads

### Restricciones de Red

```yaml
# El servicio NO es accesible desde Internet
# Solo pods dentro del namespace 'app' pueden comunicarse
type: ClusterIP
```

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

```bash
# Logs del servicio
kubectl logs -n app -l app=notification-service -f

# Logs de un pod específico
kubectl logs -n app notification-service-deployment-<POD_ID>
```

### Probar desde otro Pod

```bash
# Conectarse a un pod de users-api
kubectl exec -it -n app deployment/users-api-deployment -- bash

# Probar endpoint de notificación
curl -X POST http://notification-service.app.svc.cluster.local:9000/notify \
  -H "Content-Type: application/json" \
  -d '{"event":"user_created","user_name":"Test","user_email":"test@example.com"}'
```

## 🧪 Desarrollo Local

### Requisitos Previos

- Python 3.11+
- Cuenta de Gmail con contraseña de aplicación

### Configuración Local

1. **Clonar repositorio**:
```bash
git clone https://github.com/felipemarra15/notification-service.git
cd notification-service
```

2. **Crear entorno virtual**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USER=tu-email@gmail.com
export SMTP_PASS=tu-app-password
export FROM_EMAIL=tu-email@gmail.com
export TO_ADMIN=admin@example.com
export LOG_LEVEL=DEBUG
```

5. **Ejecutar servidor**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
```

6. **Probar API**:
```bash
curl -X POST http://localhost:8080/notify \
  -H "Content-Type: application/json" \
  -d '{"event":"user_created","user_name":"Test User","user_email":"test@example.com"}'
```

## 📁 Estructura del Proyecto

```
notification-service/
├── app/
│   └── main.py            # Código principal de FastAPI
├── k8s/
│   ├── smtp-secret.yaml                    # Secret con credenciales SMTP
│   ├── notification-service-configmap.yaml # ConfigMap con configuración
│   └── notification-service-deployment.yaml # Deployment y Service
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🧩 Integración con users-api

### Flujo Completo de Notificación

1. **Usuario crea un nuevo registro** en el frontend
2. **Frontend envía POST** a users-api: `/api/usuarios/`
3. **users-api guarda** el usuario en AWS RDS PostgreSQL
4. **users-api invoca** notification-service:
   ```python
   import requests
   
   notify_url = "http://notification-service.app.svc.cluster.local:9000/notify"
   payload = {
       "event": "user_created",
       "user_name": nuevo_usuario.nombre,
       "user_email": nuevo_usuario.email
   }
   
   try:
       requests.post(notify_url, json=payload, timeout=5)
   except Exception as e:
       print(f"Error al notificar: {e}")
       # No falla el registro si falla la notificación
   ```
5. **notification-service envía email** al administrador
6. **Administrador recibe email** con los datos del nuevo usuario

### DNS Interno de Kubernetes

```
notification-service.app.svc.cluster.local:9000
                     ↓
  <service-name>.<namespace>.svc.cluster.local:<port>
```

## 🔗 URLs de Acceso

- **Interno (ClusterIP)**: `http://notification-service.app.svc.cluster.local:9000`
- **Repositorio Git**: https://github.com/felipemarra15/notification-service
- **Imagen ECR**: `757054385635.dkr.ecr.us-east-1.amazonaws.com/notification-service:latest`

## 📧 Ejemplo de Email Enviado

```
De: notificaciones@gmail.com
Para: admin@example.com
Asunto: Nuevo usuario registrado: Juan Pérez

Nuevo Usuario Registrado
Nombre: Juan Pérez
Email: juan@example.com

Este email fue generado automáticamente por el sistema.
```


