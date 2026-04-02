#!/bin/bash
# smart-run.sh
# Esegue il digest una volta al giorno — al login o alle 9, qualunque venga prima.

LAST_RUN_FILE="/Users/alfonsomarino/projects/news-digest/logs/last_run.txt"
TODAY=$(date +%Y-%m-%d)

# Controlla se è già stato eseguito oggi
if [ -f "$LAST_RUN_FILE" ] && [ "$(cat $LAST_RUN_FILE)" = "$TODAY" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') Digest già eseguito oggi, uscita." >> /Users/alfonsomarino/projects/news-digest/logs/digest.log
    exit 0
fi

# Aspetta che Docker sia pronto (max 60 secondi)
TIMEOUT=60
ELAPSED=0
until docker info > /dev/null 2>&1; do
    sleep 2
    ELAPSED=$((ELAPSED + 2))
    if [ $ELAPSED -ge $TIMEOUT ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') Docker non disponibile dopo ${TIMEOUT}s, uscita." >> /Users/alfonsomarino/projects/news-digest/logs/digest_error.log
        exit 1
    fi
done

# Esegui il container
docker run --rm \
  --env-file /Users/alfonsomarino/projects/news-digest/.env \
  -v /Users/alfonsomarino/projects/news-digest/outputs:/app/outputs \
  news-digest

# Segna come eseguito oggi
echo "$TODAY" > "$LAST_RUN_FILE"
echo "$(date '+%Y-%m-%d %H:%M:%S') Esecuzione completata." >> /Users/alfonsomarino/projects/news-digest/logs/digest.log
