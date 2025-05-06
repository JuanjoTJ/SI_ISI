from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from models.producto import Producto

# Instancia de FastAPI
app = FastAPI()

# Conexión a MongoDB
MONGO_URL = "mongodb://mongo_db:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["productos_db"]
coleccion = db["productos"]

# Transforma el documento para que los campos "_id"
def transformar_documento(documento: dict) -> dict:
    if "_id" in documento:
        documento["_id"] = str(documento["_id"])  # Convierte ObjectId a cadena
    return documento


# Función para transformar los datos al modelo Producto
def transformar_a_producto(datos: dict) -> Producto:
    try:
        # Normaliza los datos para que cumplan con el modelo Producto
        return Producto(
            nombre=datos.get("nombre") or datos.get("title", ""),
            precio=datos.get("precio") or datos.get("price", 0.0),
            descripcion=datos.get("descripcion") or datos.get("description", ""),
            categoria=datos.get("categoria") or datos.get("category", ""),
            imagen=datos.get("imagen") or datos.get("image", ""),
            fuente=datos.get("fuente") or datos.get("source", ""),
            timestamp=datos.get("timestamp") or datos.get("timestamp", None)
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al transformar los datos: {str(e)}")


# Endpoint para serializar el "_id" un documento de productos
@app.post("/serializar_documento")
async def serializar_documento(documento: dict):
    try:
        # Aplica la función transformar_documento al diccionario recibido
        documento_serializado = transformar_documento(documento)
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
            producto = transformar_a_producto(producto_datos)

            # Convierte el producto validado a un diccionario
            producto_dict = producto.dict()

            # Busca si el producto ya existe en la base de datos (por ejemplo, por nombre)
            producto_existente = await coleccion.find_one({"nombre": producto_dict["nombre"]})

            if producto_existente:
                # Actualiza el producto existente
                await coleccion.update_one(
                    {"_id": producto_existente["_id"]},
                    {"$set": producto_dict}
                )
                # Recupera el producto actualizado desde la base de datos
                producto_actualizado = await coleccion.find_one({"_id": producto_existente["_id"]})
                # Transforma el documento para que el campo "_id" sea serializable
                producto_serializable = transformar_documento(producto_actualizado)
            else:
                # Inserta el nuevo producto
                insert_result = await coleccion.insert_one(producto_dict)
                # Añade el `_id` generado al producto
                producto_dict["_id"] = insert_result.inserted_id
                # Transforma el documento para que el campo "_id" sea serializable
                producto_serializable = transformar_documento(producto_dict)

            # Agrega el producto procesado (actualizado o insertado) a la lista de resultados
            productos_insertados_o_actualizados.append(producto_serializable)

        return {"mensaje": "Productos insertados o actualizados", "productos": productos_insertados_o_actualizados}

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Error de validación: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar productos: {str(e)}")