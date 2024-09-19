
# PROPOSTA:
Agrupar as informações por endossantes, listando suas duplicatas ativas, finalizadas e canceladas e aplicar em um modelo.

## Campos utilizados:
 - NOME_ENDOSSER
 - State

## Base do modelo

Com base nas informações da coluna de *state*, foi desenvolvida uma tabela dinâmica, na qual foi
realizada uma análise por endossante. Para cada análise foi criada uma nova coluna, para que fosse implementada no modelo, abaixo segue as colunas derivadas da coluna *state*:

| #   | Coluna        | Descrição                             |
| --- | ------------- | ------------------------------------- |
| 1   | active        | Quantidade de duplicatas ativas;      |
| 2   | canceled      | Quantidade de duplicatas canceladas;  |
| 3   | finished      | Quantidade de duplicatas finalizadas; |
| 4   | total         | Total de duplicatas;                  |
| 5   | perc_finished | Percentual de duplicatas finalizadas; |
| 6   | perc_canceled | Percentual de duplicatas canceladas;  |

Também foi realizado um estudo da tabela de *asset_trade_bills*, visando encontrar padrões de comportamento entre os endossantes e definir faixas de score para cada categoria listada acima. Métodos como: análise de histograma, desvio padrão, mediana, intervalos interquartis, média e conjunto, foram aplicados em prol de definir as escalas de pontuação.

Para as colunas 3, 4, 5 e 6 foram definidas quatro categorias para classificar os valores de cada endossante, referenciando em grau de importância com as letras A, B, C, D, respectivamente. Assim foram adicionadas as colunas:

| #   | Coluna              | Descrição                                  |
| --- | ------------------- | ------------------------------------------ |
| 7   | class_finished      | Classificação de Finalizadas               |
| 8   | class_perc_finished | Classificação de Percentual de finalizadas |
| 9   | class_perc_canceled | Classificação de Percentual de canceladas  |
| 10  | class_total         | Classificação de Total                     |
Por fim, foi criado uma média para as colunas de classificação, no qual é definido qual é o resultado aproximado daquele endossante.
# Algoritmo
O algoritmo utilizado foi Árvore de Classificação, para encontrar qual seria a média de classificação de cada endossante.
Esse foi o resultado da matriz de confusão:
![[{D9D2172B-CEE1-462F-AEFA-A8B01AC5158F}.png]]
Baseado nos resultados, devido os dados serem agrupados por endossante e a média de classificação ter sido aproximada e arredondada, as informações dos endossantes tiveram valores  muito semelhantes, ocasionando numa influência em cima do resultado do modelo. A maior parte dos fornecedores foram classificados como B, e as demais categorias tiveram uma defasagem de informação, gerando poucos resultados. Isso garante uma assertividade muito superior para os endossantes do grupo B e uma incerteza ainda maior para as demais categorias. Dado o objetivo ser garantir uma pontuação assertiva para todas as categorias, a base do modelo desenvolvido em complemento à utilização de um algoritmo de Árvore de classificação, não atende a proposta do Score.

