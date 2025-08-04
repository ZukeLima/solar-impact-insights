# PowerShell script to stop Docker services

Write-Host "🛑 Parando serviços Docker..." -ForegroundColor Yellow

# Stop and remove containers
docker-compose down

# Show status
Write-Host "📊 Status dos serviços:" -ForegroundColor Cyan
docker-compose ps

Write-Host "✅ Serviços parados!" -ForegroundColor Green
