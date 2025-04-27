# Importar FasAPI y Query para definir la API y manejar parámetros de consulta
from fastapi import FastAPI, Query

# Importar Optional para manejar tipos opcionales
from typing import Optional

# Importar funciones de servicios relacionadas a productos
from app.services.productos import obtener_productos
from app.services.productos import recolectar_desde_proveedores
from app.services.productos import web_scraping

# Crear una instancia de FastAPI
app = FastAPI()

# Define un endpoint GET en la ruta /productos
@app.get("/productos")
async def productos(search: Optional[str] = Query(None)):
    # Llama de forma asíncrona a la función obtener_productos con el parámetro de búsqueda 'search'
    return await obtener_productos(search)

# Define un endpoint GET en la ruta /recolectar
@app.get("/recolectar")
async def recolectar(search: Optional[str] = Query(None)):
    if search:
        # Llama de forma asíncrona a la función con el parámetro de búsqueda 'search'
        return await recolectar_desde_proveedores(search)
    else:
        # Llama de forma asíncrona a la función para actualizar todos los datos de productos
        return await recolectar_desde_proveedores()

# Define un endpoint GET en la ruta /scrapear
@app.get("/scrapear")
async def scrapear(search: Optional[str] = Query(None)):
    if search:
        # Llama de forma asíncrona a la función scrapear con el parámetro de búsqueda 'search'
        return await web_scraping(search)
    else:
        # Llama de forma asíncrona a la función scrapear para actualizar los datos de productos
        return await web_scraping()