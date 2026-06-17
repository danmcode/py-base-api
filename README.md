# FastAPI Core Template

Plantilla base para proyectos FastAPI con PostgreSQL, SQLAlchemy, Alembic, Nginx y Docker.

## Stack

- **Python 3.11** + **FastAPI**
- **PostgreSQL 15** (psycopg2)
- **SQLAlchemy 2** (síncrono)
- **Alembic** — migraciones
- **Nginx** — reverse proxy con SSL
- **Docker** + **Docker Compose**

---

## Estructura del proyecto

```
base-project/
├── app/
│   ├── main.py               # Entry point de FastAPI
│   ├── alembic/              # Migraciones
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── dependencies.py   # Dependencias FastAPI (DB session)
│   │   ├── exceptions.py     # Manejadores de excepciones
│   │   ├── logger.py         # Configuración de logging
│   │   └── security.py       # Utilidades JWT / hashing
│   ├── db/
│   │   ├── base.py           # Base declarativa SQLAlchemy
│   │   └── session.py        # Engine y SessionLocal
│   └── modules/              # Módulos de dominio (futuro)
├── docker/
│   ├── Dockerfile.dev
│   ├── Dockerfile.prod
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       ├── templates/
│       │   └── default.conf.template   # Nginx (envsubst)
│       └── certs/                      # Certificados SSL (no subir al repo)
├── scripts/
│   └── generate_cert.sh      # Genera certificado autofirmado
├── .env.dev.example          # Plantilla de variables de entorno para dev
├── .env.prod.example         # Plantilla de variables de entorno para prod
└── requirements.txt
```

---

## Configuración inicial

### 1. Clonar variables de entorno

```bash
cp .env.dev.example .env.dev
```

Edita `.env.dev` y ajusta al menos:

| Variable | Descripción |
|---|---|
| `POSTGRES_PASSWORD` | Contraseña de la base de datos |
| `DATABASE_URL` | URL completa de conexión (debe coincidir con usuario/password/db) |
| `SECRET_KEY` | Clave secreta para JWT (cadena larga y aleatoria) |

Para producción:

```bash
cp .env.prod.example .env.prod
# Edita .env.prod con valores reales y seguros
```

### 2. Generar certificado SSL autofirmado (solo desarrollo)

```bash
./scripts/generate_cert.sh
# Cuando pregunte el dominio, ingresa: test.dev
```

Esto genera `docker/nginx/certs/cert.pem` y `docker/nginx/certs/key.pem`.

> **Para confiar en el certificado en Chrome/Firefox**, importa `docker/nginx/certs/cert.pem`
> en el almacén de certificados de tu sistema o navegador.

Para agregar el dominio al hosts local:

```bash
echo "127.0.0.1  test.dev" | sudo tee -a /etc/hosts
```

---

## Desarrollo

### Levantar los contenedores

Los comandos de Docker Compose se ejecutan **desde la carpeta `docker/`**:

```bash
cd docker
docker compose -f docker-compose.dev.yml up --build
```

O desde la raíz del proyecto:

```bash
docker compose -f docker/docker-compose.dev.yml up --build
```

### Verificar que funciona

```bash
# Health check (desde dentro de la red Docker o con el dominio configurado)
curl -k https://test.dev/health
```

Respuesta esperada:

```json
{
  "status": "ok",
  "database": "connected",
  "environment": "development"
}
```

La documentación interactiva (Swagger) está disponible en modo `DEBUG=true`:
- `https://test.dev/docs`

### Migraciones con Alembic

```bash
# Dentro del contenedor de la API
docker exec -it fastapi_dev bash

# Crear migración
alembic revision --autogenerate -m "descripcion_del_cambio"

# Aplicar migraciones
alembic upgrade head
```

---

## Producción

### 1. Preparar variables de entorno

```bash
cp .env.prod.example .env.prod
# Edita con valores seguros reales
```

### 2. Certificado SSL

Para producción coloca un certificado válido en `docker/nginx/certs/`:

```
docker/nginx/certs/cert.pem   # Certificado (o cadena de certificados)
docker/nginx/certs/key.pem    # Clave privada
```

Agrega el dominio al DNS de tu servidor para que apunte a tu IP.

### 3. Levantar

```bash
cd docker
docker compose -f docker-compose.prod.yml up -d
```

---

## Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `DATABASE_URL` | Sí | URL de conexión PostgreSQL |
| `POSTGRES_DB` | Sí | Nombre de la base de datos |
| `POSTGRES_USER` | Sí | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | Sí | Contraseña de PostgreSQL |
| `SECRET_KEY` | Sí | Clave secreta JWT |
| `ALGORITHM` | No | Algoritmo JWT (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Expiración de tokens (default: `30`) |
| `ENVIRONMENT` | No | `development` o `production` |
| `DEBUG` | No | Activa `/docs` y `/redoc` (default: `false`) |
| `CORS_ORIGINS` | No | Lista JSON de orígenes CORS permitidos |

---

## Seguridad

- Los archivos `.env.dev` y `.env.prod` están en `.gitignore` — **nunca los subas al repositorio**.
- Los certificados `.pem` también están en `.gitignore`.
- En producción, la base de datos solo es accesible dentro de la red Docker (no expone puertos al host).
- Nginx aplica cabeceras de seguridad: `HSTS`, `X-Frame-Options`, `X-Content-Type-Options`.
- El endpoint `/docs` y `/redoc` solo están disponibles con `DEBUG=true`.
