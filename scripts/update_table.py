import psycopg2

def update_table_structure():
    conn = psycopg2.connect(
        host='localhost',
        database='previsao_solar',
        user='postgres',
        password='postgres123',
        port='5432'
    )
    cur = conn.cursor()

    print('🔧 Adicionando colunas faltantes...')

    # Adicionar colunas faltantes
    colunas_adicionar = [
        'ALTER TABLE sep_events ADD COLUMN IF NOT EXISTS solar_flux FLOAT',
        'ALTER TABLE sep_events ADD COLUMN IF NOT EXISTS aurora_intensity FLOAT', 
        'ALTER TABLE sep_events ADD COLUMN IF NOT EXISTS sunspot_count FLOAT',
        'ALTER TABLE sep_events ADD COLUMN IF NOT EXISTS cosmic_ray_intensity FLOAT'
    ]

    for sql in colunas_adicionar:
        try:
            cur.execute(sql)
            col_name = sql.split('ADD COLUMN IF NOT EXISTS ')[1].split(' ')[0]
            print(f'✅ {col_name} adicionada')
        except Exception as e:
            print(f'❌ Erro: {e}')

    conn.commit()

    # Verificar estrutura final
    cur.execute('''
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'sep_events'
        ORDER BY ordinal_position
    ''')

    columns = cur.fetchall()
    print('\n📋 ESTRUTURA FINAL:')
    for col_name, col_type in columns:
        print(f'  - {col_name}: {col_type}')

    cur.close()
    conn.close()
    print('\n✅ Estrutura da tabela atualizada!')

if __name__ == "__main__":
    update_table_structure()
