import pandas as pd
import logging
import os
from pathlib import Path
import requests

#Cargar funciones desde los diferentes directorios creados
from collectors.parser import url_dataframe
from collectors import guardar_resultados_en_duckdb, leer_config_desde_txt

carpeta = Path("graphs")
archivos_txt = sorted(carpeta.glob("*.txt"))  # Todos los .txt ordenados alfabéticamente

# Ruta del archivo donde se guardan los datos procesados
CSV_PATH = "datos_grafos.csv"

# Cargar grafos ya procesados (si existe)
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
    processed_urls = set(df["url"])
else:
    df = pd.DataFrame()
    processed_urls = set()

# Filtrar las urls que aún no han sido procesadas
remaining_collectors = []

for path_txt in archivos_txt:
    try:
        with open(path_txt, "r", encoding="utf-8") as f:
            head_url = None
            for linea in f:
                linea = linea.strip()
                if linea.startswith("head_url ="):
                    head_url = linea.split("=")[1].strip().strip("'")
                    break  # no necesitamos leer más
            if head_url and head_url not in processed_urls:
                remaining_collectors.append(path_txt)
    except Exception as e:
        print(f"Error leyendo {path_txt}: {e}")

# Tomar solo los primeros 2
to_process = remaining_collectors[:2]

try:
    logging.info("Inicio del proceso de recopilación y análisis de grafos.")
    
    #Esta función devuelve un dataframe con los datos obtenidos de los grafos

    for archivo in to_process:
        head_url, urls = leer_config_desde_txt(archivo)
        df_temp = url_dataframe(urls,head_url)
        df = pd.concat([df, df_temp], ignore_index=True)

    #En caso de que se hayan podido procesar los grafos correctamente
    if not df.empty:
        # Elimina duplicados por nombre, nodos y aristas
        df.drop_duplicates(subset=["nombre", "nodos", "aristas"], inplace=True)

        # Guarda como CSV
        df.to_csv("datos_grafos.csv", index=False)
        logging.info(f"{len(df)} grafos procesados correctamente. Archivo guardado como datos_grafos.csv")

        # Muestra el resumen básico
        logging.info("Resumen de grafos procesados:\n" + df[["nombre", "nodos", "aristas"]].to_string(index=False))

        # Guarda en DuckDB
        guardar_resultados_en_duckdb(df, db_path="resultados.duckdb", tabla="experimentos")
        logging.info("Resultados almacenados en la base de datos DuckDB: resultados.duckdb")
        
    else:
        logging.info("No se procesó ningún grafo válido.")
except Exception as e:
    logging.error("Ocurrió un error durante la ejecución", exc_info=True)
