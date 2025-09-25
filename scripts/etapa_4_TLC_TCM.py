#Aplicando el teorema del límite central con el teorema de la convergencia monótona
import os
import glob
import networkx as nx
from scipy.io import mmread

# Ruta raíz
carpeta_raiz = "/content/TFM-Grafos/data/grafos_masivos"
archivos_mtx = glob.glob(os.path.join(carpeta_raiz, "**/*.mtx"), recursive=True)

grafos_masivos = {}

print(f"🔍 Archivos encontrados: {len(archivos_mtx)}")

for archivo in archivos_mtx:
    nombre = os.path.basename(archivo).split('.')[0]
    try:
        matriz = mmread(archivo).tocoo()
        G = nx.Graph()
        G.add_edges_from(zip(matriz.row, matriz.col))

        if not nx.is_connected(G):
            G = G.subgraph(max(nx.connected_components(G), key=len)).copy()

        grafos_masivos[nombre] = G
        print(f"✅ '{nombre}': {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas.")
    except Exception as e:
        print(f"❌ Error al cargar '{nombre}': {e}")

