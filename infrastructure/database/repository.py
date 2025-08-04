from sqlalchemy.orm import Session
from infrastructure.database.models import SEPEvent, Prediction, Alert, ModelMetric, get_db
from domain.entities import SEPData
from datetime import datetime
from typing import List, Optional
import pandas as pd

class DatabaseRepository:
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def save_sep_event(self, sep_data: SEPData) -> SEPEvent:
        """Save a SEP event to the database"""
        db_event = SEPEvent(
            date=sep_data.date,
            sep_intensity=sep_data.sep_intensity,
            temperature=sep_data.temperature,
            ice_extent=sep_data.ice_extent,
            ozone_level=sep_data.ozone_level,
            kp_index=sep_data.kp_index,
            cluster_id=sep_data.cluster
        )
        self.db.add(db_event)
        self.db.commit()
        self.db.refresh(db_event)
        return db_event
    
    def save_sep_events_bulk(self, sep_data_list: List[SEPData]) -> List[SEPEvent]:
        """Save multiple SEP events to the database"""
        db_events = []
        for sep_data in sep_data_list:
            db_event = SEPEvent(
                date=sep_data.date,
                sep_intensity=sep_data.sep_intensity,
                temperature=sep_data.temperature,
                ice_extent=sep_data.ice_extent,
                ozone_level=sep_data.ozone_level,
                kp_index=sep_data.kp_index,
                cluster_id=sep_data.cluster
            )
            db_events.append(db_event)
        
        self.db.add_all(db_events)
        self.db.commit()
        return db_events
    
    def get_sep_events(self, start_date: Optional[datetime] = None, 
                      end_date: Optional[datetime] = None,
                      limit: Optional[int] = None) -> List[SEPEvent]:
        """Get SEP events from the database with optional filters"""
        query = self.db.query(SEPEvent)
        
        if start_date:
            query = query.filter(SEPEvent.date >= start_date)
        if end_date:
            query = query.filter(SEPEvent.date <= end_date)
        
        query = query.order_by(SEPEvent.date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_sep_events_as_dataframe(self, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get SEP events as a pandas DataFrame"""
        events = self.get_sep_events(start_date, end_date)
        
        data = []
        for event in events:
            data.append({
                'date': event.date,
                'sep_intensity': event.sep_intensity,
                'temperature': event.temperature,
                'ice_extent': event.ice_extent,
                'ozone_level': event.ozone_level,
                'kp_index': event.kp_index,
                'cluster': event.cluster_id
            })
        
        return pd.DataFrame(data)
    
    def save_prediction(self, prediction_date: datetime, predicted_for_date: datetime,
                       predicted_intensity: float, confidence_score: float = None,
                       model_version: str = None, features: dict = None) -> Prediction:
        """Save a prediction to the database"""
        db_prediction = Prediction(
            prediction_date=prediction_date,
            predicted_for_date=predicted_for_date,
            predicted_intensity=predicted_intensity,
            confidence_score=confidence_score,
            model_version=model_version,
            features=features
        )
        self.db.add(db_prediction)
        self.db.commit()
        self.db.refresh(db_prediction)
        return db_prediction
    
    def save_alert(self, alert_type: str, severity: str, message: str,
                  event_date: datetime, threshold_value: float = None,
                  actual_value: float = None) -> Alert:
        """Save an alert to the database"""
        db_alert = Alert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            event_date=event_date,
            threshold_value=threshold_value,
            actual_value=actual_value
        )
        self.db.add(db_alert)
        self.db.commit()
        self.db.refresh(db_alert)
        return db_alert
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return self.db.query(Alert).filter(Alert.is_active == True).all()
    
    def save_model_metric(self, model_name: str, metric_name: str,
                         metric_value: float, evaluation_date: datetime,
                         dataset_size: int = None) -> ModelMetric:
        """Save model performance metric"""
        db_metric = ModelMetric(
            model_name=model_name,
            metric_name=metric_name,
            metric_value=metric_value,
            evaluation_date=evaluation_date,
            dataset_size=dataset_size
        )
        self.db.add(db_metric)
        self.db.commit()
        self.db.refresh(db_metric)
        return db_metric
    
    def get_high_intensity_events(self, threshold: float = 5.0) -> List[SEPEvent]:
        """Get events with high SEP intensity"""
        return self.db.query(SEPEvent).filter(
            SEPEvent.sep_intensity > threshold
        ).order_by(SEPEvent.date.desc()).all()
    
    def get_recent_events(self, days: int = 30) -> List[SEPEvent]:
        """Get events from the last N days"""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        return self.db.query(SEPEvent).filter(
            SEPEvent.date >= cutoff_date
        ).order_by(SEPEvent.date.desc()).all()
