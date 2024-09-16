# ProjetoIntegrador-SpcGrafeno-IA
Repositório dedicado ao desenvolvimento dos modelos de IA

Considerar:
- Duplicatas encerradas (**state**: *finished* ou *canceled*)
- Renegociações de prazo de pagamento.
- Área de negociação: Produtos ou serviços.
- Local de Pagamento: Cidade e Estado.

Abaixo será listado quais colunas podem ser utilizadas para o treinamento da IA baseado na tabela ASSET TRADE BILLS:
- kind
- state
- due_date
- new_due_date
- payment_place
- finished_at
- ballast_kind (?)
- update_reason_kind
- endosser_original_id

# 1 PROPOSTA DE TREINAMENTO

BASE DE DADOS: Asset Trade Bills

| Coluna                 | Explicação                                          |
| ---------------------- | --------------------------------------------------- |
| **kind<br>**           | Tipo de segmento do endossante: Produto ou Serviço. |
| **state**              | Status de andamento da duplicata.                   |
| **due_date<br>**       | Data de vencimento da duplicata.                    |
| **new_due_date<br>**   | Data de vencimento que foi renegociada.             |
| **finished_at<br>**    | Data de finalização da duplicata.                   |
| **update_reason_kind** | Motivo de cancelamento da duplicata                 |

## Filtros
Coluna State: somente os tipos finished ou canceled.

## Transformações
- Criar uma coluna de conversão baseado na coluna **kind**: Se finalizada 1, senão 0.
- Criar uma coluna analisar se houve negociação de data: Se **due_date** <= **new_due_date** recebe 1, senão 0.
- Criar um coluna para classificar se a duplicata foi finalizada dentro da data de vencimento. Se a **finished_at** <= **new_due_date** recebe 1, senão 0.
- Definir critério de pesos para tipos de cancelamento: Qual a pior razão de cancelamento de um endossante?


# 2 PROPOSTA DE TREINAMENTO

## Transformações
*Participants*
- Pegar os nomes do endossantes e extrair a palavra que mais repete e transformar em uma coluna de segmento: 
	**Exemplo**:
	Caso o nome do endossante possua COMERCIO, INDUSTRIA, DISTRIBUIDORA, etc.
*Asset Trade Bills*
- Puxar o tipo de segmento do endossante pelo **endosser_id** e adicionar na base do modelo, para gerar um score baseado no tipo de segmento, para propor para os investidores, qual o melhor segmento para se fazer um adiantamento.
- Separar a coluna **payment_place** em duas: cidade e estado. 
	**OBS**: Manter os textos da coluna em caixa alta.


# PROPOSTA DE TREINAMENTO
Verificar a utilidade da coluna **ballast_kind**, o que significa e se influencia na finalização de duplicata.


# PROPOSTA DE BI
- Qual segmento (produto ou serviço) mais possui duplicatas finalizadas;
- Qual ramo de atividade (comercio, indústria, distribuidora) possui mais duplicatas finalizadas.
- Qual localização há a maior porcentagem de duplicatas finalizadas?
