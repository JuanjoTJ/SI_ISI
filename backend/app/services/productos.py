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


# Función auxiliar para recolectar datos y actualizar la base de datos a través de data_processor
async def recolectar_y_actualizar(search: str = None):
    try:
        # Llama al api_colector y al scraper
        if search:
            productos_proveedores = await recolectar_desde_proveedores(search)
            productos_scraping = await web_scraping(search)
        else:
            # Si no se proporciona un término de búsqueda, llama a las funciones sin parámetros
            productos_proveedores = await recolectar_desde_proveedores()
            productos_scraping = await web_scraping()

        # Combina los resultados de ambas funciones
        nuevos_productos = []
        if isinstance(productos_proveedores, list):
            nuevos_productos.extend(productos_proveedores)
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


# Define una función asíncrona para obtener productos filtrados por búsqueda de la base de datos + otras fuentes
async def obtener_productos(search: str = None):
    try:
        # Si no se proporciona un término de búsqueda, se recolectan nuevos datos
        if not search:
            nuevos_productos = await recolectar_y_actualizar()
            if nuevos_productos:
                return nuevos_productos
            raise HTTPException(status_code=404, detail="No se encontraron productos.")

        # Busca los productos en la base de datos
        productos_en_db = await coleccion.find({
            "nombre": {"$regex": search, "$options": "i"}
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
                            return nuevos_productos
                else:
                    # Si no hay timestamp, recolecta nuevos datos
                    nuevos_productos = await recolectar_y_actualizar(search)
                    if nuevos_productos:
                        return nuevos_productos

            # Serializamos el "_id"
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://data_processor:13000/serializar_documento",
                    json=productos_actualizados
                )
                response.raise_for_status()  # Lanza una excepción si la respuesta no es exitosa

                # Devuelve los productos procesados desde el data_processor
                return response.json()
            
        # Si no se encuentran productos en la base de datos, recolecta nuevos datos
        nuevos_productos = await recolectar_y_actualizar(search)
        if nuevos_productos:
            return nuevos_productos

        # Si no se encuentra información, devuelve un error
        raise HTTPException(status_code=404, detail="No se encontraron productos para la búsqueda proporcionada.")

    except Exception as e:
        # Maneja cualquier excepción y lanza un error HTTP
        raise HTTPException(status_code=500, detail=f"Error al obtener productos: {str(e)}")
    

# Define una función asíncrona para recolectar datos desde proveedores externos
async def recolectar_desde_proveedores(search: str = None):
    try:
        # Crea un cliente HTTP asíncrono
        async with httpx.AsyncClient() as client:
            # Hace una petición GET al servicio externo "api_collector"
            if search:
                response = await client.get("http://api_collector:10000/recolectar", params={"search": search})
            else:
                response = await client.get("http://api_collector:10000/recolectar")

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
        # Crea un cliente HTTP asíncrono
        async with httpx.AsyncClient() as client:
            # Hace una petición GET al servicio externo "scraper"
            if search:
                response = await client.get("http://scraper:11000/scrapear", params={"search": search})
            else:
                response = await client.get("http://scraper:11000/scrapear")

            # Lanza una excepción si la respuesta no es exitosa
            response.raise_for_status()

            # Devuelve los datos recolectados en formato JSON
            return response.json()
        
    except Exception as e:
        # Maneja cualquier excepción que ocurra durante el scraping
        return {"error": f"Fallo al scrapear datos: {str(e)}"}