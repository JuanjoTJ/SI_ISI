from fastapi import FastAPI, Query # Para crear la API
from pydantic import BaseModel # Para definir el modelo de datos
from typing import List # Para manejar listas
import httpx # Para hacer peticiones HTTP
from datetime import datetime # Para manejar fechas y horas

app = FastAPI() # Inicializa la aplicación FastAPI

# Modelo de datos para los productos
class Producto(BaseModel):
    asin: str
    product_title: str
    product_price: float
    product_url: str
    product_photo: str
    product_provider: str = "Amazon"
    timestamp: datetime


# Headers para la API de RapidAPI
HEADERS = {
    'x-rapidapi-key': "a44c6ca7d3msh6c3ac3b23d77accp1792bejsn7075bca9bd48",
    'x-rapidapi-host': "real-time-amazon-data.p.rapidapi.com"
}

# Endpoint para recolectar productos de los proveedores
@app.get("/recolectar", response_model=List[Producto])
async def recolectar(search: str = Query(..., description="Buscar productos por nombre")):
    productos = []

    # Se obtienen los productos de la API de RapidAPI
    URL = "https://real-time-amazon-data.p.rapidapi.com/search"

    PARAMS = {
        "query": search,
        "country": "ES",
        "sort_by": "RELEVANCE",
        "category_id": "667049031",
        "product_condition": "NEW",
        "is_prime": "false",
        "fields": "product_title, product_price, product_url, product_photo"
    }

    # Usamos httpx para hacer peticiones asíncronas
    async with httpx.AsyncClient() as client:
        try:
            # Hacemos una petición GET a la URL del proveedor
            response = await client.get(URL, headers=HEADERS, params=PARAMS)
            response.raise_for_status()
            data = response.json()

            # Accedemos al campo "products" dentro de "data"
            if isinstance(data, dict) and "data" in data and "products" in data["data"]:
                nested_data = data["data"]["products"]
                for item in nested_data:
                    try:
                        # Limpieza y procesamiento de los datos
                        product_price = item.get("product_price", "0")
                        if product_price:
                            product_price = float(
                                product_price
                                .replace("\xa0", "")  # Elimina espacios no separables
                                .replace("€", "")    # Elimina el símbolo de euro
                                .replace(",", ".")   # Cambia coma por punto para formato decimal
                            )
                        else:
                            product_price = 0.0

                        # Crear el objeto Producto
                        producto = Producto(
                            asin=item.get("asin", "N/A"),
                            product_title=item.get("product_title", "Título no disponible"),
                            product_price=product_price,
                            product_url=item.get("product_url", ""),
                            product_photo=item.get("product_photo", ""),
                            timestamp=datetime.utcnow()
                        )
                        productos.append(producto)
                    except Exception as e:
                        print(f"Error procesando el producto: {item}, Error: {e}")
            else:
                print(f"Estructura de datos inesperada: {data}")

        except httpx.HTTPStatusError as http_err:
            print(f"Error HTTP con {URL}: {http_err}")

        except Exception as e:
            print(f"Error con {URL}: {e}")
    
    return productos