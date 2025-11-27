#!/bin/bash
set -e

# Railway injeta $PORT como variável de ambiente
# Este script garante que o uvicorn use a porta correta
PORT=${PORT:-8000}

echo "Starting Uvicorn on port $PORT..."

# exec substitui o processo shell pelo uvicorn (PID 1)
# Isso garante que sinais SIGTERM sejam recebidos corretamente
exec uvicorn app.main:app \
  --host 0.0.0.0 \
  --port $PORT \
  --log-level info
