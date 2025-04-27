# Imagen base de Node.js
FROM node:18

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de configuración y dependencias
COPY package*.json ./

# Instalar dependencias
RUN npm install

# Copiar el resto de la app
COPY . .

# Exponer el puerto del API Gateway
EXPOSE 8000

# Comando por defecto para iniciar el API Gateway al iniciar el contenedor
CMD ["node", "index.js"]