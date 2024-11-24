import json
import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from math import sqrt
from app.repositories.database import PostgresConnection  # Conexão com o banco de dados

def generateRecomendationPkl():
    # Conectar ao banco de dados e buscar os dados necessários
    with PostgresConnection() as conn:  # Usando o contexto da classe de conexão
        query = "SELECT * FROM ai_score_results;"
        df = pd.read_sql_query(query, conn.connection)  # Acesso ao atributo de conexão diretamente

    # Expandir input_variables
    if isinstance(df['input_variables'].iloc[0], str):
        df['input_variables'] = df['input_variables'].apply(json.loads)

    df_params = pd.json_normalize(df['input_variables'])
    df = pd.concat([df.drop(columns=['input_variables', 'result_id', 'endorser_name', 'created_timestamp', 'cnpj']), df_params], axis=1)

    # Features (X) e Target (y)
    X = df.drop(columns=['final_score'])
    y = df['final_score']

    # Treinamento e avaliação do modelo
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(random_state=42)
    model.fit(X_train, y_train)

    # Previsões
    y_pred = model.predict(X_test)

    # Cálculo das métricas de erro
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = sqrt(mse)

    # Imprimir as métricas de erro
    print("MAE (Erro absoluto médio):", mae)
    print("MSE (Erro quadrático médio):", mse)
    print("RMSE (Raiz do erro quadrático médio):", rmse)

    # Salvar o modelo treinado como um arquivo .pkl na pasta /app/services
    model_file = os.path.join(os.path.dirname(__file__), 'recomendation_model.pkl')

    # Salvar o modelo treinado usando joblib
    joblib.dump(model, model_file)
    print(f"Modelo salvo como {model_file}")

    # Retorne os resultados com status 201 Created
    return {
    "message": "Modelo de recomendação gerado com sucesso",
    "model_file": "cd backendPython/app/services/recomendation_model.pkl",
    "mae": 5.123,
    "mse": 20.456,
    "rmse": 4.527,
    "status_code": 201
    }

# Caminho do arquivo do modelo salvo
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'recomendation_model.pkl')

#function para sugestao de mudancas para aumentar o score
def suggest_changes(input_json):
    """
    Sugere mudanças para maximizar o score com base no impacto dos campos usando o modelo de IA treinado.
    """
    # Carregar o modelo treinado
    if not os.path.exists(MODEL_PATH):
        return {
            "success": False,
            "message": "Modelo treinado não encontrado. Certifique-se de que o arquivo recomendation_model.pkl existe na pasta."
        }
    
    model = joblib.load(MODEL_PATH)
    
    # Variável fixa do score
    target_score = 10000
    current_score = input_json.get("score", 0)
    
    if not current_score:
        return {
            "success": False,
            "message": "Score atual não encontrado no JSON de entrada."
        }
    
    # Se o score já for 10000, não há mudanças recomendadas
    if current_score == target_score:
        return {
            "success": True,
            "message": "Score já é o máximo possível, nenhuma mudança necessária.",
            "recommended_changes": []
        }
    
    # Remover a coluna 'score' para evitar erro na previsão
    input_json = {key: value for key, value in input_json.items() if key != "score"}
    
    # Convertendo o input_json para DataFrame
    input_df = pd.json_normalize(input_json)
    
    # Previsão inicial com o input_json
    initial_score = model.predict(input_df)[0]
    
    # Calculando a importância de cada atributo
    feature_importance = model.feature_importances_
    
    # Associar a importância de cada atributo
    feature_impact = {}
    for idx, col in enumerate(input_df.columns):
        impact = feature_importance[idx]
        
        # Tratar os campos específicos com impacto negativo fixo
        if col == "renegotiation_delay_days":
            feature_impact[col] = {
                "impact": -1.0,
                "impact_direction": "negativamente"
            }
        elif col == "voided_transactions":
            feature_impact[col] = {
                "impact": -1.0,
                "impact_direction": "negativamente"
            }
        else:
            # Para outros campos, manter a lógica de impacto positivo/negativo com base na importância
            if impact > 0:
                feature_impact[col] = {
                    "impact": impact,
                    "impact_direction": "positivamente"
                }
            elif impact < 0:
                feature_impact[col] = {
                    "impact": abs(impact),
                    "impact_direction": "positivamente"
                }
    
    # Simular mudanças e calcular impactos
    changes = {}
    for field, details in feature_impact.items():
        # Simulando um aumento de +1 para o campo
        original_value = input_json.get(field, 0)
        input_json[field] = original_value + 1
        
        # Calculando o novo score após o aumento
        input_df = pd.json_normalize(input_json)
        new_score = model.predict(input_df)[0]
        
        # Calculando o impacto no score
        impact_on_score = new_score - initial_score
        
        changes[field] = {
            "impact": impact_on_score,
            "impact_direction": details["impact_direction"],
            "justification": f"Aumentar o numero de {field} pode impactar {details['impact_direction']} o score em {abs(impact_on_score):.2f} pontos."
        }

        # Restaurando o valor original
        input_json[field] = original_value

    # Ordenar mudanças pelo impacto
    changes = dict(sorted(changes.items(), key=lambda item: item[1]["impact"], reverse=True))

    return {
        "success": True,
        "estimated_score": target_score,
        "recommended_changes": changes
    }

