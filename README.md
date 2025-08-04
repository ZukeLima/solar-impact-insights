# 🌞 Sistema de Previsão Solar

Sistema completo para análise e previsão de eventos de partículas energéticas solares (SEP) usando Docker, PostgreSQL e FastAPI.

## 🚀 Funcionalidades

### 📊 **Múltiplos Dashboards**
- **Dashboard Web Principal**: Interface moderna com gráficos interativos
- **Streamlit Analytics**: Análises avançadas e exploração de dados
- **Grafana Monitoring**: Monitoramento em tempo real com alertas

### 🔬 **Análises Avançadas**
- **Coleta de Dados**: Integração com APIs de dados solares e atmosféricos
- **Análise de Correlações**: Análise estatística entre diferentes variáveis
- **Clustering**: Agrupamento de eventos similares com visualizações 3D
- **Detecção de Anomalias**: Identificação automática de eventos anômalos
- **Previsões**: Modelos de machine learning para previsão de eventos

### 🚨 **Sistema de Alertas**
- **Alertas em Tempo Real**: Notificações para eventos de alta intensidade
- **Classificação por Severidade**: High, Medium, Low
- **Dashboard de Alertas**: Interface dedicada para gerenciamento

### 🛠️ **Tecnologias de Interface**
- **API REST**: Interface completa para interação com o sistema
- **WebSockets**: Atualizações em tempo real (planned)
- **Banco de Dados**: Armazenamento persistente com PostgreSQL

## 🛠️ Tecnologias

- **Python 3.11**
- **FastAPI** - Framework web moderno
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Docker & Docker Compose** - Containerização
- **Pandas & NumPy** - Análise de dados
- **Scikit-learn** - Machine Learning
- **Matplotlib & Seaborn** - Visualização
- **PgAdmin** - Interface de administração do banco

## 📋 Pré-requisitos

- Docker Desktop
- Docker Compose
- PowerShell (Windows)

## 🏃‍♂️ Como Executar

### Opção 1: Script PowerShell (Recomendado)
```powershell
# Iniciar todos os serviços
.\scripts\start.ps1

# Parar todos os serviços
.\scripts\stop.ps1
```

### Opção 2: Docker Compose Manual
```bash
# Iniciar serviços
docker-compose up --build -d

# Parar serviços
docker-compose down

# Ver logs
docker-compose logs -f app
```

### Opção 3: Streamlit Local
```powershell
# Executar apenas o Streamlit localmente
.\scripts\run_streamlit.ps1
```

### Opção 4: Serviços Individuais
```bash
# Apenas banco de dados
docker-compose up -d db

# FastAPI + Banco
docker-compose up -d db app

# Todos exceto Grafana
docker-compose up -d db app streamlit pgadmin
```

## 🌐 Acessos

Após iniciar os serviços:

- **🎛️ Dashboard Principal**: http://localhost:8000/dashboard
- **📊 Streamlit Analytics**: http://localhost:8501
- **📈 Grafana Monitoring**: http://localhost:3000
  - Usuário: `admin`
  - Senha: `admin123`
- **📖 API Documentação**: http://localhost:8000/docs
- **📋 API Redoc**: http://localhost:8000/redoc
- **🗄️ PgAdmin**: http://localhost:5050
  - Email: `admin@previsao.com`
  - Senha: `admin123`

## 🗄️ Banco de Dados

### Conexão PostgreSQL
- **Host**: localhost
- **Porta**: 5432
- **Banco**: previsao_solar
- **Usuário**: postgres
- **Senha**: postgres123

### Tabelas Principais
- `sep_events` - Eventos de partículas energéticas solares
- `predictions` - Previsões geradas pelos modelos
- `alerts` - Alertas do sistema
- `model_metrics` - Métricas de performance dos modelos

## 📊 API Endpoints

### Coleta de Dados
- `POST /data/collect` - Coletar e armazenar dados
- `GET /data/events` - Listar eventos armazenados
- `GET /data/high-intensity` - Eventos de alta intensidade

### Análises
- `POST /analysis/correlations` - Análise de correlações
- `POST /analysis/clustering` - Clustering de eventos
- `POST /analysis/prediction` - Gerar previsões

### Monitoramento
- `GET /alerts` - Listar alertas ativos
- `GET /health` - Status da aplicação

## 🏗️ Estrutura do Projeto

```
previsao_solar/
├── app/                    # Aplicação principal
│   ├── main.py            # Ponto de entrada
│   └── api.py             # FastAPI routes
├── domain/                # Entidades de domínio
│   └── entities.py        # Classes de dados
├── use_cases/            # Casos de uso
│   ├── analysis.py       # Análises estatísticas
│   └── alerts.py         # Sistema de alertas
├── infrastructure/       # Infraestrutura
│   ├── data_collection.py # Coleta de dados
│   ├── visualization.py   # Visualizações
│   └── database/         # Configuração do banco
│       ├── models.py     # Modelos SQLAlchemy
│       └── repository.py # Repositórios
├── adapters/             # Adaptadores
│   └── data_adapter.py   # Integração de dados
├── sql/                  # Scripts SQL
│   └── init.sql          # Inicialização do banco
├── scripts/              # Scripts utilitários
│   ├── start.ps1         # Iniciar serviços
│   └── stop.ps1          # Parar serviços
├── docker-compose.yml    # Orquestração Docker
├── Dockerfile           # Imagem da aplicação
├── requirements.txt     # Dependências Python
└── .env                # Variáveis de ambiente
```

## 🔧 Desenvolvimento

### Ambiente Local
```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env

# Executar apenas o banco
docker-compose up -d db

# Executar aplicação local
python app/main.py
```

### Debugging
```bash
# Ver logs da aplicação
docker-compose logs -f app

# Ver logs do banco
docker-compose logs -f db

# Acessar container da aplicação
docker-compose exec app bash

# Acessar banco de dados
docker-compose exec db psql -U postgres -d previsao_solar
```

## 📈 Exemplo de Uso

1. **Iniciar os serviços**:
   ```powershell
   .\scripts\start.ps1
   ```

2. **Acessar o dashboard**: http://localhost:8000/dashboard

3. **Coletar dados**:
   - Clique em "Coletar Dados Mock"

4. **Executar análises**:
   - "Análise de Correlações"
   - "Clustering"
   - "Gerar Previsões"

5. **Monitorar**:
   - "Ver Alertas"
   - "Eventos de Alta Intensidade"

## 🚨 Alertas e Monitoramento

O sistema possui alertas automáticos para:
- Eventos de alta intensidade (SEP > 5.0)
- Anomalias detectadas nos dados
- Previsões de eventos críticos

## 📝 Logs

Logs são armazenados em:
- Container: `/app/logs/`
- Local: `./logs/`

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 🆘 Suporte

Para problemas ou dúvidas:
1. Verifique os logs: `docker-compose logs -f`
2. Reinicie os serviços: `.\scripts\stop.ps1` e `.\scripts\start.ps1`
3. Verifique se todas as portas estão disponíveis

## 🔄 Atualizações

Para atualizar o sistema:
```powershell
# Parar serviços
.\scripts\stop.ps1

# Rebuild
docker-compose build --no-cache

# Iniciar
.\scripts\start.ps1
```
