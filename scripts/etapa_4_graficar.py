# etapa_4_graficar.py
# -----------------------------
# Imports
# -----------------------------
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -----------------------------
# Función principal
# -----------------------------
def graficar_predicciones_por_modelo():
    # Rutas
    RUTA_PREDICCIONES = Path("data/metadata/descargas_etapa3/")
    archivos = list(RUTA_PREDICCIONES.glob("predicciones_*.csv"))

    # Consolidar predicciones
    df_consolidado = pd.DataFrame()
    for archivo in archivos:
        modelo = archivo.stem.replace("predicciones_", "")
        df_temp = pd.read_csv(archivo)[["nombre", "ASPL_predicho"]].copy()
        df_temp["modelo"] = modelo
        df_consolidado = pd.concat([df_consolidado, df_temp], ignore_index=True)

    # Pivot para graficar
    df_pivot = df_consolidado.pivot(index="modelo", columns="nombre", values="ASPL_predicho")

    # Graficar
    df_pivot.plot(kind="bar", figsize=(12,6))
    plt.title("Predicción de ASPL por modelo y grafo")
    plt.ylabel("ASPL predicho")
    plt.xlabel("Modelo")
    plt.legend(title="Grafo", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.savefig("Models/predicciones_comparativas.png")
    plt.close()
    print("Gráfica guardada en 'Models/predicciones_comparativas.png'")

# -----------------------------
# Ejecución controlada
# -----------------------------
if __name__ == "__main__":
    graficar_predicciones_por_modelo()
