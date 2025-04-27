# Usar una imagen ligera de Python para el contenedor
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias e instalarlas
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Exponer el puerto 9000
EXPOSE 9000

# Comando de arranque para ejecutar la aplicación FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000"]