# -----------------------------
# Librerías
# -----------------------------
import pandas as pd
import joblib
from pathlib import Path

# -----------------------------
# Rutas
# -----------------------------
RUTA_MODELOS = Path("Models/")
RUTA_METADATOS = Path("data/metadata/descargas_etapa1/metadatos_grafos_masivos.csv")
RUTA_SALIDA_DIR = Path("data/metadata/descargas_etapa3/")
RUTA_SALIDA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Features esperadas
# -----------------------------
features = [
    "Nodes", "Edges", "Maximum degree", 
    "Average degree", "Assortativity", "Number of triangles",
    "Average number of triangles", "Maximum number of triangles",
    "Average clustering coefficient", "Fraction of closed triangles",
    "Maximum k-core", "Lower bound of Maximum Clique"
]

# -----------------------------
# Cargar metadatos
# -----------------------------
df = pd.read_csv(RUTA_METADATOS)
X = df[features]

# -----------------------------
# Recorrer modelos y predecir
# -----------------------------
for modelo_path in RUTA_MODELOS.glob("modelo*.pkl"):
    nombre_modelo = modelo_path.stem.replace("modelo_", "")
    print(f"Usando modelo: {nombre_modelo}")

    try:
        modelo = joblib.load(modelo_path)
        df_resultado = df.copy()
        df_resultado["ASPL_predicho"] = modelo.predict(X)

        salida_csv = RUTA_SALIDA_DIR / f"predicciones_{nombre_modelo}.csv"
        df_resultado.to_csv(salida_csv, index=False)
        print(f"Guardado: {salida_csv}")

    except Exception as e:
        print(f"Error con {nombre_modelo}: {e}")
