# etapa_2_entrenamiento_modelos.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from xgboost import XGBRegressor
from tpot import TPOTRegressor
import joblib
from pathlib import Path
from tqdm import tqdm

# -----------------------------
# Configuración
# -----------------------------
RUTA_METADATA = Path("data/metadata/metadata_grafos.csv")
RUTA_MODELOS = Path("data/modelos_entrenados/")
RUTA_MODELOS.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Carga y preprocesamiento
# -----------------------------
df = pd.read_csv(RUTA_METADATA)

# Filtrado de columnas numéricas
X = df.drop(columns=["nombre", "distancia_promedio","duracion_calculo"])
y = df["distancia_promedio"]

# -----------------------------
# División de datos
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# -----------------------------
# Modelos a entrenar
# -----------------------------
modelos = {
    "LinearRegression": LinearRegression(),
    "RandomForest": RandomForestRegressor(n_estimators=100, random_state=42),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=100, random_state=42),
    "SVR": SVR(),
    "KNN": KNeighborsRegressor(),
    "XGBoost": XGBRegressor(n_estimators=100, random_state=42),
    "TPOT": TPOTRegressor(generations=5, population_size=20, verbosity=2, random_state=42)
}

# -----------------------------
# Entrenamiento y evaluación
# -----------------------------
resultados = []

for nombre, modelo in tqdm(modelos.items(), desc="Entrenando modelos"):
    modelo.fit(X_train, y_train)
    y_pred = modelo.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    resultados.append({
        "modelo": nombre,
        "MAE": mae,
        "MSE": mse,
        "R2": r2
    })

    # Guardar modelo entrenado
    joblib.dump(modelo, RUTA_MODELOS / f"{nombre}.joblib")

# -----------------------------
# Resultados
# -----------------------------
df_resultados = pd.DataFrame(resultados)
print("\n Resultados de evaluación:")
print(df_resultados.sort_values(by="R2", ascending=False).round(4))
