# FastAPI Core Template

Plantilla base para proyectos FastAPI con PostgreSQL, SQLAlchemy async, Alembic, Nginx y Docker.

## Stack

- **Python 3.11** + **FastAPI**
- **PostgreSQL 15** (asyncpg)
- **SQLAlchemy 2** (async) + **Alembic** — migraciones
- **uv** — gestión de dependencias y entornos virtuales
- **Nginx** — reverse proxy con SSL (TLS 1.2/1.3)
- **Docker** + **Docker Compose**

---

## Estructura del proyecto

```
base-project/
├── app/
│   ├── main.py               # Entry point de FastAPI
│   ├── alembic/              # Migraciones (async engine)
│   ├── core/
│   │   ├── config.py         # Settings (pydantic-settings, desde .env)
│   │   ├── dependencies.py   # Inyección de AsyncSession
│   │   ├── exceptions.py     # Manejadores de excepciones HTTP
│   │   ├── logger.py         # Configuración de logging
│   │   └── security.py       # Utilidades JWT / hashing
│   ├── db/
│   │   ├── base.py           # Base declarativa SQLAlchemy
│   │   └── session.py        # AsyncEngine y AsyncSessionLocal
│   └── modules/              # Módulos de dominio
├── docker/
│   ├── Dockerfile.dev        # uv sync --frozen
│   ├── Dockerfile.prod       # uv sync --frozen --no-dev
│   ├── docker-compose.dev.yml
│   ├── docker-compose.prod.yml
│   └── nginx/
│       ├── templates/
│       │   └── default.conf.template   # Nginx con envsubst (NGINX_DOMAIN)
│       └── certs/                      # Certificados SSL (no subir al repo)
├── scripts/
│   └── generate_cert.sh      # Genera certificado autofirmado (detecta WSL)
├── pyproject.toml            # Dependencias del proyecto (uv)
├── uv.lock                   # Lockfile reproducible
├── .env.dev.example
└── .env.prod.example
```

---

## Requisitos previos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose v2
- [uv](https://docs.astral.sh/uv/) (para desarrollo local fuera de Docker)
- `openssl` (para generar certificados)

Instalar uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Configuración inicial

### 1. Variables de entorno

```bash
cp .env.dev.example .env.dev
```

Edita `.env.dev` y ajusta al menos:

| Variable | Descripción |
|---|---|
| `POSTGRES_PASSWORD` | Contraseña de la base de datos |
| `DATABASE_URL` | Debe usar driver `postgresql+asyncpg://` |
| `SECRET_KEY` | Clave secreta JWT (cadena aleatoria larga) |

Para producción:

```bash
cp .env.prod.example .env.prod
```

### 2. Certificado SSL autofirmado (desarrollo)

```bash
./scripts/generate_cert.sh
# Ingresa el dominio: test.dev
```

Genera `docker/nginx/certs/cert.pem` y `docker/nginx/certs/key.pem`.

En **WSL**, el script detecta el entorno automáticamente, copia el certificado a `C:\Windows\Temp\` e intenta importarlo en el almacén de Windows abriendo una ventana UAC. Solo debes aceptarla.

Para agregar el dominio al hosts local:

```bash
# Linux / WSL
echo "127.0.0.1  test.dev" | sudo tee -a /etc/hosts

# Windows (PowerShell como Administrador)
Add-Content C:\Windows\System32\drivers\etc\hosts "127.0.0.1  test.dev"
```

> **Firefox** usa su propio almacén. Importa `cert.pem` en `about:preferences#privacy` → Ver certificados → Autoridades.

---

## Desarrollo

### Levantar los contenedores

```bash
cd docker
docker compose -f docker-compose.dev.yml up --build
```

O desde la raíz:

```bash
docker compose -f docker/docker-compose.dev.yml up --build
```

El contenedor de la API monta el código fuente con hot-reload (uvicorn `--reload`). El virtualenv instalado durante el build queda aislado en un volumen anónimo (`/app/.venv`) para que el mount no lo sobreescriba.

### Verificar que funciona

```bash
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

Documentación interactiva disponible con `DEBUG=true`:
- `https://test.dev/docs` (Swagger UI)
- `https://test.dev/redoc`

### Migraciones con Alembic

```bash
# Desde el contenedor de la API
docker exec -it fastapi_dev bash

alembic revision --autogenerate -m "descripcion_del_cambio"
alembic upgrade head
```

O con uv fuera del contenedor (requiere `.env` en la raíz o variable `DATABASE_URL` exportada):

```bash
uv run alembic upgrade head
```

---

## Gestión de dependencias (uv)

```bash
# Instalar dependencias localmente
uv sync

# Instalar solo producción (sin grupo dev)
uv sync --no-dev

# Agregar dependencia
uv add sqlalchemy

# Agregar dependencia de desarrollo
uv add --group dev ruff

# Actualizar todas las dependencias
uv lock --upgrade

# Ejecutar comandos en el venv
uv run pytest
uv run alembic upgrade head
```

Los Dockerfiles usan `uv sync --frozen` para instalar exactamente lo que está en `uv.lock`, garantizando builds reproducibles.

---

## Producción

### 1. Variables de entorno

```bash
cp .env.prod.example .env.prod
# Rellenar con credenciales reales y seguras
```

### 2. Certificado SSL

Coloca un certificado válido (ej. Let's Encrypt) en `docker/nginx/certs/`:

```
docker/nginx/certs/cert.pem   # Certificado (o cadena completa)
docker/nginx/certs/key.pem    # Clave privada
```

### 3. Levantar

```bash
cd docker
docker compose -f docker-compose.prod.yml up -d
```

---

## Variables de entorno

| Variable | Requerida | Descripción |
|---|---|---|
| `DATABASE_URL` | Sí | `postgresql+asyncpg://user:pass@host:5432/db` |
| `POSTGRES_DB` | Sí | Nombre de la base de datos |
| `POSTGRES_USER` | Sí | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | Sí | Contraseña de PostgreSQL |
| `SECRET_KEY` | Sí | Clave secreta JWT |
| `ALGORITHM` | No | Algoritmo JWT (default: `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Expiración de tokens (default: `30`) |
| `ENVIRONMENT` | No | `development` o `production` |
| `DEBUG` | No | Activa `/docs` y `/redoc` (default: `false`) |
| `CORS_ORIGINS` | No | Lista JSON de orígenes permitidos |

---

## Seguridad

- `.env.dev`, `.env.prod` y los archivos `.pem` están en `.gitignore` — **nunca los subas al repositorio**.
- En producción, la base de datos no expone puertos al host (solo red interna Docker).
- Nginx aplica cabeceras: `HSTS`, `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`.
- `/docs` y `/redoc` solo están disponibles con `DEBUG=true`.
- El driver asyncpg usa conexiones no bloqueantes; no hay `psycopg2` ni threads síncronos.

