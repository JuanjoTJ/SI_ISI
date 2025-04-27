# Usar una imagen base de Python ligera
FROM python:3.11-slim

# Establecer el directorio de trabajo "app"
WORKDIR /app

# Copiar el archivo requirements.txt al contenedor
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de los archivos de la aplicación al contenedor
COPY . .

# Exponer el puerto 10000 para la aplicación FastAPI
EXPOSE 10000

# Comando para ejecutar la aplicación FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]