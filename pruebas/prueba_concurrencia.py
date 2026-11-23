
from pathlib import Path
from urllib.request import urlopen
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import perf_counter
from statistics import mean
from math import ceil

# Configuración de la prueba
IP_SERVIDOR = "192.168.1.100"
PUERTO = 5500
TAMANO = 1_000_000

carpeta = Path(__file__).parent
archivo = carpeta / "recurso_1MB.bin"

# Crear archivo de prueba de 1 MB decimal
if not archivo.exists():
    archivo.write_bytes(b"A" * TAMANO)

URL = (
    f"http://{IP_SERVIDOR}:{PUERTO}"
    "/pruebas/recurso_1MB.bin"
)

def solicitar(barrera):
    barrera.wait()
    inicio = perf_counter()

    try:
        with urlopen(URL, timeout=20) as respuesta:
            datos = respuesta.read()
            estado = respuesta.status

        tiempo = (perf_counter() - inicio) * 1000
        correcto = estado == 200 and len(datos) == TAMANO

        return tiempo, correcto

    except Exception:
        tiempo = (perf_counter() - inicio) * 1000
        return tiempo, False

def ejecutar_prueba(clientes):
    resultados = []

    for repeticion in range(3):
        barrera = Barrier(clientes + 1)

        with ThreadPoolExecutor(
            max_workers=clientes
        ) as ejecutor:

            trabajos = [
                ejecutor.submit(solicitar, barrera)
                for _ in range(clientes)
            ]

            barrera.wait()

            for trabajo in trabajos:
                resultados.append(trabajo.result())

    exitos = sorted(
        tiempo for tiempo, ok in resultados if ok
    )

    errores = len(resultados) - len(exitos)

    print(f"\nCLIENTES SIMULTANEOS: {clientes}")
    print(f"Solicitudes: {len(resultados)}")
    print(f"Exitosas: {len(exitos)}")
    print(f"Errores: {errores}")

    if exitos:
        posicion = ceil(0.95 * len(exitos)) - 1

        print(f"Promedio: {mean(exitos):.2f} ms")
        print(f"Minimo: {min(exitos):.2f} ms")
        print(f"Maximo: {max(exitos):.2f} ms")
        print(f"P95: {exitos[posicion]:.2f} ms")

for cantidad in [5, 10, 21]:
    ejecutar_prueba(cantidad)

print("\nPrueba finalizada.")
