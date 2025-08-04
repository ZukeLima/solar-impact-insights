import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uvicorn
from app.api import app

if __name__ == "__main__":
    print("🌞 Iniciando API de Previsão Solar...")
    print("📊 Dashboard disponível em: http://localhost:8000/dashboard")
    print("📖 Documentação da API: http://localhost:8000/docs")
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)