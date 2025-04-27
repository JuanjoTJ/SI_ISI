from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException
import httpx

MONGO_URL = "mongodb://mongo_db:27017"

# Crea un cliente de MongoDB asíncrono
client = AsyncIOMotorClient(MONGO_URL)

# Conecta a la base de datos y colección
db = client["productos_db"]
coleccion = db["productos"]

# Transforma el documento para que el campo "_id" sea una cadena
def transformar_documento(documento):
    if "_id" in documento:
        documento["_id"] = str(documento["_id"])
    return documento

# Define una función asíncrona para obetener productos filtrados por búsqueda de la base de datos
async def obtener_productos(search: str = None):
    try:
        # Si no se proporciona un término de búsqueda, devuelve todos los productos de la base de datos
        if not search:
            productos = await coleccion.find().to_list(length=None)
            return [transformar_documento(producto) for producto in productos]
        
        # Busca el producto en la base de datos
        productos_en_db = await coleccion.find({
            "$or": [
                {"nombre": {"$regex": search, "$options": "i"}},
                {"title": {"$regex": search, "$options": "i"}}
            ]
        }).to_list(length=None)

        # Si se encuentran productos en la base de datos, se devuelven
        if productos_en_db:
            return [transformar_documento(producto) for producto in productos_en_db]
        
        # Si no se encuentran en la base de datos, llamamos a las funciones externas para recolectar datos
        productos_proveedores = await recolectar_desde_proveedores(search)
        productos_scraping = await web_scraping(search)

        # Combinamos los resultados de ambas funciones
        nuevos_productos = []
        if isinstance(productos_proveedores, list):
            nuevos_productos.extend(productos_proveedores)
        if isinstance(productos_scraping, list):
            nuevos_productos.extend(productos_scraping)
        
        # Si se encontraron nuevos productos, agrégalos o actualízalos en la base de datos
        for producto in nuevos_productos:
            # Busca si el producto ya existe en la base de datos
            producto_existente = await coleccion.find_one({
                "$or": [
                    {"nombre": producto["nombre"]},
                    {"title": producto.get("title", "")}
                ]
            })
            if producto_existente:
                # Actualiza el producto existente
                await coleccion.update_one(
                    {"_id": producto_existente["_id"]},
                    {"$set": producto}
                )
            else:
                # Inserta el nuevo producto
                await coleccion.insert_one(producto)

        # Devuelve los productos encontrados en las fuentes externas
        return [transformar_documento(producto) for producto in nuevos_productos]
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