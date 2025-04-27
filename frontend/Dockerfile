# Imagen base oficial de Node.js
FROM node:18

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia archivos de dependencias
COPY package*.json ./

# Instala las dependencias de la app
RUN npm install

# Copia el resto del código de la aplicación
COPY . .

# Construye la aplicación para producción
RUN npm run build

# Usa una imagen ligera para servir el frontend (Nginx)
FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html

# Expone el puerto 80
EXPOSE 80

# Comando para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]