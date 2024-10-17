import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
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

# Extract data from csv file
base = pd.read_excel('C:\\Users\\Noite\\Documents\\old_table.xlsx', sheet_name = 'Planilha1')
# Separate base for transform
test_base = base
# Calculate aging
test_base['a'] = (test_base.iloc[:,8] - test_base.iloc[:,9]).dt.days
# Separate useful columns
test_base = test_base[[test_base.iloc[:,18].name, test_base.iloc[:,4].name, test_base.iloc[:,5].name, test_base.iloc[:,19].name, test_base.iloc[:,16].name]]
# Fill empty data
test_base.iloc[:,4] =  test_base.iloc[:,4].fillna('not canceled')
# Transform values to columns
test_base = pd.get_dummies(test_base, columns = [test_base.iloc[:,1].name],dtype=int)
# One Hot Encoding
categorical_attributes = [test_base.iloc[:,1].name]
categorical_columns = test_base[categorical_attributes]
encoder = OneHotEncoder(handle_unknown='ignore')
encoder.fit(categorical_columns)
encoded = encoder.transform(categorical_columns).toarray()
enc_train = pd.DataFrame(data = encoded, columns = encoder.categories_)
test_base = pd.concat([test_base,enc_train],axis=1)
test_base.drop(categorical_attributes, axis=1, inplace=True)
# One Hot Encoding
categorical_attributes = [test_base.iloc[:,2].name]
categorical_columns = test_base[categorical_attributes]
encoder = OneHotEncoder(handle_unknown='ignore')
encoder.fit(categorical_columns)
encoded = encoder.transform(categorical_columns).toarray()
enc_train = pd.DataFrame(data = encoded, columns = encoder.categories_)
test_base = pd.concat([test_base,enc_train],axis=1)
test_base.drop(categorical_attributes, axis=1, inplace=True)
# Rename columns
test_base = test_base.rename(columns={ test_base.iloc[:,4].name: str(test_base.iloc[:,4].name)[2:-3], test_base.iloc[:,5].name: str(test_base.iloc[:,5].name)[2:-3],test_base.iloc[:,6].name: str(test_base.iloc[:,6].name)[2:-3], test_base.iloc[:,7].name: str(test_base.iloc[:,7].name)[2:-3], test_base.iloc[:,8].name: str(test_base.iloc[:,8].name)[2:-3], test_base.iloc[:,9].name: str(test_base.iloc[:,9].name)[2:-3], test_base.iloc[:,10].name: str(test_base.iloc[:,10].name)[2:-3]})
# Create calculated columns
function_dictionary = {test_base.iloc[:,1].name:'mean',test_base.iloc[:,2].name:'sum',test_base.iloc[:,3].name:'sum', test_base.iloc[:,4].name:'sum', test_base.iloc[:,5].name:'sum', test_base.iloc[:,6].name: 'sum', test_base.iloc[:,7].name: 'sum', test_base.iloc[:,8].name: 'sum',	test_base.iloc[:,9].name: 'sum',	test_base.iloc[:,10].name: 'sum'}
test_base = test_base.groupby(test_base.iloc[:,0].name).aggregate(function_dictionary).reset_index(0)
# Calculate 
base_nfe = base
base_nfe = base_nfe.groupby([base_nfe.iloc[:,18].name, base_nfe.iloc[:,2].name]).agg({base_nfe.iloc[:,0].name: pd.Series.nunique}).reset_index(0)
base_nfe = base_nfe.reset_index(0)

base_nfe = base_nfe.groupby(base_nfe.iloc[:,1].name).agg({base_nfe.iloc[:,2].name: 'median'}).reset_index(0)

test_base = test_base.set_index(base_nfe.iloc[:,0].name).join(base_nfe.set_index(base_nfe.iloc[:,0].name)).reset_index(0)
test_base = test_base.rename(columns={test_base.iloc[:,11].name: "installment median"})
test_base.fillna(test_base[test_base.iloc[:,11].name].median(), inplace=True)
test_base['t'] = test_base.iloc[:,4] + test_base.iloc[:,5] + test_base.iloc[:,6]
test_base.iloc[:,4].sort_values(ascending=False)
test_base['pnc'] = test_base.iloc[:,7] / test_base.iloc[:,12]
### Create score
test_base['score_f'] = np.where(
    test_base.iloc[:,6] <= 5,(1000*test_base.iloc[:,6])/5,
    np.where(
        (test_base.iloc[:,6] > 5) & (test_base.iloc[:,6] <= 18),(3000*test_base.iloc[:,6])/18,
    np.where(
        (test_base.iloc[:,6] > 18) & (test_base.iloc[:,6] <= 30), (4999*test_base.iloc[:,6])/30,
        5000
    )
        )
    )
test_base['score_a'] = np.where(
    test_base.iloc[:,4] <= 40,(600*test_base.iloc[:,4])/40,
    np.where(
        (test_base.iloc[:,4] > 40) & (test_base.iloc[:,4] <= 199),(1800*test_base.iloc[:,4])/199,
    np.where(
        (test_base.iloc[:,4] > 199) & (test_base.iloc[:,4] <= 484), (2999*test_base.iloc[:,4])/484,
        3000
    )
        )
    )
test_base['score_t'] = np.where(
    test_base.iloc[:,12] <= 40,(400*test_base.iloc[:,12])/40,
    np.where(
        (test_base.iloc[:,12] > 40) & (test_base.iloc[:,12] <= 100),(1200*test_base.iloc[:,12])/100,
    np.where(
        (test_base.iloc[:,12] > 100) & (test_base.iloc[:,12] <= 200), (1999*test_base.iloc[:,12])/200,
        2000
    )
        )
    )
test_base['score_c'] = np.where(
    test_base.iloc[:,5] <= 13,(200*test_base.iloc[:,5])/13,
    np.where(
        (test_base.iloc[:,5] > 13) & (test_base.iloc[:,5] <= 35),(600*test_base.iloc[:,5])/35,
    np.where(
        (test_base.iloc[:,5] > 35) & (test_base.iloc[:,5] <= 65), (999*test_base.iloc[:,5])/65,
        1000
    )
        )
    )
test_base['s'] = test_base.iloc[:,14] + test_base.iloc[:,15] + test_base.iloc[:,16] - test_base.iloc[:,17]
# Limite the data for the model
test_base = test_base[(test_base['t'] < 1000) & (test_base['s']< 4000)]
# Separate columns for the model
base_model = test_base[[test_base.iloc[:,1].name,	test_base.iloc[:,2].name,	test_base.iloc[:,3].name,test_base.iloc[:,4].name,	test_base.iloc[:,5].name,	test_base.iloc[:,6].name,	test_base.iloc[:,7].name,	test_base.iloc[:,11].name,	test_base.iloc[:,12].name,test_base.iloc[:,18].name]]
base_model = base_model[test_base.iloc[:,8] <= 1000]
# Separate target
X = base_model.loc[ : , base_model.columns != base_model.iloc[:,9].name]
y = base_model.iloc[:,9]
# Separate data for training and testing
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)
# Normalize the data
# Normalization
sc = MinMaxScaler()
X_train = sc.fit_transform(X_train)
X_test = sc.transform(X_test)
# Training model
model = LinearRegression()
model = model.fit(X_train, y_train)
# IA metrics
# Accuracy
r2_score(y_test, model.fit(X_train, y_train).predict(X_test))
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# Predictions
y_pred = model.predict(X_test)
# Calculating
mae = mean_absolute_error(y_test, y_pred)
mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_test, y_pred)

# Try to predict score
v1 = 0
v2 = 520
v3 = 19
v4 = 471
v5 = 0
v6 = 68
v7 = 539
v8 = 0
v9 = 539

new_test = [v1,v2,v3,v4,v5,v6,v7,v8,v9]


X = np.array(new_test).reshape(1,-1)

X = sc.transform(X)
import joblib
joblib.dump(model, 'model_score.pkl')
