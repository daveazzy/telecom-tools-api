#!/bin/bash
set -e

echo "[ENTRYPOINT] Starting TelecomTools API..."

# Railway injeta $PORT como variável de ambiente
# Este script garante que o uvicorn use a porta correta
PORT=${PORT:-8000}

# Detectar se estamos usando PostgreSQL
if [[ "$DATABASE_URL" == postgresql* ]] || [[ "$DATABASE_URL" == postgres* ]]; then
    echo "[ENTRYPOINT] PostgreSQL detected - waiting for database to be ready..."
    
    # Extrair host e porta da DATABASE_URL
    # Formato: postgresql://user:pass@host:port/dbname
    DB_HOST=$(echo $DATABASE_URL | sed -E 's/.*@([^:]+).*/\1/')
    DB_PORT=$(echo $DATABASE_URL | sed -E 's/.*:([0-9]+)\/.*/\1/')
    
    # Se não conseguiu extrair, usar valores padrão
    DB_HOST=${DB_HOST:-postgres}
    DB_PORT=${DB_PORT:-5432}
    
    echo "[ENTRYPOINT] Checking connection to $DB_HOST:$DB_PORT..."
    
    # Tentar conectar ao banco com timeout
    MAX_RETRIES=30
    RETRY_COUNT=0
    
    # Instalar netcat se não estiver disponível (para check de porta)
    if ! command -v nc &> /dev/null; then
        echo "[ENTRYPOINT] Installing netcat for connection check..."
        apt-get update -qq && apt-get install -y -qq netcat-openbsd > /dev/null 2>&1 || true
    fi
    
    while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
        if nc -z -w5 $DB_HOST $DB_PORT 2>/dev/null; then
            echo "[ENTRYPOINT] Database is ready!"
            break
        fi
        
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "[ENTRYPOINT] Waiting for database... (attempt $RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    done
    
    if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
        echo "[WARNING] Could not confirm database connection, but will try to start anyway..."
    fi
else
    echo "[ENTRYPOINT] Using SQLite database"
fi

echo "[ENTRYPOINT] Starting uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
