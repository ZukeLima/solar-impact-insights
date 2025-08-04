import matplotlib.pyplot as plt

def visualizar_dados(merged_data):
    plt.figure(figsize=(14, 7))
    plt.plot(merged_data['date'], merged_data['sep_intensity'], label='Intensidade SEP', color='orange')
    plt.plot(merged_data['date'], merged_data['temperature'] * 10, label='Temperatura (x10)', color='red')
    plt.plot(merged_data['date'], merged_data['ice_extent'] / 100, label='Extensão de Gelo (/100)', color='blue')
    plt.plot(merged_data['date'], merged_data['ozone_level'] / 10, label='Nível de Ozônio (/10)', color='green')
    plt.plot(merged_data['date'], merged_data['kp_index'] * 20, label='Índice Kp (x20)', color='purple')
    plt.legend()
    plt.title('Análise de Impactos: SEP e Variáveis Ambientais (Dados Mock)')
    plt.xlabel('Data')
    plt.ylabel('Valores Escalados')
    plt.grid(True)
    plt.show()