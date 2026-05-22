"""
Script de tráfico sintético para la API de monitoreo.
Genera requests aleatorias a los distintos endpoints para producir métricas.

Uso:
    pip install requests
    python generate-traffic.py
"""
import requests
import random
import time
import sys

BASE_URL = "http://localhost:3000"

# Distribución de tráfico: damos más peso a endpoints rápidos para simular tráfico real
ENDPOINTS = [
    ("/", 5),
    ("/api/datos", 5),
    ("/api/lento", 1),
    ("/api/error", 3),
]

# Construir lista ponderada
pool = []
for endpoint, weight in ENDPOINTS:
    pool.extend([endpoint] * weight)


def main():
    print(f"Generando tráfico hacia {BASE_URL}")
    print("Presiona Ctrl+C para detener\n")

    contador = 0
    try:
        while True:
            endpoint = random.choice(pool)
            try:
                r = requests.get(BASE_URL + endpoint, timeout=10)
                contador += 1
                estado = "OK" if r.status_code < 400 else "ERROR"
                print(f"[{contador:04d}] {endpoint:<15} -> {r.status_code} {estado}")
            except requests.exceptions.RequestException as e:
                print(f"[----] {endpoint:<15} -> EXC {e}")

            # Pausa variable entre requests
            time.sleep(random.uniform(0.1, 0.8))

    except KeyboardInterrupt:
        print(f"\n\nDetenido. Total de requests enviadas: {contador}")
        sys.exit(0)


if __name__ == "__main__":
    main()
