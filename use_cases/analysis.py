from scipy.stats import pearsonr
from scipy.cluster.vq import kmeans, vq
from statsmodels.tsa.arima.model import ARIMA

def analisar_correlacoes(merged_data):
    corrs = {}
    for var in ['temperature', 'ice_extent', 'ozone_level', 'kp_index']:
        corr, _ = pearsonr(merged_data['sep_intensity'], merged_data[var])
        corrs[var] = round(corr, 2)
    print("Correlações com Intensidade SEP:")
    for k, v in corrs.items():
        print(f"{k}: {v}")
    return corrs

def clusterizar_eventos(merged_data, n_clusters=3):
    data_cluster = merged_data[['sep_intensity', 'temperature', 'ice_extent']].values
    centroids, _ = kmeans(data_cluster, n_clusters)
    idx, _ = vq(data_cluster, centroids)
    merged_data['cluster'] = idx
    print("\nExemplo de clusters (0: baixa, 1: média, 2: alta):")
    print(merged_data[['date', 'sep_intensity', 'cluster']].head(10))
    return merged_data

def prever_eventos(merged_data, steps=30):
    try:
        model = ARIMA(merged_data['temperature'], order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=steps)
        print(f"\nPrevisão de temperatura para os próximos {steps} dias:")
        print(forecast)
        return forecast
    except Exception as e:
        print(f"Erro na previsão ARIMA: {e}")
        return None