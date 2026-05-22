#!/bin/bash
# Script de tráfico sintético usando curl.
# Alternativa al script Python si no se tiene Python instalado.
#
# Uso:
#   chmod +x generate-traffic.sh
#   ./generate-traffic.sh

BASE_URL="http://localhost:3000"
ENDPOINTS=("/" "/api/datos" "/api/datos" "/api/lento" "/api/error" "/api/error")

echo "Generando tráfico hacia $BASE_URL"
echo "Presiona Ctrl+C para detener"
echo

CONTADOR=0
while true; do
    INDEX=$((RANDOM % ${#ENDPOINTS[@]}))
    ENDPOINT="${ENDPOINTS[$INDEX]}"
    CONTADOR=$((CONTADOR + 1))

    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}${ENDPOINT}")
    printf "[%04d] %-15s -> %s\n" "$CONTADOR" "$ENDPOINT" "$STATUS"

    # Pausa entre 0.2 y 0.8 segundos
    sleep $(awk -v min=0.2 -v max=0.8 'BEGIN{srand(); print min+rand()*(max-min)}')
done
