#!/bin/bash
# Aspetta Docker per massimo 60 secondi
TIMEOUT=60
ELAPSED=0
until docker info > /dev/null 2>&1; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "$(date): Docker non disponibile dopo ${TIMEOUT}s, uscita." >&2
        exit 1
    fi
done
docker run --rm \
  --env-file /Users/alfonsomarino/Desktop/news-digest/.env \
  -v /Users/alfonsomarino/Desktop/news-digest/outputs:/app/outputs \
  news-digest