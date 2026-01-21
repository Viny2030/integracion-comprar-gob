FROM python:3.9-slim

WORKDIR /app

# Copiamos el archivo de requerimientos primero
COPY requirements.txt .

# Instalamos las librerías DENTRO de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]