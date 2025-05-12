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
    image: Optional[str] = None
    source: Optional[str] = None
    timestamp: datetime

# Lista de URLs de proveedores
PROVEEDORES = [
    "https://fakestoreapi.com/products",
    "https://api.freeapi.app/api/v1/public/randomproducts"
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

                # Manejo de diferentes estructuras de datos
                if isinstance(data, list):
                    # Caso 1: Los datos son una lista directamente
                    productos.extend(
                        [
                            Producto(
                                **{
                                    **item,
                                    "image": item.get("image") if isinstance(item.get("image"), str) else None
                                },
                                source=url,
                                timestamp=datetime.utcnow()
                            )
                            for item in data
                            if not search or search.lower() in item.get("title", "").lower()
                        ]
                    )
                elif isinstance(data, dict) and "data" in data:
                    # Caso 2: Los productos están dentro de un campo "data"
                    nested_data = data["data"]
                    if isinstance(nested_data, dict) and "data" in nested_data:
                        # Caso 2.1: Los productos están dentro de un segundo nivel de "data"
                        nested_data = nested_data["data"]

                    if isinstance(nested_data, list):
                        productos.extend(
                            [
                                Producto(
                                    **{
                                        **item,
                                        # Obtiene la primera imagen de "images" si es una lista, o usa None
                                        "image": item.get("images")[0] if isinstance(item.get("images"), list) else None
                                    },
                                    source=url,
                                    timestamp=datetime.utcnow()
                                )
                                for item in nested_data
                                if not search or search.lower() in item.get("title", "").lower()
                            ]
                        )
                    else:
                        print(f"Estructura de datos inesperada en {url}: {nested_data}")
                else:
                    print(f"Estructura de datos inesperada en {url}: {data}")

            except httpx.HTTPStatusError as http_err:
                print(f"Error HTTP con {url}: {http_err}")

            except Exception as e:
                print(f"Error con {url}: {e}")
                
    return productos