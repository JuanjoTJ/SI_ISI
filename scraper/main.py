# Importar FastAPI para crear la API y manejar parámetros de consulta
from fastapi import FastAPI, Query

# Importar BeautifulSoup para parsear HTML (web scraping)
from bs4 import BeautifulSoup

# Importar requests para hacer peticiones HTTP a la página web
import requests

# Importar re para trabajar con expresiones regulares (limpiar textos)
import re

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

        # Extraemos la descripción del producto
        descripcion = item.select_one(".description").text

        try:
            # Convertimos el precio limpio a un número decimal (float)
            precio = float(precio_limpio)
        except ValueError:
            # Si no se puede convertir, asignamos 0.0 como precio por defecto
            precio = 0.0

        # Agregamos el producto extraido a la lista
        productos.append({
            "nombre": nombre,
            "precio": precio,
            "descripcion": descripcion,
            "categoria": "electronics",
            "fuente": url
        })

    # Si se proporciona un término de búsqueda, filtramos los productos
    if search:
        productos = [
            producto for producto in productos
            if search.lower() in producto["nombre"].lower()
        ]

    # Devuelve todos los productos extraídos en formato JSON
    return productos
