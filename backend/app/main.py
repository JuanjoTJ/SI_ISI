# Importar FasAPI y Query para definir la API y manejar parámetros de consulta
from fastapi import FastAPI, Query

# Importar funciones de servicios relacionadas a productos
from app.services.productos import obtener_productos

# Crear una instancia de FastAPI
app = FastAPI()


# Define un endpoint GET en la ruta /productos
@app.get("/productos")
async def productos(search: str = Query(..., description="Buscar productos por nombre")):
    # Llama de forma asíncrona a la función obtener_productos con el parámetro de búsqueda 'search'
    return await obtener_productos(search)