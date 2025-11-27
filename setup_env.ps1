# Setup Environment - PowerShell Script
# Script para configurar o ambiente de desenvolvimento no Windows

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  TelecomTools API - Setup Ambiente" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se .env já existe
if (Test-Path ".env") {
    Write-Host "⚠️  Arquivo .env já existe!" -ForegroundColor Yellow
    $resposta = Read-Host "Deseja substituí-lo? (s/N)"
    if ($resposta -ne "s" -and $resposta -ne "S") {
        Write-Host "❌ Operação cancelada." -ForegroundColor Red
        exit 0
    }
}

# Copiar env.example para .env
Write-Host "📄 Copiando env.example para .env..." -ForegroundColor Green
Copy-Item -Path "env.example" -Destination ".env" -Force

# Gerar SECRET_KEY
Write-Host "🔐 Gerando SECRET_KEY..." -ForegroundColor Green
$secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"

if ($LASTEXITCODE -eq 0 -and $secretKey) {
    # Substituir SECRET_KEY no .env
    $conteudo = Get-Content ".env" -Raw
    $conteudo = $conteudo -replace 'SECRET_KEY=dev-key-change-in-production-use-secure-random-key', "SECRET_KEY=$secretKey"
    Set-Content ".env" -Value $conteudo -NoNewline
    Write-Host "✅ SECRET_KEY gerada e configurada!" -ForegroundColor Green
} else {
    Write-Host "⚠️  Não foi possível gerar SECRET_KEY automaticamente." -ForegroundColor Yellow
    Write-Host "   Execute manualmente: python -c `"import secrets; print(secrets.token_urlsafe(32))`"" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✅ Configuração concluída!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Próximos passos:" -ForegroundColor Cyan
Write-Host "   1. Edite .env se necessário (DATABASE_URL, OPENCELLID_API_KEY, etc.)"
Write-Host "   2. Instale as dependências: pip install -r requirements.txt"
Write-Host "   3. Inicie o servidor: python run.py ou uvicorn app.main:app --reload"
Write-Host ""
Write-Host "🧪 Para testar a conexão com o banco:" -ForegroundColor Cyan
Write-Host "   python scripts/test_db_connection.py"
Write-Host ""


