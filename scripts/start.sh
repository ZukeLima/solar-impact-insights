#!/bin/bash

# Build and start all services
echo "🐳 Construindo e iniciando serviços Docker..."

# Stop any running containers
docker-compose down

# Build and start services
docker-compose up --build -d

# Wait for database to be ready
echo "⏳ Aguardando banco de dados..."
sleep 10

# Show status
docker-compose ps

echo "✅ Serviços iniciados!"
echo "📊 Dashboard: http://localhost:8000/dashboard"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🗄️ PgAdmin: http://localhost:5050 (admin@previsao.com / admin123)"
echo "🔧 Para logs: docker-compose logs -f"
