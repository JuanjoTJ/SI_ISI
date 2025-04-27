const express = require('express'); // Framework para Node.js que facilita la creación de aplicaciones web/API
const morgan = require('morgan'); // Middleware para registrar solicitudes HTTP
const cors = require('cors'); // Middleware para habilitar CORS (Cross-Origin Resource Sharing)
const axios = require('axios'); // Cliente HTTP para hacer solicitudes a otros servicios

// Crear una instancia de Express
const app = express();

// Configuración del puerto
const PORT = 8000;

// Middleware
app.use(cors());
app.use(morgan('dev'));
app.use(express.json());

// Inicialización del servidor Express y apertura del puerto 8000
app.listen(PORT, () => {
  console.log(`API Gateway escuchando en puerto ${PORT}`);
});

// Ruta para manejar solicitudes GET a /productos
app.get('/productos', async (req, res) => {
  try {
    // Nombre del servicio backend Docker
    const backendUrl = 'http://backend:9000/productos';

    // Hacer una solicitud GET al servicio backend y pasar los parámetros de consulta (axios)
    const response = await axios.get(backendUrl, { params: req.query });

    // Enviar la respuesta del servicio backend al cliente
    res.json(response.data);

  } catch (error) {
    res.status(500).json({ error: 'Error en el API Gateway', details: error.message });
  }
});