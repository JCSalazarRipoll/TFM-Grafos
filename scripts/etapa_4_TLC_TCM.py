#Aplicando el teorema del límite central con el teorema de la convergencia monótona
import os
import csv
import random
import networkx as nx
from datetime import datetime

# Estructura heredada de etapa 1
grafos_masivos = {
    "soc-flickr": "https://nrvis.com/download/data/soc/soc-flickr.zip",
    "soc-livejournal": "https://nrvis.com/download/data/soc/soc-livejournal.zip",
    "soc-pokec": "https://nrvis.com/download/data/soc/soc-pokec.zip"
}

# Rutas
carpeta_base = "/content/TFM-Grafos/data/grafos_masivos"
carpeta_resultados = "/content/TFM-Grafos/resultados_etapa_4"
os.makedirs(carpeta_resultados, exist_ok=True)

# Generar subgrafos conexos de tamaño exacto
def generar_subgrafos_conexos_exactos(path, tamaño_objetivo=500, cantidad=30):
    subgrafos = []
    with open(path, 'r') as f:
        lineas = [linea.strip() for linea in f if not linea.startswith('%') and linea.strip()]
    
    i = 0
    while len(subgrafos) < cantidad and i < len(lineas):
        nodos = set()
        aristas = []
        while i < len(lineas):
            partes = lineas[i].split()
            if len(partes) != 2:
                i += 1
                continue
            u, v = map(int, partes)
            if not nodos:
                nodos.update([u, v])
                aristas.append((u, v))
            elif u in nodos or v in nodos:
                nuevo = v if u in nodos else u
                nodos.add(nuevo)
                aristas.append((u, v))
            if len(nodos) >= tamaño_objetivo:
                break
            i += 1
        if len(nodos) == tamaño_objetivo:
            subgrafos.append((nodos.copy(), aristas.copy()))
        i += 1
    return subgrafos

# Calcular ASPL y registrar resultados
def evaluar_y_guardar(subgrafos, nombre_grafo, tamaño_objetivo):
    archivo = os.path.join(carpeta_resultados, f"resultados_{nombre_grafo}.csv")
    with open(archivo, 'a', newline='') as f:
        writer = csv.writer(f)
        for rep, (nodos, aristas) in enumerate(subgrafos):
            G = nx.Graph()
            G.add_edges_from(aristas)
            if nx.is_connected(G):
                aspl = nx.average_shortest_path_length(G)
                timestamp = datetime.now().isoformat()
                writer.writerow([tamaño_objetivo, aspl, rep, timestamp])
                print(f"  {nombre_grafo} | Tamaño {tamaño_objetivo} | Rep {rep+1}: ASPL = {aspl:.4f}")
            else:
                print(f"  {nombre_grafo} | Rep {rep+1}: Subgrafo no conexo (raro)")

# Ejecución principal
if __name__ == "__main__":
    tamaños = [500, 1000, 2000]
    muestras_por_tamaño = 30

    for nombre_grafo in grafos_masivos:
        ruta_mtx = os.path.join(carpeta_base, f"{nombre_grafo}_descomprimido", f"{nombre_grafo}.mtx")
        if not os.path.exists(ruta_mtx):
            print(f" Archivo no encontrado: {ruta_mtx}")
            continue

        archivo_csv = os.path.join(carpeta_resultados, f"resultados_{nombre_grafo}.csv")
        if os.path.exists(archivo_csv):
            print(f" Resultados ya existen para '{nombre_grafo}', se omite.")
            continue

        print(f"\n Procesando grafo '{nombre_grafo}'...")
        for tamaño in tamaños:
            print(f" Generando subgrafos de tamaño {tamaño}...")
            subgrafos = generar_subgrafos_conexos_exactos(ruta_mtx, tamaño_objetivo=tamaño, cantidad=muestras_por_tamaño)
            evaluar_y_guardar(subgrafos, nombre_grafo, tamaño)
