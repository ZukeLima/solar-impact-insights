import pandas as pd
import numpy as np
import requests
from io import StringIO

def coletar_dados_reais(start_date='2024-01-01', end_date='2025-08-03'):
    try:
        # SEP da NASA DONKI
        sep_url = f"https://api.nasa.gov/DONKI/SEP?startDate={start_date}&endDate={end_date}&api_key=DEMO_KEY"
        sep_response = requests.get(sep_url)
        sep_data = pd.DataFrame(sep_response.json()) if sep_response.status_code == 200 else pd.DataFrame()

        # Temperatura global da NASA GISS
        giss_url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"
        giss_response = requests.get(giss_url)
        if giss_response.status_code == 200:
            giss_csv = StringIO(giss_response.text)
            temp_data = pd.read_csv(giss_csv, skiprows=7)
            temp_data = temp_data[temp_data['Year'].isin([2024, 2025])]
            temp_data = temp_data.melt(id_vars=['Year'], value_vars=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug'])
            temp_data['date'] = pd.to_datetime(temp_data['Year'].astype(str) + '-' + temp_data['variable'] + '-01')
            temp_data = temp_data[['date', 'value']].rename(columns={'value': 'temperature'})
        else:
            temp_data = pd.DataFrame()

        # Extensão de gelo polar da NSIDC
        ice_url = "https://noaadata.apps.nsidc.org/NOAA/G02135/north/daily/data/N_seaice_extent_daily_v3.0.csv"
        ice_data = pd.read_csv(ice_url)
        ice_data['date'] = pd.to_datetime(ice_data[['Year', 'Month', 'Day']].astype(str).agg('-'.join, axis=1))
        ice_data = ice_data[(ice_data['date'] >= start_date) & (ice_data['date'] <= end_date)]
        ice_data = ice_data[['date', 'Extent']].rename(columns={'Extent': 'ice_extent'})

        # Ozônio e Geomagnetismo: Placeholders (adapte com APIs reais)
        ozone_data = pd.DataFrame()
        geomag_data = pd.DataFrame()

        return sep_data, temp_data, ice_data, ozone_data, geomag_data
    except Exception as e:
        print(f"Erro na coleta de dados reais: {e}")
        return [pd.DataFrame()] * 5

def gerar_dados_mock(start_date='2024-01-01', periods=581):
    dates = pd.date_range(start=start_date, periods=periods, freq='D')
    sep_intensity = np.random.normal(50, 10, periods) + np.sin(np.linspace(0, 10, periods)) * 20
    temperature = np.random.normal(15, 2, periods) + np.sin(np.linspace(0, 10, periods)) * 1.5 + sep_intensity * 0.01
    ice_extent = 10000 - np.random.normal(100, 20, periods) - np.sin(np.linspace(0, 10, periods)) * 50 - sep_intensity * 0.05
    ozone_level = np.random.normal(300, 20, periods) - sep_intensity * 0.1
    kp_index = np.random.normal(3, 1, periods) + sep_intensity * 0.02

    sep_data = pd.DataFrame({'date': dates, 'sep_intensity': sep_intensity})
    temp_data = pd.DataFrame({'date': dates, 'temperature': temperature})
    ice_data = pd.DataFrame({'date': dates, 'ice_extent': ice_extent})
    ozone_data = pd.DataFrame({'date': dates, 'ozone_level': ozone_level})
    geomag_data = pd.DataFrame({'date': dates, 'kp_index': kp_index})

    return sep_data, temp_data, ice_data, ozone_data, geomag_data