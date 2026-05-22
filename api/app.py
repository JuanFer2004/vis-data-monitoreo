from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import random
import psutil

app = Flask(__name__)

# ---------- MÉTRICAS PROMETHEUS ----------
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requests HTTP recibidas',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'Latencia de los requests HTTP en segundos',
    ['endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Requests actualmente en proceso'
)

CPU_USAGE = Gauge('app_cpu_percent', 'Uso de CPU del proceso (%)')
MEM_USAGE = Gauge('app_memory_mb', 'Memoria usada por el proceso (MB)')


# ---------- MIDDLEWARE ----------
@app.before_request
def before_request():
    request.start_time = time.time()
    ACTIVE_REQUESTS.inc()


@app.after_request
def after_request(response):
    # Excluimos /metrics del cálculo para no contaminar
    if request.endpoint != 'metrics':
        latency = time.time() - request.start_time
        endpoint = request.endpoint or 'unknown'
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()
    ACTIVE_REQUESTS.dec()

    # Métricas del sistema
    try:
        CPU_USAGE.set(psutil.cpu_percent(interval=None))
        MEM_USAGE.set(psutil.Process().memory_info().rss / 1024 / 1024)
    except Exception:
        pass

    return response


# ---------- ENDPOINTS ----------
@app.route('/')
def home():
    return jsonify({
        "mensaje": "API de monitoreo - Juan Fernando Bueno Torres",
        "version": "1.0",
        "endpoints": ["/", "/api/datos", "/api/lento", "/api/error", "/metrics"]
    })


@app.route('/api/datos')
def datos():
    """Endpoint rápido que retorna datos aleatorios."""
    return jsonify({
        "datos": [random.randint(1, 100) for _ in range(5)],
        "timestamp": time.time()
    })


@app.route('/api/lento')
def lento():
    """Simula procesamiento lento (entre 2 y 3 segundos)."""
    delay = random.uniform(2, 3)
    time.sleep(delay)
    return jsonify({
        "mensaje": "procesado tras delay",
        "delay_segundos": round(delay, 2)
    })


@app.route('/api/error')
def error():
    """Genera errores 500 con una probabilidad del 50% (útil para tasa de errores)."""
    if random.random() < 0.5:
        return jsonify({"error": "fallo simulado en el servidor"}), 500
    return jsonify({"ok": True, "mensaje": "todo bien"})


@app.route('/metrics')
def metrics():
    """Endpoint expuesto para que Prometheus haga scraping."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
