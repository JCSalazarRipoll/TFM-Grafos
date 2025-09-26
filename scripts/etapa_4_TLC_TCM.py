#Aplicando el teorema del límite central con el teorema de la convergencia monótona
import os
import csv
import random
import networkx as nx
from datetime import datetime

#  Rutas
ruta_mtx = "/content/TFM-Grafos/data/grafos_masivos/soc-livejournal/soc-livejournal.mtx"
carpeta_resultados = "/content/TFM-Grafos/resultados_etapa_4"
os.makedirs(carpeta_resultados, exist_ok=True)

#  Generar subgrafos conexos de tamaño exacto
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
        i += 1  # avanzar para el siguiente intento
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
                print(f" Rep {rep+1}: ASPL = {aspl:.4f}")
            else:
                print(f" Rep {rep+1}: Subgrafo no conexo (debería ser raro)")

#  Ejecución principal
if __name__ == "__main__":
    nombre_grafo = "soc-livejournal"
    tamaños = [500, 1000, 2000]
    muestras_por_tamaño = 30

    for tamaño in tamaños:
        print(f"\n Generando subgrafos de tamaño {tamaño} para '{nombre_grafo}'...")
        subgrafos = generar_subgrafos_conexos_exactos(ruta_mtx, tamaño_objetivo=tamaño, cantidad=muestras_por_tamaño)
        evaluar_y_guardar(subgrafos, nombre_grafo, tamaño)
