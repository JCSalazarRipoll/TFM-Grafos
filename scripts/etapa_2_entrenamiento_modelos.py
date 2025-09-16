# etapa_2_entrenamiento_modelos.py

import pandas as pd
import numpy as np
import time
from pathlib import Path
from sklearn.model_selection import KFold, train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from tpot import TPOTRegressor
import joblib

# -----------------------------
# Configuración
# -----------------------------
RUTA_METADATA = Path("data/metadata/metadata_grafos.csv")
RUTA_MODELOS = Path("data/modelos_entrenados/")
RUTA_MODELOS.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Carga y selección de columnas
# -----------------------------
df = pd.read_csv(RUTA_METADATA)

columnas_viables = [
    'nodos', 'aristas', 'grado_maximo', 'grado_promedio', 'asortatividad',
    'numero_triangulos', 'triangulos_promedio', 'triangulos_maximo',
    'coeficiente_aglomeracion_promedio', 'proporcion_triangulos_promedio',
    'centro_k_maximo', 'estimacion_minima_clique_maxima'
]

X = df[columnas_viables]
y = df["distancia_promedio"]

# -----------------------------
# Validación cruzada
# -----------------------------
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# -----------------------------
# Modelos clásicos
# -----------------------------
modelos = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(random_state=42),
    "ExtraTrees": ExtraTreesRegressor(random_state=42),
    "SVR": SVR(),
    "KNN": KNeighborsRegressor(),
    "XGBoost": XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42)
}

resultados = []

for nombre, modelo in modelos.items():
    mae_list, rmse_list, r2_list = [], [], []
    inicio = time.time()

    for train_idx, test_idx in kf.split(X):
        X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
        y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

        modelo.fit(X_train, y_train)
        y_pred = modelo.predict(X_test)

        mae_list.append(mean_absolute_error(y_test, y_pred))
        rmse_list.append(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2_list.append(r2_score(y_test, y_pred))

    duracion = time.time() - inicio
    joblib.dump(modelo, RUTA_MODELOS / f"{nombre}.joblib")

    resultados.append({
        "modelo": nombre,
        "MAE": np.mean(mae_list),
        "RMSE": np.mean(rmse_list),
        "R2": np.mean(r2_list),
        "duracion_segundos": round(duracion, 2)
    })

# -----------------------------
# TPOT por separado
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
inicio = time.time()
tpot = TPOTRegressor(generations=5, population_size=20, random_state=42)
tpot.fit(X_train, y_train)
duracion = time.time() - inicio

best_model = tpot.fitted_pipeline_
y_pred = best_model.predict(X_test)

joblib.dump(best_model, RUTA_MODELOS / "TPOT.joblib")

resultados.append({
    "modelo": "TPOT",
    "MAE": mean_absolute_error(y_test, y_pred),
    "RMSE": np.sqrt(mean_squared_error(y_test, y_pred)),
    "R2": r2_score(y_test, y_pred),
    "duracion_segundos": round(duracion, 2)
})

# -----------------------------
# Guardar resultados
# -----------------------------
df_resultados = pd.DataFrame(resultados)
df_resultados.sort_values(by="R2", ascending=False, inplace=True)
print("\n Resultados de evaluación:")
print(df_resultados.round(4))

df_resultados.to_csv(RUTA_MODELOS / "resultados_modelos.csv", index=False)

