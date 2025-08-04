#!/usr/bin/env python3
"""
Script para popular o banco de dados com os dados coletados
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys
import time

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from infrastructure.database.models import SEPEvent
    from domain.entities import SolarEvent
    from use_cases.analysis import SolarAnalysisService
    from use_cases.alerts import AlertService
    print("✅ Importações realizadas com sucesso")
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
    print("Instalando dependências...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "sqlalchemy", "psycopg2-binary", "pandas", "numpy", "scikit-learn"], 
                   check=True)

def get_database_connection():
    """Conecta ao banco de dados"""
    print("🔌 Conectando ao banco de dados...")
    
    # String de conexão para PostgreSQL
    DATABASE_URL = "postgresql://solar_user:solar_pass@localhost:5432/solar_db"
    
    try:
        engine = create_engine(DATABASE_URL)
        # Testar conexão
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Conexão com banco estabelecida")
        return engine
    except Exception as e:
        print(f"❌ Erro ao conectar com banco: {e}")
        print("🔄 Tentando aguardar e reconectar...")
        time.sleep(10)
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                print("✅ Conexão estabelecida após retry")
            return engine
        except Exception as e2:
            print(f"❌ Falha definitiva na conexão: {e2}")
            return None

def load_data():
    """Carrega dados do arquivo CSV"""
    print("📂 Carregando dados do arquivo...")
    
    file_path = 'data/real_solar_data.csv'
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        print("Execute primeiro: python scripts/quick_collect.py")
        return None
    
    try:
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        print(f"✅ Dados carregados: {len(df):,} registros")
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar dados: {e}")
        return None

def populate_database(engine, df):
    """Popula o banco de dados"""
    print("💾 Populando banco de dados...")
    
    try:
        # Limpar tabela existente
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM sep_events"))
            conn.commit()
            print("🗑️ Dados antigos removidos")
        
        # Preparar dados para inserção
        df_insert = df.copy()
        df_insert = df_insert.rename(columns={
            'datetime': 'timestamp',
            'sep_intensity': 'intensity',
            'kp_index': 'kp_index',
            'solar_flux': 'solar_flux',
            'sunspot_number': 'sunspot_count',
            'aurora_activity': 'aurora_intensity',
            'cosmic_ray_count': 'cosmic_ray_intensity'
        })
        
        # Adicionar colunas necessárias
        df_insert['event_type'] = 'SEP'
        df_insert['severity'] = df_insert['intensity'].apply(lambda x: 
            'HIGH' if x > 7 else 'MEDIUM' if x > 4 else 'LOW')
        df_insert['location'] = 'GLOBAL'
        
        # Selecionar apenas as colunas que existem na tabela
        columns_to_insert = [
            'timestamp', 'event_type', 'intensity', 'severity', 'location',
            'kp_index', 'solar_flux', 'sunspot_count', 'aurora_intensity', 
            'cosmic_ray_intensity', 'temperature', 'ice_extent', 'ozone_level'
        ]
        
        df_final = df_insert[columns_to_insert]
        
        # Inserir em batches
        batch_size = 1000
        total_batches = len(df_final) // batch_size + 1
        
        for i in range(0, len(df_final), batch_size):
            batch = df_final.iloc[i:i+batch_size]
            batch.to_sql('sep_events', engine, if_exists='append', index=False)
            batch_num = (i // batch_size) + 1
            print(f"📦 Batch {batch_num}/{total_batches} inserido ({len(batch)} registros)")
        
        print(f"✅ {len(df_final):,} registros inseridos com sucesso")
        
        # Verificar inserção
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sep_events"))
            count = result.scalar()
            print(f"🔍 Verificação: {count:,} registros na tabela")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao popular banco: {e}")
        return False

def generate_alerts(engine):
    """Gera alertas baseados nos dados"""
    print("🚨 Gerando alertas...")
    
    try:
        with engine.connect() as conn:
            # Buscar eventos de alta intensidade
            high_intensity_query = text("""
                SELECT COUNT(*) FROM sep_events 
                WHERE intensity > 7 AND timestamp > NOW() - INTERVAL '7 days'
            """)
            result = conn.execute(high_intensity_query)
            high_events = result.scalar()
            
            print(f"🔴 Eventos de alta intensidade (últimos 7 dias): {high_events}")
            
            # Buscar tendência recente
            trend_query = text("""
                SELECT AVG(intensity) as avg_intensity 
                FROM sep_events 
                WHERE timestamp > NOW() - INTERVAL '24 hours'
            """)
            result = conn.execute(trend_query)
            avg_intensity = result.scalar() or 0
            
            print(f"📈 Intensidade média (últimas 24h): {avg_intensity:.2f}")
            
            if avg_intensity > 5:
                print("⚠️ ALERTA: Atividade solar elevada detectada!")
            else:
                print("✅ Atividade solar dentro do normal")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao gerar alertas: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 POPULANDO BANCO DE DADOS")
    print("=" * 50)
    
    # Conectar ao banco
    engine = get_database_connection()
    if not engine:
        print("❌ Não foi possível conectar ao banco. Verifique se o Docker está rodando.")
        return False
    
    # Carregar dados
    df = load_data()
    if df is None:
        return False
    
    # Popular banco
    if not populate_database(engine, df):
        return False
    
    # Gerar alertas
    generate_alerts(engine)
    
    print("\n" + "=" * 50)
    print("🎉 POPULAÇÃO DO BANCO CONCLUÍDA!")
    print("\n🌐 ACESSE O DASHBOARD:")
    print("📊 Streamlit: http://localhost:8501")
    print("📈 Grafana: http://localhost:3000")
    print("🗄️ PgAdmin: http://localhost:5050")
    
    print("\n📊 ESTATÍSTICAS DOS DADOS:")
    print(f"📅 Período: {df['datetime'].min()} até {df['datetime'].max()}")
    print(f"📊 Total de registros: {len(df):,}")
    print(f"🔴 Eventos alta intensidade: {len(df[df['sep_intensity'] > 7]):,}")
    print(f"🟡 Eventos média intensidade: {len(df[(df['sep_intensity'] > 4) & (df['sep_intensity'] <= 7)]):,}")
    print(f"🟢 Eventos baixa intensidade: {len(df[df['sep_intensity'] <= 4]):,}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
