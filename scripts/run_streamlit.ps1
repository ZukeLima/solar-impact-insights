# PowerShell script to run Streamlit locally

Write-Host "🚀 Iniciando Streamlit Dashboard..." -ForegroundColor Green

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "📦 Ativando ambiente virtual..." -ForegroundColor Yellow
    .\venv\Scripts\Activate.ps1
} else {
    Write-Host "⚠️ Ambiente virtual não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    Write-Host "📦 Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Set environment variables
$env:DATABASE_URL = "postgresql://postgres:postgres123@localhost:5432/previsao_solar"
$env:PYTHONPATH = "."

Write-Host "🌞 Iniciando Streamlit na porta 8501..." -ForegroundColor Green
Write-Host "📊 Acesse: http://localhost:8501" -ForegroundColor Blue

streamlit run streamlit_app.py --server.address=localhost --server.port=8501
