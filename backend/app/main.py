# Importar FasAPI y Query para definir la API y manejar parámetros de consulta
from fastapi import FastAPI, Query

# Importar Optional para manejar tipos opcionales
from typing import Optional

# Importar funciones de servicios relacionadas a productos
from app.services.productos import obtener_productos


# Crear una instancia de FastAPI
app = FastAPI()

# Define un endpoint GET en la ruta /productos
@app.get("/productos")
async def productos(search: Optional[str] = Query(None)):
    if search:
        # Llama de forma asíncrona a la función obtener_productos con el parámetro de búsqueda 'search'
        return await obtener_productos(search)
    else:
        # Llama de forma asíncrona a la función obtener_productos para obtener todos los productos
        return await obtener_productos()