#etapa_3_entrenamiento_modelos
# -----------------------------
# Librerías
# -----------------------------
import os
import glob
import time
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import KFold, train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from xgboost import XGBRegressor

# -----------------------------
# Paso 1: Cargar y limpiar datos
# -----------------------------
csv_files = glob.glob("data/metadata/descargas_etapa2/*.csv")
df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

columnas_clave = [
    'ASPL',
    'Nodes',
    'Edges',
    'Maximum degree',
    'Average degree',
    'Assortativity',
    'Number of triangles',
    'Average number of triangles',
    'Maximum number of triangles',
    'Average clustering coefficient',
    'Fraction of closed triangles',
    'Maximum k-core',
    'Lower bound of Maximum Clique'
]

print(f"Grafos antes de limpieza: {len(df)}")
df = df.dropna(subset=columnas_clave)
print(f"Grafos después de limpieza: {len(df)}")

X = df[[col for col in columnas_clave if col != "ASPL"]]
y = df["ASPL"]

# -----------------------------
# Paso 2: Definir modelos
# -----------------------------
kf = KFold(n_splits=5, shuffle=True, random_state=42)

models = {
    "Linear Regression": LinearRegression(),
    "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
    "XGBoost": XGBRegressor(objective='reg:squarederror', n_estimators=100, random_state=42),
    "Gradient Boosting": GradientBoostingRegressor(random_state=42),
    "Extra Trees": ExtraTreesRegressor(random_state=42),
    "SVR": SVR(),
    "KNN": KNeighborsRegressor()
}

# -----------------------------
# Paso 3: Entrenamiento clásico
# -----------------------------
os.makedirs("Models", exist_ok=True)
resultados = []

for model_name, model in models.items():
    mae_list, rmse_list, r2_list = [], [], []

    start_time = time.time()

    for train_index, test_index in kf.split(X):
        X_train, X_test = X.iloc[train_index], X.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]

        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae_list.append(mean_absolute_error(y_test, y_pred))
        rmse_list.append(np.sqrt(mean_squared_error(y_test, y_pred)))
        r2_list.append(r2_score(y_test, y_pred))

    end_time = time.time()
    tiempo_segundos = round(end_time - start_time, 2)

    joblib.dump(model, f"Models/modelo_{model_name.replace(' ', '_')}.pkl")

    resultados.append({
        "Modelo": model_name,
        "MAE": np.mean(mae_list),
        "RMSE": np.mean(rmse_list),
        "R²": np.mean(r2_list),
        "MAE_std": np.std(mae_list),
        "RMSE_std": np.std(rmse_list),
        "R²_std": np.std(r2_list),
        "Tiempo (s)": tiempo_segundos
    })

# -----------------------------
# Paso 5: Guardar resultados
# -----------------------------
# Gráfica 1: Métricas principales (MAE, RMSE, R²)
df_resultados.plot(x="Modelo", y=["MAE", "RMSE", "R²"], kind="bar", figsize=(10,6))
plt.title("Comparación de modelos de regresión")
plt.ylabel("Valor promedio")
plt.tight_layout()
plt.savefig("Models/comparacion_modelos.png")
plt.close()

# Gráfica 2: Tiempo de entrenamiento
df_resultados.plot(x="Modelo", y="Tiempo (s)", kind="bar", color="gray", figsize=(8,5))
plt.title("Tiempo de entrenamiento por modelo")
plt.ylabel("Segundos")
plt.tight_layout()
plt.savefig("Models/tiempo_entrenamiento.png")
plt.close()

# Gráfica 3: Desviación estándar de MAE
df_resultados.plot(x="Modelo", y="MAE_std", kind="bar", color="skyblue", figsize=(8,5))
plt.title("Variabilidad del MAE por modelo")
plt.ylabel("Desviación estándar")
plt.tight_layout()
plt.savefig("Models/variabilidad_mae.png")
plt.close()

# Gráfica 4: Desviación estándar de RMSE
df_resultados.plot(x="Modelo", y="RMSE_std", kind="bar", color="salmon", figsize=(8,5))
plt.title("Variabilidad del RMSE por modelo")
plt.ylabel("Desviación estándar")
plt.tight_layout()
plt.savefig("Models/variabilidad_rmse.png")
plt.close()

# Gráfica 5: Desviación estándar de R²
df_resultados.plot(x="Modelo", y="R²_std", kind="bar", color="limegreen", figsize=(8,5))
plt.title("Variabilidad del R² por modelo")
plt.ylabel("Desviación estándar")
plt.tight_layout()
plt.savefig("Models/variabilidad_r2.png")
plt.close()

