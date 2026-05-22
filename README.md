# Monitoreo y Observabilidad — API con Prometheus y Grafana

**Estudiante:** Juan Fernando Bueno Torres
**Código:** 202225714601
**Asignatura:** Herramientas y visualización de datos
**Actividad:** Monitoreo y observabilidad

---

##  Descripción

Sistema completo de monitoreo y observabilidad para una API REST desarrollada en
**Python (Flask)**, instrumentada con métricas en formato **Prometheus** y
visualizada en **Grafana**. Todo el stack se ejecuta con **Docker Compose** y
viene con un dashboard preconfigurado más un script para generar tráfico
sintético.

##  Arquitectura

```
┌──────────────┐    scrape    ┌──────────────┐    query    ┌──────────────┐
│  API Flask   │ ◄──────────  │  Prometheus  │ ◄────────── │   Grafana    │
│   :3000      │   /metrics   │    :9090     │  PromQL     │    :3001     │
└──────────────┘              └──────────────┘             └──────────────┘
       ▲
       │ tráfico sintético
       │
┌──────────────┐
│ generate-    │
│ traffic.py   │
└──────────────┘
```

##  Estructura del proyecto

```
monitoreo-api/
├── docker-compose.yml
├── README.md
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── prometheus/
│   └── prometheus.yml
├── grafana/
│   └── provisioning/
│       ├── datasources/
│       │   └── datasource.yml
│       └── dashboards/
│           ├── dashboard.yml
│           └── api-dashboard.json
└── scripts/
    ├── generate-traffic.py
    └── generate-traffic.sh
```

##  Cómo ejecutar

### Requisitos previos
- Docker
- Docker Compose
- Python 3 (solo si se quiere usar el script de tráfico en Python)

### Levantar todo el stack

```bash
docker-compose up -d --build
```

Verificar que los 3 servicios estén corriendo:

```bash
docker-compose ps
```

### Detener y limpiar

```bash
docker-compose down -v
```

##  Acceso a los servicios

| Servicio   | URL                          | Credenciales    |
|------------|------------------------------|-----------------|
| API        | http://localhost:3000        | -               |
| Métricas   | http://localhost:3000/metrics| -               |
| Prometheus | http://localhost:9090        | -               |
| Grafana    | http://localhost:3001        | admin / admin   |

> El dashboard **"API Monitoreo - Juan Fernando Bueno"** se carga
> automáticamente en Grafana gracias al provisioning.

##  Endpoints de la API

| Método | Endpoint       | Descripción                                       |
|--------|----------------|---------------------------------------------------|
| GET    | `/`            | Endpoint principal con información de la API      |
| GET    | `/api/datos`   | Retorna datos aleatorios (respuesta rápida)       |
| GET    | `/api/lento`   | Simula procesamiento lento (2 a 3 segundos)       |
| GET    | `/api/error`   | Falla con 500 el 50% de las veces (para errores)  |
| GET    | `/metrics`     | Métricas en formato Prometheus                    |

##  Métricas expuestas

| Métrica                          | Tipo      | Descripción                              |
|----------------------------------|-----------|------------------------------------------|
| `http_requests_total`            | Counter   | Requests por método, endpoint y status   |
| `http_request_duration_seconds`  | Histogram | Latencia de respuesta por endpoint       |
| `http_requests_active`           | Gauge     | Requests procesándose en este momento    |
| `app_cpu_percent`                | Gauge     | Uso de CPU del proceso (%)               |
| `app_memory_mb`                  | Gauge     | Memoria del proceso en MB                |

##  Generar tráfico sintético

### Opción 1: Python (recomendada)

```bash
pip install requests
python scripts/generate-traffic.py
```

### Opción 2: Bash con curl

```bash
chmod +x scripts/generate-traffic.sh
./scripts/generate-traffic.sh
```

Ambos scripts envían requests aleatorios a los 4 endpoints con distribución
ponderada y pausas variables para simular tráfico real.

##  Queries PromQL útiles

```promql
# Requests por segundo, agrupado por endpoint
sum by (endpoint) (rate(http_requests_total[1m]))

# Latencia promedio por endpoint
rate(http_request_duration_seconds_sum[1m])
  / rate(http_request_duration_seconds_count[1m])

# Percentil 95 de latencia
histogram_quantile(0.95,
  sum by (le, endpoint) (rate(http_request_duration_seconds_bucket[5m])))

# Tasa de errores 5xx
sum(rate(http_requests_total{status=~"5.."}[1m]))

# Total de requests por endpoint
sum by (endpoint) (http_requests_total)
```

##  Paneles del dashboard

1. **Throughput** — requests por segundo por endpoint
2. **Latencia** — promedio y percentil 95 por endpoint
3. **Tasa de errores y requests activos** — 2xx, 5xx y conexiones activas
4. **Uso del sistema** — memoria y CPU del proceso

##  Stack tecnológico

- **Python 3.11** + **Flask 3.0**
- **prometheus-client** para instrumentación
- **psutil** para métricas del sistema
- **Prometheus** (última versión oficial)
- **Grafana** (última versión oficial)
- **Docker Compose 3.8**

##  Notas

- El dashboard usa `refresh: 5s`, así que los datos se actualizan en vivo
  mientras corre el script de tráfico.
- El endpoint `/api/error` produce intencionalmente errores 500 con
  probabilidad 50% para que el panel de tasa de errores muestre datos.
- El endpoint `/api/lento` introduce un delay aleatorio entre 2 y 3 segundos
  para que el percentil 95 de latencia sea claramente visible.

##  Autor

Juan Fernando Bueno Torres — Código 202225714601
