import pandas as pd

def integrar_dados(sep_data, temp_data, ice_data, ozone_data, geomag_data):
    merged = sep_data.merge(temp_data, on='date', how='outer') \
                     .merge(ice_data, on='date', how='outer') \
                     .merge(ozone_data, on='date', how='outer') \
                     .merge(geomag_data, on='date', how='outer')
    merged = merged.dropna(subset=['sep_intensity'])  # Remover linhas sem SEP principal
    return merged