import pandas as pd
import psycopg2
from datetime import datetime

def populate_database():
    print('📂 Carregando dados...')
    df = pd.read_csv('data/real_solar_data.csv')
    df['datetime'] = pd.to_datetime(df['datetime'])
    print(f'✅ {len(df):,} registros carregados')

    print('🔌 Conectando ao banco...')
    conn = psycopg2.connect(
        host='localhost',
        database='previsao_solar',
        user='postgres',
        password='postgres123',
        port='5432'
    )
    cur = conn.cursor()
    print('✅ Conectado ao banco')

    print('🗑️ Limpando tabela...')
    cur.execute('DELETE FROM sep_events')

    print('📊 Preparando dados...')
    data_to_insert = []
    for _, row in df.iterrows():
        data_to_insert.append((
            row['datetime'],
            float(row['sep_intensity']),
            float(row['temperature']),
            float(row['ice_extent']),
            float(row['ozone_level']),
            float(row['kp_index']),
            float(row['solar_flux']),
            float(row['aurora_activity']),
            int(row['sunspot_number']),
            float(row['cosmic_ray_count'])
        ))

    print('💾 Inserindo dados...')
    batch_size = 1000
    total_batches = len(data_to_insert) // batch_size + 1

    for i in range(0, len(data_to_insert), batch_size):
        batch = data_to_insert[i:i+batch_size]
        cur.executemany('''
            INSERT INTO sep_events 
            (date, sep_intensity, temperature, ice_extent, ozone_level,
             kp_index, solar_flux, aurora_intensity, sunspot_count, cosmic_ray_intensity)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', batch)
        batch_num = (i // batch_size) + 1
        print(f'📦 Batch {batch_num}/{total_batches} inserido')

    conn.commit()

    # Estatísticas
    cur.execute('SELECT COUNT(*) FROM sep_events')
    count = cur.fetchone()[0]
    print(f'✅ {count:,} registros inseridos com sucesso!')

    cur.execute('SELECT COUNT(*) FROM sep_events WHERE sep_intensity > 7')
    high_events = cur.fetchone()[0]
    print(f'🔴 Eventos de alta intensidade: {high_events}')

    cur.execute('SELECT COUNT(*) FROM sep_events WHERE sep_intensity BETWEEN 4 AND 7')
    medium_events = cur.fetchone()[0]
    print(f'🟡 Eventos de média intensidade: {medium_events}')

    cur.execute('SELECT COUNT(*) FROM sep_events WHERE sep_intensity < 4')
    low_events = cur.fetchone()[0]
    print(f'🟢 Eventos de baixa intensidade: {low_events}')

    # Datas
    cur.execute('SELECT MIN(date), MAX(date) FROM sep_events')
    min_date, max_date = cur.fetchone()
    print(f'📅 Período: {min_date} até {max_date}')

    cur.close()
    conn.close()
    
    print('\n🎉 BANCO POPULADO COM SUCESSO!')
    print('\n🌐 ACESSE O DASHBOARD:')
    print('📊 Streamlit: http://localhost:8501')
    print('📈 Grafana: http://localhost:3000')
    print('🗄️ PgAdmin: http://localhost:5050')

if __name__ == "__main__":
    populate_database()
