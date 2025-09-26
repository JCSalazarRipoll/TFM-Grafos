#Aplicando el teorema del límite central con el teorema de la convergencia monótona
import os
import glob
import random
import csv
import numpy as np
import networkx as nx
from scipy.io import mmread
from datetime import datetime

# Configuración de rutas
carpeta_raiz = "/content/TFM-Grafos/data/grafos_masivos"
carpeta_resultados = "/content/TFM-Grafos/resultados_etapa_4"
os.makedirs(carpeta_resultados, exist_ok=True)

# Detectar qué grafos procesar
def detectar_grafos_pendientes():
    archivos_csv = glob.glob(os.path.join(carpeta_resultados, "resultados_*.csv"))
    if not archivos_csv:
        return ['soc-flickr', 'soc-livejournal']  # fase 1
    else:
        nombres = [os.path.basename(a).split('_')[1].split('.')[0] for a in archivos_csv]
        if 'soc-pokec' not in nombres:
            return ['soc-pokec']  # fase 2
        else:
            return []  # todo completado

# Cargar grafos desde .mtx
def cargar_grafos(grafos_a_cargar):
    grafos_masivos = {}
    archivos_mtx = glob.glob(os.path.join(carpeta_raiz, "**/*.mtx"), recursive=True)
    print(f" Archivos encontrados: {len(archivos_mtx)}")

    for archivo in archivos_mtx:
        nombre = os.path.basename(archivo).split('.')[0]
        if nombre not in grafos_a_cargar:
            continue
        try:
            matriz = mmread(archivo).tocoo()
            G = nx.Graph()
            G.add_edges_from(zip(matriz.row, matriz.col))
            if not nx.is_connected(G):
                G = G.subgraph(max(nx.connected_components(G), key=len)).copy()
            grafos_masivos[nombre] = G
            print(f"  '{nombre}': {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas.")
        except Exception as e:
            print(f"  Error al cargar '{nombre}': {e}")
    return grafos_masivos

# Muestreo por TLC
def muestrear_por_TLC(nombre_grafo, G, tamaños=[500, 1000, 2000], repeticiones=30):
    for tamaño in tamaños:
        print(f"\n Procesando tamaño {tamaño} para '{nombre_grafo}'...")
        aspls = []

        for rep in range(repeticiones):
            nodos_muestra = random.sample(G.nodes(), tamaño)
            subgrafo = G.subgraph(nodos_muestra)

            if nx.is_connected(subgrafo):
                aspl = nx.average_shortest_path_length(subgrafo)
                aspls.append(aspl)
                guardar_resultado(nombre_grafo, tamaño, aspl, rep)
                print(f" Rep {rep+1}: ASPL = {aspl:.4f}")
            else:
                print(f" Rep {rep+1}: Subgrafo no conexo")

        if aspls:
            media = np.mean(aspls)
            std = np.std(aspls, ddof=1)
            error = std / np.sqrt(len(aspls))
            print(f" Tamaño {tamaño}: Media={media:.4f}, σ={std:.4f}, Error={error:.4f}")
        else:
            print(f" No se pudo calcular ASPL para tamaño {tamaño}")

# Guardar resultados en CSV
def guardar_resultado(nombre_grafo, tamaño, aspl, rep):
    archivo = os.path.join(carpeta_resultados, f"resultados_{nombre_grafo}.csv")
    timestamp = datetime.now().isoformat()
    with open(archivo, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([tamaño, aspl, rep, timestamp])

# Ejecución principal
if __name__ == "__main__":
    grafos_a_cargar = detectar_grafos_pendientes()
    if not grafos_a_cargar:
        print("🎉 Todos los grafos ya fueron procesados.")
    else:
        grafos = cargar_grafos(grafos_a_cargar)
        for nombre, G in grafos.items():
            muestrear_por_TLC(nombre, G)
