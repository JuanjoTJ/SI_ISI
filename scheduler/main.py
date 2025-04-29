from apscheduler.schedulers.blocking import BlockingScheduler
import httpx
from datetime import datetime

# Palabras clave de productos populares (pueden venir de DB o archivo en el futuro)
PALABRAS_CLAVE = ["laptop", "iphone", "monitor"]

# Endpoints de los recolectores
RECOLECTORES = [
    "http://api_collector:10000/recolectar",
    "http://scraper:11000/scrapear"
]

def recolectar_datos():
    print(f"[{datetime.now()}] Ejecutando recolección periódica...")

    for palabra in PALABRAS_CLAVE:
        for url in RECOLECTORES:
            try:
                with httpx.Client(timeout=10.0) as client:
                    if "recolectar" in url:
                        res = client.get(f"{url}?search={palabra}")
                    else:
                        res = client.get(url)  # El scraper no acepta parámetros

                    if res.status_code == 200:
                        print(f"✔ Recolección exitosa desde {url} con '{palabra}'")
                    else:
                        print(f"✘ Error {res.status_code} al consultar {url} con '{palabra}'")

            except Exception as e:
                print(f"✘ Excepción consultando {url}: {e}")

# Programador
scheduler = BlockingScheduler()
scheduler.add_job(recolectar_datos, 'interval', minutes=15)

print("⏳ Scheduler iniciado. Ejecutando cada 15 minutos...")
scheduler.start()
