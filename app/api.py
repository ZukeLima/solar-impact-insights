import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from infrastructure.database.models import get_db, create_tables
from infrastructure.database.repository import DatabaseRepository
from domain.entities import SEPData
from use_cases.analysis import analisar_correlacoes, clusterizar_eventos, prever_eventos
from use_cases.alerts import gerar_alertas
from infrastructure.data_collection import coletar_dados_reais, gerar_dados_mock
from infrastructure.visualization import visualizar_dados
from adapters.data_adapter import integrar_dados
from datetime import datetime, timedelta
from typing import List, Optional
import pandas as pd
import uvicorn

# Create FastAPI app
app = FastAPI(
    title="Previsão Solar API",
    description="API para análise e previsão de eventos solares",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "API de Previsão Solar - Sistema de Análise de Eventos Solares"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

@app.post("/data/collect")
async def collect_data(use_mock: bool = True, db: Session = Depends(get_db)):
    """Collect and store SEP data"""
    try:
        repo = DatabaseRepository(db)
        
        if use_mock:
            sep, temp, ice, ozone, geomag = gerar_dados_mock()
        else:
            sep, temp, ice, ozone, geomag = coletar_dados_reais()
        
        # Integrate data
        merged_data = integrar_dados(sep, temp, ice, ozone, geomag)
        
        # Convert to SEPData entities and save to database
        sep_data_list = []
        for _, row in merged_data.iterrows():
            sep_data = SEPData(
                date=row['date'],
                sep_intensity=row['sep_intensity'],
                temperature=row['temperature'],
                ice_extent=row['ice_extent'],
                ozone_level=row['ozone_level'],
                kp_index=row['kp_index']
            )
            sep_data_list.append(sep_data)
        
        # Save to database
        db_events = repo.save_sep_events_bulk(sep_data_list)
        
        return {
            "message": f"Successfully collected and stored {len(db_events)} events",
            "data_points": len(db_events),
            "date_range": {
                "start": merged_data['date'].min().isoformat(),
                "end": merged_data['date'].max().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/events")
async def get_events(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db)
):
    """Get SEP events from database"""
    try:
        repo = DatabaseRepository(db)
        
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        events = repo.get_sep_events(start_dt, end_dt, limit)
        
        return {
            "events": [
                {
                    "id": str(event.id),
                    "date": event.date.isoformat(),
                    "sep_intensity": event.sep_intensity,
                    "temperature": event.temperature,
                    "ice_extent": event.ice_extent,
                    "ozone_level": event.ozone_level,
                    "kp_index": event.kp_index,
                    "cluster_id": event.cluster_id
                }
                for event in events
            ],
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/correlations")
async def analyze_correlations(db: Session = Depends(get_db)):
    """Analyze correlations in the data"""
    try:
        repo = DatabaseRepository(db)
        df = repo.get_sep_events_as_dataframe()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        correlations = analisar_correlacoes(df)
        
        return {
            "message": "Correlation analysis completed",
            "data_points": len(df),
            "correlations": correlations.to_dict() if correlations is not None else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/clustering")
async def perform_clustering(db: Session = Depends(get_db)):
    """Perform clustering analysis on the data"""
    try:
        repo = DatabaseRepository(db)
        df = repo.get_sep_events_as_dataframe()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        clustered_data = clusterizar_eventos(df)
        
        # Update cluster information in database
        for _, row in clustered_data.iterrows():
            if pd.notna(row['cluster']):
                # Find corresponding database record and update cluster
                events = repo.get_sep_events(row['date'], row['date'])
                if events:
                    event = events[0]
                    event.cluster_id = int(row['cluster'])
                    repo.db.commit()
        
        return {
            "message": "Clustering analysis completed",
            "data_points": len(clustered_data),
            "clusters_found": clustered_data['cluster'].nunique() if 'cluster' in clustered_data else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/prediction")
async def make_prediction(db: Session = Depends(get_db)):
    """Generate predictions for future events"""
    try:
        repo = DatabaseRepository(db)
        df = repo.get_sep_events_as_dataframe()
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        forecast = prever_eventos(df)
        
        # Save predictions to database
        prediction_date = datetime.utcnow()
        for _, row in forecast.iterrows():
            repo.save_prediction(
                prediction_date=prediction_date,
                predicted_for_date=row['date'],
                predicted_intensity=row['predicted_sep_intensity'],
                model_version="v1.0"
            )
        
        return {
            "message": "Predictions generated successfully",
            "predictions": len(forecast),
            "forecast_period": {
                "start": forecast['date'].min().isoformat(),
                "end": forecast['date'].max().isoformat()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    """Get active alerts"""
    try:
        repo = DatabaseRepository(db)
        alerts = repo.get_active_alerts()
        
        return {
            "alerts": [
                {
                    "id": str(alert.id),
                    "type": alert.alert_type,
                    "severity": alert.severity,
                    "message": alert.message,
                    "event_date": alert.event_date.isoformat(),
                    "threshold_value": alert.threshold_value,
                    "actual_value": alert.actual_value,
                    "created_at": alert.created_at.isoformat()
                }
                for alert in alerts
            ],
            "count": len(alerts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/data/high-intensity")
async def get_high_intensity_events(threshold: float = 5.0, db: Session = Depends(get_db)):
    """Get high intensity events"""
    try:
        repo = DatabaseRepository(db)
        events = repo.get_high_intensity_events(threshold)
        
        return {
            "events": [
                {
                    "id": str(event.id),
                    "date": event.date.isoformat(),
                    "sep_intensity": event.sep_intensity,
                    "temperature": event.temperature,
                    "kp_index": event.kp_index
                }
                for event in events
            ],
            "count": len(events),
            "threshold": threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Advanced dashboard with multiple views"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/simple-dashboard", response_class=HTMLResponse)
async def simple_dashboard():
    """Simple dashboard HTML"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Previsão Solar Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .card { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 5px; }
            .btn { background-color: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .btn:hover { background-color: #0056b3; }
        </style>
    </head>
    <body>
        <h1>🌞 Dashboard de Previsão Solar</h1>
        
        <div class="card">
            <h3>Coleta de Dados</h3>
            <button class="btn" onclick="collectData()">Coletar Dados Mock</button>
            <button class="btn" onclick="getEvents()">Listar Eventos</button>
        </div>
        
        <div class="card">
            <h3>Análises</h3>
            <button class="btn" onclick="analyzeCorrelations()">Análise de Correlações</button>
            <button class="btn" onclick="performClustering()">Clustering</button>
            <button class="btn" onclick="makePrediction()">Gerar Previsões</button>
        </div>
        
        <div class="card">
            <h3>Monitoramento</h3>
            <button class="btn" onclick="getAlerts()">Ver Alertas</button>
            <button class="btn" onclick="getHighIntensity()">Eventos de Alta Intensidade</button>
        </div>
        
        <div id="results" class="card" style="display:none;">
            <h3>Resultados</h3>
            <pre id="output"></pre>
        </div>
        
        <script>
            async function apiCall(endpoint, method = 'GET') {
                try {
                    const response = await fetch(endpoint, { method });
                    const data = await response.json();
                    document.getElementById('results').style.display = 'block';
                    document.getElementById('output').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('results').style.display = 'block';
                    document.getElementById('output').textContent = 'Erro: ' + error.message;
                }
            }
            
            function collectData() { apiCall('/data/collect', 'POST'); }
            function getEvents() { apiCall('/data/events'); }
            function analyzeCorrelations() { apiCall('/analysis/correlations', 'POST'); }
            function performClustering() { apiCall('/analysis/clustering', 'POST'); }
            function makePrediction() { apiCall('/analysis/prediction', 'POST'); }
            function getAlerts() { apiCall('/alerts'); }
            function getHighIntensity() { apiCall('/data/high-intensity'); }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/metrics/dashboard")
async def dashboard_metrics(db: Session = Depends(get_db)):
    """Get comprehensive dashboard metrics"""
    try:
        repo = DatabaseRepository(db)
        
        # Get recent events
        events = repo.get_recent_events(30)
        all_events = repo.get_sep_events()
        high_intensity = repo.get_high_intensity_events()
        alerts = repo.get_active_alerts()
        
        # Calculate metrics
        total_events = len(all_events)
        avg_intensity = sum(e.sep_intensity for e in events) / len(events) if events else 0
        high_intensity_count = len(high_intensity)
        active_alerts_count = len(alerts)
        
        # Trend calculations (simplified)
        if len(events) >= 7:
            recent_week = events[:7]
            previous_week = events[7:14] if len(events) >= 14 else []
            
            recent_avg = sum(e.sep_intensity for e in recent_week) / len(recent_week)
            previous_avg = sum(e.sep_intensity for e in previous_week) / len(previous_week) if previous_week else recent_avg
            
            trend_percentage = ((recent_avg - previous_avg) / previous_avg * 100) if previous_avg > 0 else 0
        else:
            trend_percentage = 0
        
        # Event distribution by intensity
        intensity_distribution = {
            "low": len([e for e in events if e.sep_intensity < 2.0]),
            "medium": len([e for e in events if 2.0 <= e.sep_intensity < 5.0]),
            "high": len([e for e in events if e.sep_intensity >= 5.0])
        }
        
        # Alert distribution
        alert_distribution = {}
        for alert in alerts:
            severity = alert.severity.lower()
            alert_distribution[severity] = alert_distribution.get(severity, 0) + 1
        
        return {
            "summary": {
                "total_events": total_events,
                "avg_intensity": round(avg_intensity, 2),
                "high_intensity_events": high_intensity_count,
                "active_alerts": active_alerts_count,
                "trend_percentage": round(trend_percentage, 1)
            },
            "distributions": {
                "intensity": intensity_distribution,
                "alerts": alert_distribution
            },
            "recent_events": [
                {
                    "date": event.date.isoformat(),
                    "intensity": event.sep_intensity,
                    "temperature": event.temperature
                }
                for event in events[:10]
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/correlations")
async def correlation_metrics(db: Session = Depends(get_db)):
    """Get correlation analysis metrics"""
    try:
        repo = DatabaseRepository(db)
        df = repo.get_sep_events_as_dataframe()
        
        if df.empty:
            return {"correlations": {}, "message": "No data available"}
        
        # Calculate correlations
        numeric_cols = ['sep_intensity', 'temperature', 'ice_extent', 'ozone_level', 'kp_index']
        correlations = {}
        
        for col in numeric_cols:
            if col != 'sep_intensity' and col in df.columns:
                corr = df['sep_intensity'].corr(df[col])
                correlations[col] = round(corr, 3) if pd.notna(corr) else 0
        
        return {
            "correlations": correlations,
            "strongest_positive": max(correlations.items(), key=lambda x: x[1]) if correlations else None,
            "strongest_negative": min(correlations.items(), key=lambda x: x[1]) if correlations else None,
            "data_points": len(df)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/anomalies")
async def anomaly_metrics(db: Session = Depends(get_db)):
    """Get anomaly detection metrics"""
    try:
        repo = DatabaseRepository(db)
        df = repo.get_sep_events_as_dataframe()
        
        if df.empty:
            return {"anomalies": [], "count": 0}
        
        # Simple anomaly detection using IQR
        Q1 = df['sep_intensity'].quantile(0.25)
        Q3 = df['sep_intensity'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = df[
            (df['sep_intensity'] < lower_bound) | 
            (df['sep_intensity'] > upper_bound)
        ]
        
        anomaly_list = []
        for _, row in anomalies.iterrows():
            anomaly_list.append({
                "date": row['date'].isoformat(),
                "intensity": row['sep_intensity'],
                "type": "high" if row['sep_intensity'] > upper_bound else "low",
                "deviation": abs(row['sep_intensity'] - df['sep_intensity'].median())
            })
        
        return {
            "anomalies": anomaly_list,
            "count": len(anomaly_list),
            "threshold": {
                "lower": round(lower_bound, 2),
                "upper": round(upper_bound, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
