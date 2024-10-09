# -*- coding: utf-8 -*-
"""AI_MODEL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XMAT60MJItnQ34SGyEmnsWe9QVVZPjZ4

# Prepare the base

#### Import data and python libraries
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder

# IMPORTANT: NEED TO CHANGE THE PATH OF THE FILE
base = pd.read_excel('/content/sample_data/dados_asset_bills.xlsx', sheet_name = 'Planilha1')

"""#### Transform data"""

base_test = base

# Calculate the aging of due_date
base_test['aging_due_date'] = (base_test['new_due_date'] -  base_test['due_date']).dt.days
# Select useful columns
base_test = base_test[['NOME_ENDOSSER', 'kind', 'state', 'aging_due_date', 'update_reason_kind']]
# Filling the NaN values from column state for finished duplicates
base_test['update_reason_kind'] =  base_test['update_reason_kind'].fillna('not canceled')
# One hot encoding for kind
base_test = pd.get_dummies(base_test, columns = ['kind'],dtype=int)

# One hot encoding to state
# Separate the column for one hot
categorical_attributes = ['state']
categorical_columns = base_test[categorical_attributes]
# instance and train OneHotEncoder
encoder = OneHotEncoder(handle_unknown='ignore')
encoder.fit(categorical_columns)
# Codify the categorical columns and transform in a dataframe
encoded = encoder.transform(categorical_columns).toarray()
enc_train = pd.DataFrame(data = encoded, columns = encoder.categories_)
# Concat with the original dataframe and drop original column
base_test = pd.concat([base_test,enc_train],axis=1)
base_test.drop(categorical_attributes, axis=1, inplace=True)

# One hot encoding for update_reason_kind
# Separate the column for one hot
categorical_attributes = ['update_reason_kind']
categorical_columns = base_test[categorical_attributes]
# instance and train OneHotEncoder
encoder = OneHotEncoder(handle_unknown='ignore')
encoder.fit(categorical_columns)
# Codify the categorical columns and transform in a dataframe
encoded = encoder.transform(categorical_columns).toarray()
enc_train = pd.DataFrame(data = encoded, columns = encoder.categories_)
# Concat with the original dataframe and drop original column
base_test = pd.concat([base_test,enc_train],axis=1)
base_test.drop(categorical_attributes, axis=1, inplace=True)

# Rename columns
base_test.columns

base_test = base_test.rename(columns={ ('active',): "active", ('canceled',): "canceled", ('finished',): 'finished', ('not canceled',): 'not_canceled', ('operational_error',): 'operational_error', ('others',): 'others', ('reversal',): 'reversal'})

base_test.isna().sum()

base_test.head()

function_dictionary = {'aging_due_date':'mean','kind_goods':'sum','kind_services':'sum', 'active':'sum', 'canceled':'sum', 'finished': 'sum', 'not_canceled': 'sum', 'operational_error': 'sum',	'others': 'sum',	'reversal': 'sum'}
base_crazy = base_test
base_test = base_test.groupby("NOME_ENDOSSER").aggregate(function_dictionary).reset_index(0)

base_nfe = base

# base_nfe.groupby("NOME_ENDOSSER").agg({"nfe_number": pd.Series.nunique})
# base_nfe.groupby(['NOME_ENDOSSER', 'nfe_number']).agg({'nfe_number': 'count'})
base_nfe = base_nfe.groupby(["NOME_ENDOSSER", "nfe_number"]).agg({"id": pd.Series.nunique}).reset_index(0)

base_nfe = base_nfe.reset_index(0)

base_nfe = base_nfe.groupby("NOME_ENDOSSER").agg({"id": 'median'}).reset_index(0)

base_test = base_test.set_index('NOME_ENDOSSER').join(base_nfe.set_index('NOME_ENDOSSER')).reset_index(0)

base_test = base_test.rename(columns={ 'id': "installment median"})

base_test.fillna(base_test['installment median'].median(), inplace=True)

base_test[base_test['active'] != 0].sort_values(by=['active'], ascending=True).head(10)

base_test['total'] = base_test['active'] + base_test['canceled'] + base_test['finished']

base_test.sort_values(by=['active'], ascending = False).head(10)

base_test

# create percentage of not canceled
base_test['percent_not_canceled'] = base_test['not_canceled'] / base_test['total']

"""#### Create scoring"""

base_test['score_finished'] = np.where(
    base_test["finished"] <= 5,(1000*base_test["finished"])/5,
    np.where(
        (base_test["finished"] > 5) & (base_test["finished"] <= 18),(3000*base_test["finished"])/18,
    np.where(
        (base_test["finished"] > 18) & (base_test["finished"] <= 30), (4999*base_test["finished"])/30,
        5000
    )
        )
    )

base_test['score_active'] = np.where(
    base_test["active"] <= 40,(600*base_test["active"])/40,
    np.where(
        (base_test["active"] > 40) & (base_test["active"] <= 199),(1800*base_test["active"])/199,
    np.where(
        (base_test["active"] > 199) & (base_test["active"] <= 484), (2999*base_test["active"])/484,
        3000
    )
        )
    )

base_test['score_total'] = np.where(
    base_test["total"] <= 40,(400*base_test["total"])/40,
    np.where(
        (base_test["total"] > 40) & (base_test["total"] <= 100),(1200*base_test["total"])/100,
    np.where(
        (base_test["total"] > 100) & (base_test["total"] <= 200), (1999*base_test["total"])/200,
        2000
    )
        )
    )

base_test['score_canceled'] = np.where(
    base_test["canceled"] <= 13,(200*base_test["canceled"])/13,
    np.where(
        (base_test["canceled"] > 13) & (base_test["canceled"] <= 35),(600*base_test["canceled"])/35,
    np.where(
        (base_test["canceled"] > 35) & (base_test["canceled"] <= 65), (999*base_test["canceled"])/65,
        1000
    )
        )
    )

base_test['score'] = base_test['score_finished'] + base_test['score_active'] + base_test['score_total'] - base_test['score_canceled']

base_test.sort_values(by=['total'], ascending=False).head(10)

"""# IA - MODEL Nº2

"""

from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split, cross_val_score # Utilizado para separar dados de treino e teste
from sklearn.preprocessing import StandardScaler # Utilizado para fazer a normalização dos dados
from sklearn.preprocessing import MinMaxScaler # Utilizado para fazer a normalização dos dados
from sklearn.preprocessing import LabelEncoder # Utilizado para fazer o OneHotEncoding
from sklearn.linear_model import LinearRegression # Algoritmo de Regressão Linear
from sklearn.metrics import r2_score, accuracy_score,confusion_matrix, ConfusionMatrixDisplay # Métricas de avaliação do models
from sklearn.tree import DecisionTreeClassifier
import graphviz
from sklearn import tree

base_test.describe()

# Separate data for use
base_model = base_test[['aging_due_date',	'kind_goods',	'kind_services',	'active',	'canceled',	'finished',	'not_canceled',	'installment median',	'total','score']]
base_model = base_model[base_model['total'] <= 1000]

base_model.describe()

X = base_model.loc[ : , base_model.columns != 'score']
y = base_model['score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

# Normalization
sc = MinMaxScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)

# Treina o modelo
model = LinearRegression()
model = model.fit(X_train, y_train)

# Accuracy
r2_score(y_test, model.fit(X_train, y_train).predict(X_test))

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# Previsões
y_pred = model.predict(X_test)

# Cálculo das métricas
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

# Exibição dos resultados
print(f'MAE: {mae}')
print(f'MSE: {mse}')
print(f'RMSE: {rmse}')
print(f'R²: {r2}')

base_model.sort_values(by=['score'], ascending=False).head(10)

# Try to predict score
aging_due_date = 0
kind_goods = 539
kind_services	= 0
active = 471
canceled = 0
finished	=68
not_canceled	= 539
installment_median	= 0
total	= 539

new_test = [aging_due_date,	kind_goods,	kind_services,	active,	canceled,	finished,	not_canceled,installment_median,	total	]

X = np.array(new_test).reshape(1,-1)
X = sc.transform(X)
print("Score do endossante:", model.predict(X))

pesos = model.coef_
intercepto = model.intercept_
print('aging_due_date	kind_goods	kind_services	active		not_canceled	total')
print( pesos)
print("Intercepto:", intercepto)