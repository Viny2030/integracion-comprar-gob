FROM python:3.12-slim
WORKDIR /app

# Instalamos dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos requerimientos e instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código (incluyendo la carpeta data)
COPY . .

# Exponemos el puerto de Streamlit
EXPOSE 8501

# Comando corregido para que use tu dashboard.py
ENTRYPOINT ["python", "-m", "streamlit", "run", "dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]