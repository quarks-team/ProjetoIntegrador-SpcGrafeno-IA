import pandas as pd
from datetime import datetime
from collections import Counter
base = pd.read_excel('C:\\Temp\\TESTE.xlsx',sheet_name='Planilha1')
forecast = {
    'anterior': 0,
    'entrada': 0,
    'saida': 0,
    'resultado': 0,
    'restante': 0
}
datas = base['DAT PRAZO'].dropna().values
data = {'DATA': list(Counter(datas).keys()), 'QTD': list(Counter(datas).values())}
tabela_prazos = pd.DataFrame(data)
date = pd.concat([base['DATE'], base['DAT PRAZO']], ignore_index=True)

date = date.sort_values().unique().dropna()
dicio = {}
p, anterior, saida, resultado, saida_acumulada= 0,0,0,0,0

for d in date:
    dia = d.date()
    entrada = len(base[base['DATE']== d])
    f_acumulado = len(base[base['DATE']<= d])
    saida = int(tabela_prazos[tabela_prazos['DATA']== str(dia)[:10]]['QTD'].sum())
    saida_acumulada=int(tabela_prazos[tabela_prazos['DATA']<= d]['QTD'].sum())
    # print(str(d)[:10],str(datetime.today())[:10])
    if str(d)[:10] == str(datetime.today())[:10]: resultado =  f_acumulado
    else: resultado =  f_acumulado-saida_acumulada 
    dicio[str(dia)] =  {
        'DIA': str(dia),
        'SALDO DIA ANT.': anterior,
        'ENTRADA':  entrada ,
        'TOTAL_ACUMULADO': f_acumulado,
        'SAIDA': saida,
        'SAIDA ACUMULADA': saida_acumulada,
        'RESULTADO': resultado
    },
    anterior += entrada
for lin,x in dicio.items():
    print(lin,x, '\n')


print(tabela_prazos)