def gerar_alertas(forecast, threshold_temp=16):
    if forecast is not None and forecast.mean() > threshold_temp:
        print("Alerta: Previsão de temperatura alta - Risco para agricultura, logística polar e comunicações!")