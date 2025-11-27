#!/bin/bash
set -e

# Railway injeta $PORT como variável de ambiente
# Este script garante que o uvicorn use a porta correta
PORT=${PORT:-8000}

exec uvicorn app.main:app --host 0.0.0.0 --port $PORT
