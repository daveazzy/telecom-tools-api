#!/bin/bash
# Setup Environment - Bash Script
# Script para configurar o ambiente de desenvolvimento no Linux/Mac

echo "=========================================="
echo "  TelecomTools API - Setup Ambiente"
echo "=========================================="
echo ""

# Verificar se .env já existe
if [ -f ".env" ]; then
    echo "⚠️  Arquivo .env já existe!"
    read -p "Deseja substituí-lo? (s/N): " resposta
    if [ "$resposta" != "s" ] && [ "$resposta" != "S" ]; then
        echo "❌ Operação cancelada."
        exit 0
    fi
fi

# Copiar env.example para .env
echo "📄 Copiando env.example para .env..."
cp env.example .env

# Gerar SECRET_KEY
echo "🔐 Gerando SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))" 2>/dev/null)

if [ $? -eq 0 ] && [ -n "$SECRET_KEY" ]; then
    # Substituir SECRET_KEY no .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=dev-key-change-in-production-use-secure-random-key/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=dev-key-change-in-production-use-secure-random-key/SECRET_KEY=$SECRET_KEY/" .env
    fi
    echo "✅ SECRET_KEY gerada e configurada!"
else
    echo "⚠️  Não foi possível gerar SECRET_KEY automaticamente."
    echo "   Execute manualmente: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
fi

echo ""
echo "=========================================="
echo "✅ Configuração concluída!"
echo "=========================================="
echo ""
echo "📝 Próximos passos:"
echo "   1. Edite .env se necessário (DATABASE_URL, OPENCELLID_API_KEY, etc.)"
echo "   2. Instale as dependências: pip install -r requirements.txt"
echo "   3. Inicie o servidor: python run.py ou uvicorn app.main:app --reload"
echo ""
echo "🧪 Para testar a conexão com o banco:"
echo "   python scripts/test_db_connection.py"
echo ""


