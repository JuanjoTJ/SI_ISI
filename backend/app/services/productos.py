from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import httpx
from datetime import datetime, timedelta

MONGO_URL = "mongodb://mongo_db:27017"

# Crea un cliente de MongoDB asíncrono
client = AsyncIOMotorClient(MONGO_URL)

# Conecta a la base de datos y colección
db = client["productos_db"]
coleccion = db["productos"]

# Función auxiliar para serializar los IDs de los productos
def serializar_ids(productos):
    for producto in productos:
        if "_id" in producto:
            producto["_id"] = str(producto["_id"])
    return productos


# Función auxiliar para recolectar datos y actualizar la base de datos a través de data_processor
async def recolectar_y_actualizar(search: str):
    try:
        # Llama a los api_colectors y al scraper
        productos_api_1 = await recolectar_desde_amazon(search)
        productos_api_2 = await recolectar_desde_aliexpress(search)
        productos_scraping = await web_scraping(search)

        # Combina los resultados de ambas funciones
        nuevos_productos = []
        if isinstance(productos_api_1, list):
            nuevos_productos.extend(productos_api_1)
        if isinstance(productos_api_2, list):
            nuevos_productos.extend(productos_api_2)
        if isinstance(productos_scraping, list):
            nuevos_productos.extend(productos_scraping)

        # Si se encontraron nuevos productos, envíalos al data_processor
        if nuevos_productos:
            async with httpx.AsyncClient() as client:
                # Envía los productos al data_processor para insertar o actualizar
                response = await client.post(
                    "http://data_processor:13000/insertar_o_actualizar_productos",
                    json=nuevos_productos
                )
                response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa

                # Devuelve los productos procesados desde el data_processor
                return response.json()
        return None

    except Exception as e:
        # Maneja cualquier excepción durante la recolección o actualización
        raise HTTPException(status_code=500, detail=f"Error al recolectar o actualizar productos: {str(e)}")


async def scrapear_y_actualizar():
    try:
        # Llama al scraper
        nuevos_productos = await web_scraping()

        # Si se encontraron nuevos productos, envíalos al data_processor
        if nuevos_productos:
            async with httpx.AsyncClient() as client:
                # Envía los productos al data_processor para insertar o actualizar
                response = await client.post(
                    "http://data_processor:13000/insertar_o_actualizar_productos",
                    json=nuevos_productos
                )
                response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa

                # Devuelve los productos procesados desde el data_processor
                return response.json()
        return None

    except Exception as e:
        # Maneja cualquier excepción durante la recolección o actualización
        raise HTTPException(status_code=500, detail=f"Error al scrapear o actualizar productos: {str(e)}")
    

# Define una función asíncrona para obtener productos filtrados por búsqueda de la base de datos + otras fuentes
async def obtener_productos(search: str):
    try:
        # Busca los productos en la base de datos
        productos_en_db = await coleccion.find({
            "product_title": {"$regex": search, "$options": "i"}
        }).to_list(length=None)

        # Si se encuentran productos en la base de datos
        if productos_en_db:
            productos_actualizados = []
            for producto in productos_en_db:
                timestamp = producto.get("timestamp")

                if timestamp:
                    # Convierte el timestamp a un objeto datetime
                    timestamp = datetime.fromisoformat(timestamp) if isinstance(timestamp, str) else timestamp

                    # Comprueba si el timestamp es de hace más de 1 hora
                    if datetime.utcnow() - timestamp < timedelta(hours=1):
                        productos_actualizados.append(producto)
                    else:
                        # Si el timestamp es antiguo, recolecta nuevos datos
                        nuevos_productos = await recolectar_y_actualizar(search)
                        if nuevos_productos:
                            return serializar_ids(nuevos_productos)
                else:
                    # Si no hay timestamp, recolecta nuevos datos
                    nuevos_productos = await recolectar_y_actualizar(search)
                    if nuevos_productos:
                        return serializar_ids(nuevos_productos)

            # Serializamos el "_id"
            return serializar_ids(productos_actualizados)
            
        # Si no se encuentran productos en la base de datos, recolecta nuevos datos
        nuevos_productos = await recolectar_y_actualizar(search)
        if nuevos_productos:
            return serializar_ids(nuevos_productos)

        # Si no se encuentra información, devuelve un error
        raise HTTPException(status_code=404, detail="No se encontraron productos para la búsqueda proporcionada.")

    except Exception as e:
        # Maneja cualquier excepción y lanza un error HTTP
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")


# Define una función asíncrona para recolectar datos desde Amazon
async def recolectar_desde_amazon(search: str):
    try:
        # Crea un cliente HTTP asíncrono
        async with httpx.AsyncClient() as client:
            # Hace una petición GET al servicio externo "api_collector"
            response = await client.get("http://api_collector:10000/recolectar", params={"search": search})

            # Lanza una excepción si la respuesta no es exitosa
            response.raise_for_status()

            # Devuelve los datos recolectados en formato JSON
            return response.json()
        
    except Exception as e:
        # Maneja cualquier excepción que ocurra durante la recolección de datos
        return {"error": f"Fallo al recolectar datos: {str(e)}"}    
    

# Define una función asíncrona para recolectar datos desde Aliexpress
async def recolectar_desde_aliexpress(search: str):
    try:
        # Crea un cliente HTTP asíncrono
        async with httpx.AsyncClient() as client:
            # Hace una petición GET al servicio externo "api_collector_2"
            response = await client.get("http://api_collector_2:10001/recolectar", params={"search": search})

            # Lanza una excepción si la respuesta no es exitosa
            response.raise_for_status()

            # Devuelve los datos recolectados en formato JSON
            return response.json()
        
    except Exception as e:
        # Maneja cualquier excepción que ocurra durante la recolección de datos
        return {"error": f"Fallo al recolectar datos: {str(e)}"}    


# Define una función asíncrona para scrapear datos desde un sitio web de prueba
async def web_scraping(search: str = None):
    try:
        async with httpx.AsyncClient() as client:
            params = {"search": search} if search else {}
            response = await client.get("http://scraper:11000/scrapear", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        return {"error": f"Fallo al scrapear datos: {str(e)}"}