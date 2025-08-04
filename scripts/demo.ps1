# PowerShell script for quick demo

Write-Host "🌞 DEMONSTRAÇÃO RÁPIDA - Sistema de Previsão Solar" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Yellow

Write-Host ""
Write-Host "🚀 Iniciando demonstração..." -ForegroundColor Cyan

# Start only essential services for demo
Write-Host "📦 Iniciando serviços essenciais (DB + API + Streamlit)..." -ForegroundColor Yellow
docker-compose up -d db app streamlit

Write-Host "⏳ Aguardando serviços ficarem prontos..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "📊 Coletando dados de exemplo..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/data/collect" -Method POST -TimeoutSec 30
    Write-Host "✅ Dados coletados: $($response.data_points) eventos" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Erro ao coletar dados, mas serviços estão rodando" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 DEMO PRONTA! Acesse os dashboards:" -ForegroundColor Green
Write-Host ""
Write-Host "📊 STREAMLIT (Recomendado para demo):" -ForegroundColor Cyan
Write-Host "   → http://localhost:8501" -ForegroundColor Blue
Write-Host "   → Interface mais interativa e completa" -ForegroundColor Gray
Write-Host ""
Write-Host "🎛️ DASHBOARD WEB:" -ForegroundColor Cyan
Write-Host "   → http://localhost:8000/dashboard" -ForegroundColor Blue
Write-Host "   → Interface mais rápida e objetiva" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 API DOCS (para desenvolvedores):" -ForegroundColor Cyan
Write-Host "   → http://localhost:8000/docs" -ForegroundColor Blue

Write-Host ""
Write-Host "🎮 ROTEIRO DE DEMONSTRAÇÃO:" -ForegroundColor Yellow
Write-Host "1. Abra o Streamlit (http://localhost:8501)" -ForegroundColor White
Write-Host "2. Clique em 'Refresh Data' na sidebar" -ForegroundColor White
Write-Host "3. Explore as abas: Time Series → Analysis → Correlations → Predictions" -ForegroundColor White
Write-Host "4. Teste filtros de data e intensidade" -ForegroundColor White
Write-Host "5. Veja a detecção de anomalias" -ForegroundColor White
Write-Host "6. Explore o Data Explorer para exportar dados" -ForegroundColor White

Write-Host ""
Write-Host "🛑 Para parar a demo:" -ForegroundColor Red
Write-Host "   docker-compose down" -ForegroundColor Gray

Write-Host ""
Write-Host "✨ Demo iniciada com sucesso!" -ForegroundColor Green
