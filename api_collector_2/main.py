from fastapi import FastAPI, Query # Para crear la API
from pydantic import BaseModel # Para definir el modelo de datos
from typing import List # Para manejar listas
import httpx # Para hacer peticiones HTTP
from datetime import datetime # Para manejar fechas y horas

app = FastAPI() # Inicializa la aplicación FastAPI

# Modelo de datos para los productos
class Producto(BaseModel):
    itemId: str
    title: str
    promotionPrice: float
    itemUrl: str
    image: str
    product_provider: str = "Aliexpress"
    timestamp: datetime


# Headers para la API de RapidAPI
HEADERS = {
    'x-rapidapi-key': "a44c6ca7d3msh6c3ac3b23d77accp1792bejsn7075bca9bd48",
    'x-rapidapi-host': "aliexpress-datahub.p.rapidapi.com"
}

# Categorías de búsqueda
catIDs = [7, 509]

# Endpoint para recolectar productos de los proveedores
@app.get("/recolectar", response_model=List[Producto])
async def recolectar(search: str = Query(..., description="Buscar productos por nombre")):
    productos = []
    URL = "https://aliexpress-datahub.p.rapidapi.com/item_search_2"

    for catID in catIDs:
        # Se establecen parámetros de búsqueda
        PARAMS = {
            "q": search,
            "sort": "default",
            "catId": catID,
            "region": "ES",
            "currency": "EUR"
        }

        # Usamos httpx para hacer peticiones asíncronas
        async with httpx.AsyncClient() as client:
            try:
                # Hacemos una petición GET a la URL del proveedor
                response = await client.get(URL, headers=HEADERS, params=PARAMS)
                response.raise_for_status()
                data = response.json()

                # Accedemos al campo "resultList" dentro de "result"
                if isinstance(data, dict) and "result" in data and "resultList" in data["result"]:
                    nested_data = data["result"]["resultList"]
                    for item_wrapper in nested_data:
                        try:
                            # Accedemos al producto dentro de "item"
                            item = item_wrapper.get("item", {})
                            
                            # Limpieza y procesamiento del precio
                            promotion_price = item.get("sku", {}).get("def", {}).get("promotionPrice", 0.0)
                            if promotion_price is None:
                                promotion_price = 0.0

                            # Crear el objeto Producto
                            producto = Producto(
                                itemId=item.get("itemId", "N/A"),
                                title=item.get("title", "Título no disponible"),
                                promotionPrice=float(promotion_price),
                                itemUrl=f"https:{item.get('itemUrl', '')}",
                                image=f"https:{item.get('image', '')}",
                                timestamp=datetime.utcnow()
                            )
                            productos.append(producto)
                        except Exception as e:
                            print(f"Error procesando el producto: {item_wrapper}, Error: {e}")
                else:
                    print(f"Estructura de datos inesperada: {data}")

            except httpx.HTTPStatusError as http_err:
                print(f"Error HTTP con {URL}: {http_err}")

            except Exception as e:
                print(f"Error con {URL}: {e}")
    
    return productos