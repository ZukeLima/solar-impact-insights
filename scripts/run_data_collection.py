#!/usr/bin/env python3
"""
Script simplificado para coletar e popular o banco com dados reais
Execute este script para obter dados reais de múltiplas fontes
"""

import sys
import os
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_data_collection():
    """Executa a coleta de dados reais"""
    
    print("🌞 COLETANDO DADOS REAIS DE APIS PÚBLICAS")
    print("=" * 50)
    print()
    
    try:
        # Executar coleta de dados
        logger.info("Executando coleta de dados reais...")
        
        # Importar e executar o coletor
        from collect_real_data import main as collect_main
        collect_main()
        
        print("\n✅ Coleta de dados concluída!")
        print("\nDados coletados de:")
        print("📡 NOAA Space Weather - Índices Kp e fluxo solar")
        print("☀️ SILSO - Dados de manchas solares")
        print("🌌 Aurora - Atividade auroral")
        print("⚡ Raios cósmicos - Contadores de nêutrons")
        print("🌡️ NASA - Dados climáticos")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro na coleta: {e}")
        return False

def main():
    print("🚀 INICIANDO COLETA DE DADOS REAIS")
    print("Este script coleta dados de múltiplas APIs públicas")
    print("para fornecer informações reais sobre atividade solar")
    print()
    
    success = run_data_collection()
    
    if success:
        print("\n🎉 SUCESSO!")
        print("Os dados foram coletados e salvos em:")
        print("📁 data/real_solar_data.csv")
        print("📁 data/real_solar_data.json")
        print()
        print("Próximos passos:")
        print("1. Execute o container: docker-compose up -d")
        print("2. Popular banco: python scripts/populate_real_data.py")
        print("3. Acesse: http://localhost:8501")
    else:
        print("\n❌ Erro na coleta de dados")
        print("Verifique sua conexão com a internet e tente novamente")

if __name__ == "__main__":
    main()
