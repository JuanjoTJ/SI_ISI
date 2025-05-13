from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from rapidfuzz import fuzz
from models.producto import Producto

# Instancia de FastAPI
app = FastAPI()

# Conexión a MongoDB
MONGO_URL = "mongodb://mongo_db:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["productos_db"]
coleccion = db["productos"]

# Transforma el documento para que los campos "_id"
def transformar_id(documento: dict) -> dict:
    if "_id" in documento:
        documento["_id"] = str(documento["_id"])  # Convierte ObjectId a cadena
    return documento


# Función para transformar los datos al modelo Producto
def transformar_a_producto(datos: dict) -> Producto:
    try:
        # Normaliza los datos para que cumplan con el modelo Producto
        return Producto(
            product_id=datos.get("asin") or datos.get("itemId",""),
            product_title=datos.get("product_title") or datos.get("title", ""),
            product_price=datos.get("product_price") or datos.get("promotionPrice") or datos.get("price", 0.0),
            product_url=datos.get("product_url") or datos.get("itemUrl", ""),
            product_photo=datos.get("product_photo") or datos.get("image", ""),
            product_provider=datos.get("product_provider", ""),
            timestamp=datos.get("timestamp", None)
        )
    except Exception as e:
        print(f"Error al transformar los datos: {datos}, Error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Error al transformar los datos: {str(e)}")


# Busca si el producto ya existe en la base de datos
async def buscar_producto_existente(producto_dict):
    productos_en_db = coleccion.find({})  # Obtiene todos los productos de la base de datos
    async for producto in productos_en_db:
        # Calcula la similitud entre los títulos
        similitud = fuzz.ratio(producto_dict["product_title"], producto["product_title"])
        if similitud >= 90:  # Considera una coincidencia si la similitud es del 90% o más
            return producto
    return None

# Endpoint para serializar el "_id" un documento de productos
@app.post("/serializar_documento")
async def serializar_documento(documento: dict):
    try:
        # Aplica la función transformar_id al diccionario recibido
        documento_serializado = transformar_id(documento)
        return documento_serializado
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al serializar el documento: {str(e)}")


# Endpoint para insertar o actualizar uno o varios productos
@app.post("/insertar_o_actualizar_productos")
async def insertar_o_actualizar_productos(productos: list[dict]):
    try:
        productos_insertados_o_actualizados = []

        # Itera sobre cada producto en la lista
        for producto_datos in productos:
            # Transforma los datos genéricos al modelo Producto
            try:
                producto = transformar_a_producto(producto_datos)
                print(f"Producto transformado: {producto}")
            except Exception as e:
                print(f"Error al transformar producto: {producto_datos}, Error: {str(e)}")
                raise

            # Convierte el producto validado a un diccionario
            producto_dict = producto.dict()

            # Busca si el producto ya existe en la base de datos usando similitud
            producto_existente = await buscar_producto_existente(producto_dict)

            if producto_existente:
                # Integra los datos de las distintas fuentes
                producto_actualizado = {
                    "product_id": producto_existente["product_id"],
                    "product_title": producto_existente["product_title"],
                    "product_price": list(set(producto_existente.get("product_price", []) + [producto_dict["product_price"]])),
                    "product_url": list(set(producto_existente.get("product_url", []) + [producto_dict["product_url"]])),
                    "product_photo": producto_existente.get("product_photo") or producto_dict.get("product_photo"),
                    "product_provider": list(set(producto_existente.get("product_provider", []) + [producto_dict["product_provider"]])),
                    "timestamp": producto_dict.get("timestamp") or producto_existente.get("timestamp")
                }

                # Actualiza el producto existente en la base de datos
                await coleccion.update_one(
                    {"_id": producto_existente["_id"]},
                    {"$set": producto_actualizado}
                )

                # Recupera el producto actualizado desde la base de datos
                producto_actualizado = await coleccion.find_one({"_id": producto_existente["_id"]})
                # Transforma el documento para que el campo "_id" sea serializable
                producto_serializable = transformar_id(producto_actualizado)
            else:
                # Inserta el nuevo producto
                producto_dict["product_price"] = [producto_dict["product_price"]]
                producto_dict["product_url"] = [producto_dict["product_url"]]
                producto_dict["product_provider"] = [producto_dict["product_provider"]]

                insert_result = await coleccion.insert_one(producto_dict)
                # Añade el `_id` generado al producto
                producto_dict["_id"] = insert_result.inserted_id
                # Transforma el documento para que el campo "_id" sea serializable
                producto_serializable = transformar_id(producto_dict)

            # Agrega el producto procesado (actualizado o insertado) a la lista de resultados
            productos_insertados_o_actualizados.append(producto_serializable)

        return {"mensaje": "Productos insertados o actualizados", "productos": productos_insertados_o_actualizados}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Error de validación: {e}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")  # Agrega un log para depuración
        raise HTTPException(status_code=500, detail=f"Error al procesar productos: {str(e)}")