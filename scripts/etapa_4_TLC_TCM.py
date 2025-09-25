#Aplicando el teorema del límite central con el teorema de la convergencia monótona
import os
import glob
import networkx as nx

# Ruta a la carpeta con los grafos
carpeta_grafos = "/data/grafos_masivos"
archivos = glob.glob(os.path.join(carpeta_grafos, "*.mxt"))  # ajusta extensión si es .edges o .csv

grafos_masivos = {}

print(f"Buscando archivos en: {carpeta_grafos}")
print(f"Archivos encontrados: {archivos}")

for archivo in archivos:
    nombre = os.path.basename(archivo).split('.')[0]
    try:
        G = nx.read_edgelist(archivo, nodetype=int)
        if nx.is_connected(G):
            grafos_masivos[nombre] = G
            print(f"Grafo '{nombre}' cargado con {G.number_of_nodes()} nodos y {G.number_of_edges()} aristas.")
        else:
            print(f"Grafo '{nombre}' no es conexo. Se omite.")
    except Exception as e:
        print(f"Error al cargar '{nombre}': {e}")

