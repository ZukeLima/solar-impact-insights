-- Database initialization script
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables for solar event prediction data
CREATE TABLE IF NOT EXISTS sep_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date TIMESTAMP NOT NULL,
    sep_intensity FLOAT NOT NULL,
    temperature FLOAT,
    ice_extent FLOAT,
    ozone_level FLOAT,
    kp_index FLOAT,
    solar_flux FLOAT,
    aurora_intensity FLOAT,
    sunspot_count FLOAT,
    cosmic_ray_intensity FLOAT,
    cluster_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for date queries
CREATE INDEX IF NOT EXISTS idx_sep_events_date ON sep_events(date);
CREATE INDEX IF NOT EXISTS idx_sep_events_cluster ON sep_events(cluster_id);

-- Create table for predictions
CREATE TABLE IF NOT EXISTS predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_date TIMESTAMP NOT NULL,
    predicted_for_date TIMESTAMP NOT NULL,
    predicted_intensity FLOAT NOT NULL,
    confidence_score FLOAT,
    model_version VARCHAR(50),
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_predictions_for_date ON predictions(predicted_for_date);

-- Create table for alerts
CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    threshold_value FLOAT,
    actual_value FLOAT,
    event_date TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_active ON alerts(is_active);

-- Create table for model performance metrics
CREATE TABLE IF NOT EXISTS model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value FLOAT NOT NULL,
    evaluation_date TIMESTAMP NOT NULL,
    dataset_size INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_model_metrics_name ON model_metrics(model_name);
CREATE INDEX IF NOT EXISTS idx_model_metrics_date ON model_metrics(evaluation_date);

-- Create function to update timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for sep_events
CREATE TRIGGER update_sep_events_updated_at 
    BEFORE UPDATE ON sep_events 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data
INSERT INTO sep_events (date, sep_intensity, temperature, ice_extent, ozone_level, kp_index) VALUES
    ('2024-01-01 00:00:00', 1.5, -0.2, 15.2, 285.0, 2.1),
    ('2024-01-02 00:00:00', 2.3, -0.1, 15.1, 286.5, 2.8),
    ('2024-01-03 00:00:00', 3.1, 0.1, 14.9, 284.2, 3.5);

-- Create views for common queries
CREATE OR REPLACE VIEW recent_events AS
SELECT * FROM sep_events 
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;

CREATE OR REPLACE VIEW high_intensity_events AS
SELECT * FROM sep_events 
WHERE sep_intensity > 5.0
ORDER BY date DESC;
