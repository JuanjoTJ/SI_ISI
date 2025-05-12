# Importar FastAPI para crear la API y manejar parámetros de consulta
from fastapi import FastAPI, Query

# Importar BeautifulSoup para parsear HTML (web scraping)
from bs4 import BeautifulSoup

# Importar requests para hacer peticiones HTTP a la página web
import requests

# Importar re para trabajar con expresiones regulares (limpiar textos)
import re

# Importar datetime para manejar fechas y horas
from datetime import datetime

# Para definir el modelo de datos
from pydantic import BaseModel 

# Importar Optional para manejar tipos opcionales
from typing import Optional

# BaseModel de Pydantic para definir el modelo de datos
class Producto(BaseModel):
    title: str
    price: float
    product_url: str
    image: Optional[str] = None
    product_provider: Optional[str] = None
    timestamp: datetime

# Crear una instancia de FastAPI
app = FastAPI()

# Define un endpoint GET en la ruta /scrapear
@app.get("/scrapear")
def scrapear(search: str = Query(None)):
    # URL del sitio web de prueba que vamos a scrapear
    url = "https://webscraper.io/test-sites/e-commerce/allinone/computers/laptops"
    
    # Hace una petición HTTP para obtener el contenido de la página
    res = requests.get(url)

    # Usa BeautifulSoup para parsear el contenido HTML recibido
    soup = BeautifulSoup(res.text, "lxml")

    # Lista donde guardaremos los productos extraídos
    productos = []

    # Busca todos los elementos que tengan la clase 'thumbnail' (cada uno es un producto)
    for item in soup.select(".thumbnail"):
        # Extraemos el nombre del producto del (atributo 'title' del enlace)
        nombre = item.select_one(".title").get("title")

        # Extraemos el precio bruto como texto
        raw_precio = item.select_one(".price").text

        # Usamos una expresión regular para limpiar el precio, eliminando caracteres no numéricos
        precio_limpio = re.sub(r"[^\d.]", "", raw_precio)

        # Extraemos la URL del producto (atributo 'href' del enlace)
        # y la convertimos a una URL completa
        producto_tag = item.select_one(".title")
        if producto_tag:
            producto_url = producto_tag.get("href")
            producto_url = f"https://webscraper.io{producto_url}"
        else:
            producto_url = None

        # Extraemos la imagen del producto (atributo 'src' de la etiqueta img)
        # y la convertimos a una URL completa
        imagen_tag = item.select_one(".image img")
        if imagen_tag:
            imagen = imagen_tag.get("src")
            imagen = f"https://webscraper.io{imagen}"
        else:
            imagen = None  # Si no se encuentra la imagen, asignamos None

        try:
            # Convertimos el precio limpio a un número decimal (float)
            precio = float(precio_limpio)
        except ValueError:
            # Si no se puede convertir, asignamos 0.0 como precio por defecto
            precio = 0.0

       # Creamos una instancia del modelo Producto
        producto = Producto(
            title=nombre,
            price=precio,
            product_url=producto_url,
            image=imagen,
            product_provider=url,
            timestamp=datetime.utcnow()
        )

        # Agregamos el producto a la lista
        productos.append(producto)

    # Si se proporciona un término de búsqueda, filtramos los productos
    if search:
        productos = [
            producto for producto in productos
            if search.lower() in producto.title.lower()
        ]

    # Devuelve todos los productos extraídos en formato JSON
    return [producto.dict() for producto in productos]
