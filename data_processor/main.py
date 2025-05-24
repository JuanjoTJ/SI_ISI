from fastapi import FastAPI, HTTPException
from pydantic import ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from models.producto import Producto
from difflib import SequenceMatcher
import regex as re

# Instancia de FastAPI
app = FastAPI()

# Conexión a MongoDB
MONGO_URL = "mongodb://mongo_db:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["productos_db"]
coleccion = db["productos"]

# Umbral de similitud para considerar títulos como iguales
UMBRAL_SIMILITUD = 0.70

# Stopwords que se ignorarán al normalizar el título
STOPWORDS = {
    # Palabras genéricas y técnicas
    "smartphone", "smartphones", "phone", "phones", "movil", "móvil", "moviles", "móviles",
    "pantalla", "screen", "lcd", "hd", "uhd", "oled", "ips", "tft", "hz", "full", "plus",
    "dual", "triple", "quad", "camera", "cámara", "camaras", "cámaras", "megapixel", "mp",
    "con", "de", "y", "the", "with", "version", "versión", "es", "ultra", "nfc", "pro",
    "max", "mini", "lite", "edition", "edición", "nuevo", "nueva", "new", "kit", "negro",
    "black", "blanco", "white", "azul", "blue", "rojo", "red", "gris", "gray", "grey",
    "oro", "gold", "plata", "silver", "verde", "green", "amarillo", "yellow", "inch", "pulgadas",
    "procesador", "processor", "cpu", "ram", "gb", "tb", "mb", "storage", "almacenamiento",
    "bateria", "batería", "battery", "mah", "android", "ios", "windows", "wifi", "bluetooth",
    "sim", "nano", "micro", "sd", "slot", "expansion", "expansión", "sensor", "face", "id",
    "huella", "fingerprint", "lector", "reader", "usb", "type", "c", "lightning", "jack",
    "auriculares", "earphones", "headphones", "altavoz", "speaker", "altavoces", "speakers",
    "garantia", "garantía", "warranty", "incluido", "incluida", "incluidos", "incluidas",
    "accesorios", "accesorio", "accesories", "accessory", "accessories", "cargador", "charger",
    "cable", "manual", "usuario", "user", "manual", "español", "spanish", "english", "inglés",
    "china", "chino", "global", "internacional", "international", "original", "oficial", "nuevo",
    "nueva", "nuevo", "nuevos", "nuevas", "originales", "oficiales", "para", "por", "a", "en",
    "un", "una", "unos", "unas", "el", "la", "los", "las", "del", "al", "por", "sobre", "desde",
    "hasta", "compatible", "compatibles", "modelo", "model", "serie", "series",

    # Palabras frecuentes en títulos de Xiaomi y ASUS (según los JSON)
    "mi", "series", "oled", "intel", "amd", "ryzen", "core", "i3", "i5", "i7", "i9", "gen", "windows", "home", "pro",
    "geforce", "mx", "ssd", "hdd", "pcie", "nvme", "ips", "fhd", "uhd", "wqxga", "wuxga", "wqhd", "touch", "led",
    "backlit", "fingerprint", "sensor", "webcam", "hdmi", "usb", "wifi", "bluetooth", "ethernet", "battery", "mah",
    "w", "kg", "mm", "cm", "inch", "pulgadas", "pantalla", "teclado", "keyboard", "numeric", "pad", "backlight", "cam",
    "audio", "jack", "mic", "microphone", "speaker", "altavoz", "color", "gris", "plata", "negro", "azul", "blanco", "rojo",
    "green", "silver", "gray", "grey", "black", "white", "blue", "red", "gold", "pink", "purple", "orange", "yellow",

    # Palabras de marketing y variantes
    "nuevo", "nueva", "original", "oficial", "edición", "edition", "2023", "2024", "2022", "2021", "2020", "plus",
    "lite", "max", "pro", "ultra", "prime", "smart", "premium", "basic", "essential", "business", "gaming", "creator",
    "student", "office", "home", "professional", "touchscreen", "convertible", "flip", "duo", "go", "air", "book",

    # Palabras de conectividad y puertos
    "hdmi", "vga", "displayport", "thunderbolt", "usb", "typec", "typea", "microhdmi", "minihdmi", "minidisplayport",
    "sd", "microsd", "card", "reader", "slot", "port", "ports", "jack", "audio", "mic", "microphone", "webcam",

    # Palabras de almacenamiento y memoria
    "ram", "rom", "ssd", "hdd", "pcie", "nvme", "ddr4", "ddr5", "lpddr4", "lpddr5", "emmc", "storage", "memory",

    # Palabras de batería y energía
    "bateria", "batería", "battery", "mah", "watt", "w", "adapter", "charger", "cargador", "power", "supply",

    # Palabras de dimensiones y peso
    "mm", "cm", "kg", "g", "gram", "grams", "peso", "weight", "dimension", "dimensions", "size", "thickness", "width", "height", "depth",

    # Palabras de garantía y accesorios
    "garantia", "garantía", "warranty", "accesorio", "accesorios", "accessory", "accessories", "incluido", "incluida", "incluidos", "incluidas",

    # Palabras de sistema operativo y software
    "windows", "linux", "ubuntu", "dos", "freedos", "endless", "chrome", "chromebook", "android", "ios", "macos", "os", "sistema", "operativo",

    # Palabras de conectividad extra
    "bluetooth", "wifi", "ethernet", "lan", "wan", "wireless", "network", "4g", "5g", "lte", "sim", "nano", "micro", "dual", "triple", "quad",

    # Palabras de cámara y multimedia
    "camera", "cámara", "cam", "webcam", "megapixel", "mp", "video", "hd", "fullhd", "uhd", "4k", "8k", "hdr", "dolby", "audio", "altavoz", "speaker",

    # Palabras de teclado y ratón
    "teclado", "keyboard", "mouse", "trackpad", "touchpad", "numeric", "pad", "backlight", "backlit",

    # Palabras de marketing y otras variantes
    "nuevo", "nueva", "nuevos", "nuevas", "original", "oficial", "edición", "edition", "premium", "basic", "essential", "business", "gaming", "creator", "student", "office", "home", "professional", "touchscreen", "convertible", "flip", "duo", "go", "air", "book"
}


# Normaliza el título del producto
def normalizar_titulo(titulo):
    if not titulo:
        return ""
    titulo = titulo.lower()
    titulo = re.sub(r'[^a-z0-9 ]', '', titulo)
    titulo = re.sub(r'\s+', ' ', titulo).strip()
    return titulo


# Función para extraer palabras clave del título
def extraer_palabras_clave(titulo):
    titulo = normalizar_titulo(titulo)
    # Unifica variantes de números y unidades (ej: 6,88 -> 688, 8+256GB -> 8gb 256gb)
    titulo = re.sub(r'(\d+)[\s\+\-xX](\d+)(gb|tb|mb)?', r'\1gb \2gb', titulo)
    # Separa letras y números pegados (ej: g81ultra -> g81 ultra)
    titulo = re.sub(r'([a-z]+)(\d+)', r'\1 \2', titulo)
    titulo = re.sub(r'(\d+)([a-z]+)', r'\1 \2', titulo)
    # Elimina palabras sueltas de 1 o 2 caracteres (menos números)
    palabras = [w for w in titulo.split() if len(w) > 2 or w.isdigit()]
    # Elimina stopwords
    palabras_clave = set(palabras) - STOPWORDS
    return palabras_clave


# Función para comparar títulos
def calcular_ratio(titulo1, titulo2):
    # Extrae y ordena palabras clave de ambos títulos normalizados
    palabras1 = sorted(extraer_palabras_clave(titulo1))
    palabras2 = sorted(extraer_palabras_clave(titulo2))
    cadena1 = " ".join(palabras1)
    cadena2 = " ".join(palabras2)
    ratio = SequenceMatcher(None, cadena1, cadena2).ratio()
    return ratio


# Busca si el producto ya existe en la base de datos por product_id (puede ser lista o str)
async def buscar_producto_por_id(producto_dict):
    product_id_nuevo = producto_dict.get("product_id")
    if not product_id_nuevo:
        return None

    # Si es una lista, buscamos coincidencia con cualquier id de la lista
    if isinstance(product_id_nuevo, list):
        query = {"product_id": {"$in": product_id_nuevo}}
    else:
        query = {"product_id": product_id_nuevo}

    producto_existente = await coleccion.find_one(query)
    return producto_existente


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
            except Exception as e:
                print(f"Error al transformar producto: {producto_datos}, Error: {str(e)}")
                raise

            # Convierte el producto validado a un diccionario
            producto_dict = producto.dict()

            # Busca si el producto ya existe en la base de datos usando similitud
            producto_existente = await buscar_producto_por_id(producto_dict)

            if producto_existente:
                # Si existe, actualiza las listas de los campos relevante
                ids_existentes = producto_existente.get("product_id", [])
                if not isinstance(ids_existentes, list):
                    ids_existentes = [ids_existentes]
                precios_existentes = producto_existente.get("product_price", [])
                if not isinstance(precios_existentes, list):
                    precios_existentes = [precios_existentes]
                urls_existentes = producto_existente.get("product_url", [])
                if not isinstance(urls_existentes, list):
                    urls_existentes = [urls_existentes]
                proveedores_existentes = producto_existente.get("product_provider", [])
                if not isinstance(proveedores_existentes, list):
                    proveedores_existentes = [proveedores_existentes]


                # El nuevo id a actualizar
                id_nuevo = producto_dict.get("product_id")
                # Buscar el índice del id antiguo (si existe)
                idx = None
                if id_nuevo in ids_existentes:
                    idx = ids_existentes.index(id_nuevo)
                else:
                    # Si no está, no eliminamos nada
                    idx = None

                # Elimina el dato antiguo en la posición correspondiente de cada lista
                if idx is not None:
                    ids_existentes.pop(idx)
                    if idx < len(precios_existentes):
                        precios_existentes.pop(idx)
                    if idx < len(urls_existentes):
                        urls_existentes.pop(idx)
                    if idx < len(proveedores_existentes):
                        proveedores_existentes.pop(idx)


                # Añade el nuevo dato al final de cada lista
                ids_existentes.append(producto_dict.get("product_id"))
                precios_existentes.append(producto_dict.get("product_price"))
                urls_existentes.append(producto_dict.get("product_url"))
                proveedores_existentes.append(producto_dict.get("product_provider"))

                # Construye el producto actualizado respetando los demás campos
                producto_actualizado = producto_existente.copy()
                producto_actualizado["product_id"] = ids_existentes
                producto_actualizado["product_price"] = precios_existentes
                producto_actualizado["product_url"] = urls_existentes
                producto_actualizado["product_provider"] = proveedores_existentes
                producto_actualizado["timestamp"] = producto_dict.get("timestamp", None)

                # Actualiza el producto en la base de datos
                await coleccion.update_one(
                    {"_id": producto_existente["_id"]},
                    {"$set": producto_actualizado}
                )

                # Transforma el documento para que el campo "_id" sea serializable
                producto_serializable = transformar_id(producto_actualizado)

            else:
                # Si NO existe por product_id, busca integración por similitud de títul
                titulo_nuevo = producto_dict.get("product_title", "")
                producto_similar = None
                max_ratio = 0
                
                # Busca en la colección un producto con título suficientemente parecido
                async for prod in coleccion.find({}):
                    titulo_existente = prod.get("product_title", "")
                    ratio = calcular_ratio(titulo_nuevo, titulo_existente)
                    if ratio > max_ratio and ratio >= UMBRAL_SIMILITUD:
                        max_ratio = ratio
                        producto_similar = prod
                
                if producto_similar:
                    # Si encuentra un producto similar, integra los datos en sus listas
                    ids_existentes = producto_similar.get("product_id", [])
                    if not isinstance(ids_existentes, list):
                        ids_existentes = [ids_existentes]
                    precios_existentes = producto_similar.get("product_price", [])
                    if not isinstance(precios_existentes, list):
                        precios_existentes = [precios_existentes]
                    urls_existentes = producto_similar.get("product_url", [])
                    if not isinstance(urls_existentes, list):
                        urls_existentes = [urls_existentes]
                    proveedores_existentes = producto_similar.get("product_provider", [])
                    if not isinstance(proveedores_existentes, list):
                        proveedores_existentes = [proveedores_existentes]

                    ids_existentes.append(producto_dict.get("product_id"))
                    precios_existentes.append(producto_dict.get("product_price"))
                    urls_existentes.append(producto_dict.get("product_url"))
                    proveedores_existentes.append(producto_dict.get("product_provider"))

                    # Construye el producto integrado respetando los demás campos
                    producto_integrado = producto_similar.copy()
                    producto_integrado["product_id"] = ids_existentes
                    producto_integrado["product_price"] = precios_existentes
                    producto_integrado["product_url"] = urls_existentes
                    producto_integrado["product_provider"] = proveedores_existentes
                    producto_integrado["timestamp"] = producto_dict.get("timestamp", None)
                    
                    
                    # Actualiza el producto similar en la base de datos
                    await coleccion.update_one(
                        {"_id": producto_similar["_id"]},
                        {"$set": producto_integrado}
                    )
                    producto_serializable = transformar_id(producto_integrado)
                else:
                    # Si no hay producto similar, inserta el nuevo producto como documento independiente
                    producto_dict["product_id"] = [producto_dict["product_id"]]
                    producto_dict["product_price"] = [producto_dict["product_price"]]
                    producto_dict["product_url"] = [producto_dict["product_url"]]
                    producto_dict["product_provider"] = [producto_dict["product_provider"]]

                    insert_result = await coleccion.insert_one(producto_dict)
                    producto_dict["_id"] = insert_result.inserted_id
                    producto_serializable = transformar_id(producto_dict)
                

            # Agrega el producto procesado (actualizado o insertado) a la lista de resultados
            productos_insertados_o_actualizados.append(producto_serializable)

        # Elimina productos repetidos por _id antes de devolver el resultado
        productos_unicos = {}
        for prod in productos_insertados_o_actualizados:
            clave = prod.get("_id")
            productos_unicos[clave] = prod

        return list(productos_unicos.values())
    
    
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=f"Error de validación: {e}")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")  # Agrega un log para depuración
        raise HTTPException(status_code=500, detail=f"Error al procesar productos: {str(e)}")