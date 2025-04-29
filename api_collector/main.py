from fastapi import FastAPI, Query # Para crear la API
from pydantic import BaseModel # Para definir el modelo de datos
from typing import List, Optional # Para manejar listas y tipos opcionales
import httpx # Para hacer peticiones HTTP
from datetime import datetime # Para manejar fechas y horas

app = FastAPI() # Inicializa la aplicación FastAPI

class Producto(BaseModel):
    title: str
    price: float
    description: str
    category: str
    image: str
    source: Optional[str] = None
    timestamp: datetime

# Lista de URLs de proveedores
PROVEEDORES = [
    "https://fakestoreapi.com/products", "https://apismaster.com/product"
]

# Endpoint para recolectar productos de los proveedores
@app.get("/recolectar", response_model=List[Producto])
async def recolectar(search: Optional[str] = Query(None)):
    productos = []

    # Usamos httpx para hacer peticiones asíncronas
    async with httpx.AsyncClient() as client:
        for url in PROVEEDORES:
            try:
                # Hacemos una petición GET a la URL del proveedor
                res = await client.get(url)

                # Transformamos la respuesta a formato JSON
                data = res.json()

                # Validamos que los datos sean una lista
                if isinstance(data, list):
                    if search:
                        # Filtramos los productos si se proporciona un término de búsqueda
                        productos.extend(
                            [
                                Producto(**item, source=url, timestamp=datetime.utcnow())
                                for item in data
                                if search.lower() in item.get("title", "").lower()
                            ]
                        )
                    else:
                        # Añadimos todos los productos si no hay término de búsqueda
                        productos.extend(
                            [Producto(**item, source=url, timestamp=datetime.utcnow()) for item in data]
                        )
                else:
                    print(f"Datos inesperados de {url}: {data}")

            except httpx.HTTPStatusError as http_err:
                print(f"Error HTTP con {url}: {http_err}")

            except Exception as e:
                print(f"Error con {url}: {e}")
                
    return productos