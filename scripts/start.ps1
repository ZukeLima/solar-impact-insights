# PowerShell script to start Docker services

Write-Host "🐳 Construindo e iniciando serviços Docker..." -ForegroundColor Green

# Stop any running containers
Write-Host "🛑 Parando containers existentes..." -ForegroundColor Yellow
docker-compose down

# Build and start services
Write-Host "🔨 Construindo e iniciando serviços..." -ForegroundColor Yellow
docker-compose up --build -d

# Wait for database to be ready
Write-Host "⏳ Aguardando banco de dados..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Show status
Write-Host "📊 Status dos serviços:" -ForegroundColor Cyan
docker-compose ps

Write-Host "✅ Serviços iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 DASHBOARDS DISPONÍVEIS:" -ForegroundColor Cyan
Write-Host "🎛️ Dashboard Principal: http://localhost:8000/dashboard" -ForegroundColor Blue
Write-Host "� Streamlit Analytics: http://localhost:8501" -ForegroundColor Blue
Write-Host "📈 Grafana Monitoring: http://localhost:3000 (admin/admin123)" -ForegroundColor Blue
Write-Host ""
Write-Host "🛠️ FERRAMENTAS:" -ForegroundColor Cyan
Write-Host "�📖 API Docs: http://localhost:8000/docs" -ForegroundColor Blue
Write-Host "🗄️ PgAdmin: http://localhost:5050 (admin@previsao.com/admin123)" -ForegroundColor Blue
Write-Host ""
Write-Host "🔧 COMANDOS ÚTEIS:" -ForegroundColor Magenta
Write-Host "   Logs da API: docker-compose logs -f app" -ForegroundColor Gray
Write-Host "   Logs Streamlit: docker-compose logs -f streamlit" -ForegroundColor Gray
Write-Host "   Parar tudo: .\scripts\stop.ps1" -ForegroundColor Gray
