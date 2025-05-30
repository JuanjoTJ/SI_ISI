from apscheduler.schedulers.blocking import BlockingScheduler
import httpx
from datetime import datetime
import sys

# Deshabilitar el buffering de stdout
sys.stdout.reconfigure(line_buffering=True)

def actualizar_db():
    print(f"[{datetime.now()}] Ejecutando scrapeo periódico...")
    try:
        # Realiza una solicitud al endpoint /scrapear_y_actualizar del backend
        response = httpx.get("http://backend:9000/scrapear_y_actualizar")
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
# Actualiza la base de datos cada 24 horas, a la medianoche
scheduler.add_job(actualizar_db, 'cron', hour=0, minute=0)

print("Scheduler iniciado. Ejecutando cada 24 horas...")
scheduler.start()
