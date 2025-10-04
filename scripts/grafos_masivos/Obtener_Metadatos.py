# -----------------------------
# Librerías
# -----------------------------
import os
import pandas as pd

# -----------------------------
# Función auxiliar
# -----------------------------
def extraer_metadatos(ruta_grafos):
    metadatos = []

    for carpeta in os.listdir(ruta_grafos):
        ruta_completa = os.path.join(ruta_grafos, carpeta)
        if os.path.isdir(ruta_completa) and carpeta.endswith("_descomprimido"):
            archivos = os.listdir(ruta_completa)
            tamaño_total = sum(os.path.getsize(os.path.join(ruta_completa, f)) for f in archivos)
            num_archivos = len(archivos)

            metadatos.append({
                "grafo": carpeta.replace("_descomprimido", ""),
                "num_archivos": num_archivos,
                "tamaño_bytes": tamaño_total,
                "archivos": ", ".join(archivos)
            })

    return pd.DataFrame(metadatos)

# -----------------------------
# Ejecución principal
# -----------------------------
if __name__ == "__main__":
    ruta_grafos = "data/grafos_masivos"
    df_metadatos = extraer_metadatos(ruta_grafos)

    ruta_salida = os.path.join(ruta_grafos, "metadatos", "resumen_metadatos.csv")
    os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
    df_metadatos.to_csv(ruta_salida, index=False)

    print(f"Metadatos guardados en: {ruta_salida}")
    print(df_metadatos)

