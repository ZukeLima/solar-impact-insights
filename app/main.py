import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from domain.entities import SEPData  # Não usado diretamente, mas para exemplo de domínio
from use_cases.analysis import analisar_correlacoes, clusterizar_eventos, prever_eventos
from use_cases.alerts import gerar_alertas
from infrastructure.data_collection import coletar_dados_reais, gerar_dados_mock
from infrastructure.visualization import visualizar_dados
from adapters.data_adapter import integrar_dados

if __name__ == "__main__":
    # Escolha: dados reais ou mock
    # sep, temp, ice, ozone, geomag = coletar_dados_reais()
    sep, temp, ice, ozone, geomag = gerar_dados_mock()

    merged_data = integrar_dados(sep, temp, ice, ozone, geomag)
    analisar_correlacoes(merged_data)
    merged_data = clusterizar_eventos(merged_data)
    forecast = prever_eventos(merged_data)
    visualizar_dados(merged_data)
    gerar_alertas(forecast)

    # Extensões futuras: Integre com Streamlit ou FastAPI aqui
    # Ex: import streamlit as st; st.title('Dashboard SEP'); st.line_chart(merged_data.set_index('date')[['sep_intensity', 'temperature']])