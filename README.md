# 🌞 Solar Impact Insights

Complete system for analysis and prediction of Solar Energetic Particle (SEP) events using Docker, PostgreSQL, and FastAPI.

## 🚀 Features

### 📊 **Multiple Dashboards**
- **Main Web Dashboard**: Modern interface with interactive charts
- **Streamlit Analytics**: Advanced analysis and data exploration
- **Grafana Monitoring**: Real-time monitoring with alerts

### 🔬 **Advanced Analytics**
- **Data Collection**: Integration with solar and atmospheric data APIs
- **Correlation Analysis**: Statistical analysis between different variables
- **Clustering**: Grouping of similar events with 3D visualizations
- **Anomaly Detection**: Automatic identification of anomalous events
- **Predictions**: Machine learning models for event prediction

### 🚨 **Alert System**
- **Real-time Alerts**: Notifications for high-intensity events
- **Severity Classification**: High, Medium, Low
- **Alert Dashboard**: Dedicated interface for management

### 🛠️ **Interface Technologies**
- **REST API**: Complete interface for system interaction
- **WebSockets**: Real-time updates (planned)
- **Database**: Persistent storage with PostgreSQL

## 🛠️ Technologies

- **Python 3.11**
- **FastAPI** - Modern web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - Python ORM
- **Docker & Docker Compose** - Containerization
- **Pandas & NumPy** - Data analysis
- **Scikit-learn** - Machine Learning
- **Matplotlib & Seaborn** - Visualization
- **PgAdmin** - Database administration interface

## 📋 Prerequisites

- Docker Desktop
- Docker Compose
- PowerShell (Windows)

## 🏃‍♂️ How to Run

### Option 1: PowerShell Script (Recommended)
```powershell
# Start all services
.\scripts\start.ps1

# Stop all services
.\scripts\stop.ps1
```

### Option 2: Manual Docker Compose
```bash
# Start services
docker-compose up --build -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f app
```

### Option 3: Local Streamlit
```powershell
# Run only Streamlit locally
.\scripts\run_streamlit.ps1
```

### Option 4: Demo Mode
```powershell
# Run demo with sample data
.\scripts\demo.ps1
```

### Option 5: Individual Services
```bash
# Database only
docker-compose up -d db

# FastAPI + Database
docker-compose up -d db app

# All except Grafana
docker-compose up -d db app streamlit pgadmin
```

## 🌐 Access Points

After starting the services:

- **🎛️ Main Dashboard**: http://localhost:8000/dashboard
- **📊 Streamlit Analytics**: http://localhost:8501
- **📈 Grafana Monitoring**: http://localhost:3000
  - User: `admin`
  - Password: `admin123`
- **📖 API Documentation**: http://localhost:8000/docs
- **📋 API Redoc**: http://localhost:8000/redoc
- **🗄️ PgAdmin**: http://localhost:5050
  - Email: `admin@previsao.com`
  - Password: `admin123`

## 🗄️ Database

### PostgreSQL Connection
- **Host**: localhost
- **Port**: 5432
- **Database**: previsao_solar
- **User**: postgres
- **Password**: postgres123

### Main Tables
- `sep_events` - Solar energetic particle events
- `predictions` - Model-generated predictions
- `alerts` - System alerts
- `model_metrics` - Model performance metrics

## 📊 API Endpoints

### Data Collection
- `POST /data/collect` - Collect and store data
- `GET /data/events` - List stored events
- `GET /data/high-intensity` - High-intensity events

### Analytics
- `POST /analysis/correlations` - Correlation analysis
- `POST /analysis/clustering` - Event clustering
- `POST /analysis/prediction` - Generate predictions

### Monitoring
- `GET /alerts` - List active alerts
- `GET /health` - Application status

## 🏗️ Project Structure

```
solar-impact-insights/
├── app/                    # Main application
│   ├── main.py            # Entry point
│   └── api.py             # FastAPI routes
├── domain/                # Domain entities
│   └── entities.py        # Data classes
├── use_cases/            # Use cases
│   ├── analysis.py       # Statistical analysis
│   └── alerts.py         # Alert system
├── infrastructure/       # Infrastructure
│   ├── data_collection.py # Data collection
│   ├── visualization.py   # Visualizations
│   └── database/         # Database configuration
│       ├── models.py     # SQLAlchemy models
│       └── repository.py # Repositories
├── adapters/             # Adapters
│   └── data_adapter.py   # Data integration
├── data/                 # Data files
│   └── real_solar_data.csv # Solar event dataset
├── sql/                  # SQL scripts
│   └── init.sql          # Database initialization
├── scripts/              # Utility scripts
│   ├── start.ps1         # Start services
│   ├── stop.ps1          # Stop services
│   ├── run_streamlit.ps1 # Run Streamlit locally
│   ├── populate_database.py # Database population
│   ├── collect_real_data.py # Real data collection
│   └── demo.ps1          # Demo script
├── static/               # Static web assets
│   ├── dashboard.css     # Dashboard styles
│   └── dashboard.js      # Dashboard JavaScript
├── templates/            # HTML templates
│   └── dashboard.html    # Main dashboard template
├── grafana/              # Grafana configuration
│   └── dashboard.json    # Grafana dashboard config
├── logs/                 # Application logs
├── streamlit_app.py      # Streamlit application
├── demo_api.py          # API demonstration script
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Application image
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

## 🔧 Development

### Local Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env

# Run database only
docker-compose up -d db

# Run local application
python app/main.py

# Run Streamlit locally
python streamlit_app.py
```

### Data Management
```powershell
# Populate database with sample data
python scripts/populate_database.py

# Collect real solar data
python scripts/collect_real_data.py

# Quick data collection
python scripts/quick_collect.py
```

### Debugging
```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db

# Access application container
docker-compose exec app bash

# Access database
docker-compose exec db psql -U postgres -d previsao_solar
```

## 📈 Usage Example

1. **Start the services**:
   ```powershell
   .\scripts\start.ps1
   ```

2. **Access the dashboard**: http://localhost:8000/dashboard

3. **Collect data**:
   - Click "Collect Mock Data"

4. **Run analyses**:
   - "Correlation Analysis"
   - "Clustering"
   - "Generate Predictions"

5. **Monitor**:
   - "View Alerts"
   - "High-Intensity Events"

## 🚨 Alerts and Monitoring

The system has automatic alerts for:
- High-intensity events (SEP > 5.0)
- Data anomalies detected
- Critical event predictions

## 📝 Logs

Logs are stored in:
- Container: `/app/logs/`
- Local: `./logs/`

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is under the MIT license.

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Restart services: `.\scripts\stop.ps1` and `.\scripts\start.ps1`
3. Verify all ports are available

## 🔄 Updates

To update the system:
```powershell
# Stop services
.\scripts\stop.ps1

# Rebuild
docker-compose build --no-cache

# Start
.\scripts\start.ps1
```
