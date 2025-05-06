from apscheduler.schedulers.blocking import BlockingScheduler
import httpx
from datetime import datetime
import sys

# Deshabilitar el buffering de stdout
sys.stdout.reconfigure(line_buffering=True)

def actualizar_db():
    print(f"[{datetime.now()}] Ejecutando recolección periódica...")
    try:
        # Realiza una solicitud al endpoint /productos del backend
        response = httpx.get("http://backend:9000/productos")
        response.raise_for_status()  # Lanza una excepción si el código de estado no es 2xx

        # Mensaje de confirmación
        print(f"[{datetime.now()}] Actualización de la base de datos completada.")

    except httpx.HTTPStatusError as http_err:
        # Maneja errores HTTP
        print(f"[{datetime.now()}] Error HTTP al llamar al endpoint: {http_err}")
    except Exception as e:
        # Maneja cualquier otro error
        print(f"[{datetime.now()}] Ocurrió un error al actualizar la base de datos: {str(e)}")


# Programador
scheduler = BlockingScheduler()
scheduler.add_job(actualizar_db, 'interval', minutes=2)

print("Scheduler iniciado. Ejecutando cada 2 minutos...")
scheduler.start()
