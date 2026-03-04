# Usamos Python 3.14-slim para coincidir con tu entorno local
FROM python:3.14-slim

# Variables de entorno de Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurar directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema requeridas por algunos paquetes de Python
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el proyecto
COPY . /app/

# Recolectar archivos estáticos para producción
# Pasamos una DATABASE_URL "dummy" porque Railway no inyecta variables secretas en la fase de Build, 
# y Django necesita que la variable exista para arrancar y recolectar los estáticos.
RUN DATABASE_URL=postgresql://dummy:dummy@localhost/dummy python manage.py collectstatic --noinput

# Exponer el puerto que usará Gunicorn
EXPOSE 8000

# Script de entrada para correr migraciones e iniciar Gunicorn
CMD python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000
