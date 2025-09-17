import requests, re, csv
from pathlib import Path
from bs4 import BeautifulSoup
import os
import zipfile
import time
import pandas as pd
import networkx as nx

# -----------------------------
# Configuración de rutas
# -----------------------------
RUTA_CONFIG = Path("config/")
RUTA_DESTINO = Path("data/grafos_medianos/")
RUTA_DESTINO.mkdir(parents=True, exist_ok=True)
RUTA_SALIDA = Path("data/metadata/descargas_etapa2.csv")
RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Funciones auxiliares
# -----------------------------
def normalizar_valor(valor: str) -> float:
    valor = valor.replace(",", "")
    if valor.endswith("K"):
        return float(valor[:-1]) * 1_000
    elif valor.endswith("M"):
        return float(valor[:-1]) * 1_000_000
    else:
        return float(valor)

def estadisticas_completas(estadisticas: dict) -> bool:
    METRICAS_ESPERADAS = [
        "Nodes", "Edges", "Density", "Maximum degree", "Minimum degree",
        "Average degree", "Assortativity", "Number of triangles",
        "Average number of triangles", "Maximum number of triangles",
        "Average clustering coefficient", "Fraction of closed triangles",
        "Maximum k-core", "Lower bound of Maximum Clique"
    ]
    return all(m in estadisticas for m in METRICAS_ESPERADAS)

def extraer_estadisticas_red(url_php):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    response = requests.get(url_php, headers=headers, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(separator="\n")
    stats_text = text[text.find("Network Data Statistics"):text.find("Network Data Statistics")+1000]

    patrones = {
        "Nodes": r"Nodes\s+([0-9\.KM]+)",
        "Edges": r"Edges\s+([0-9\.KM]+)",
        "Density": r"Density\s+([0-9\.]+)",
        "Maximum degree": r"Maximum degree\s+([0-9\.K]+)",
        "Minimum degree": r"Minimum degree\s+([0-9]+)",
        "Average degree": r"Average degree\s+([0-9\.]+)",
        "Assortativity": r"Assortativity\s+([\-0-9\.]+)",
        "Number of triangles": r"Number of triangles\s+([0-9\.KM]+)",
        "Average number of triangles": r"Average number of triangles\s+([0-9\.]+)",
        "Maximum number of triangles": r"Maximum number of triangles\s+([0-9\.KM]+)",
        "Average clustering coefficient": r"Average clustering coefficient\s+([0-9\.]+)",
        "Fraction of closed triangles": r"Fraction of closed triangles\s+([0-9\.]+)",
        "Maximum k-core": r"Maximum k-core\s+([0-9]+)",
        "Lower bound of Maximum Clique": r"Lower bound of Maximum Clique\s+([0-9]+)"
    }

    return {
        k: normalizar_valor(re.search(v, stats_text).group(1)) for k, v in patrones.items() if re.search(v, stats_text)
    }

def descargar_zip(url_zip, destino):
    nombre = url_zip.split("/")[-1]
    ruta = destino / nombre
    if ruta.exists():
        print(f"Ya existe: {nombre}")
        return True
    try:
        print(f"Descargando: {nombre}")
        response = requests.get(url_zip, timeout=30)
        response.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"Error al descargar {nombre}: {e}")
        return False

def cargar_grafo(path):
    edges = []
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('%') or line.strip() == "":
                continue
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    edges.append((int(parts[0]), int(parts[1])))
                except ValueError:
                    continue  # Ignora líneas con datos no numéricos
    G = nx.Graph()
    G.add_edges_from(edges)
    return G


def calculate_aspl(path_grafo):
    G = cargar_grafo(path_grafo)
    if nx.is_connected(G):
        return nx.average_shortest_path_length(G)
    else:
        componentes = list(nx.connected_components(G))
        total_nodos = sum(len(c) for c in componentes if len(c) > 1)
        suma_ponderada = 0
        for c in componentes:
            if len(c) > 1:
                subgrafo = G.subgraph(c)
                l = nx.average_shortest_path_length(subgrafo)
                suma_ponderada += len(c) * l
        return suma_ponderada / total_nodos if total_nodos > 0 else None


def update_csv_with_aspl(csv_path, zip_folder, output_csv):
    df = pd.read_csv(csv_path)
    aspl_values = []
    start = time.perf_counter()

    for nombre in df['nombre']:
        zip_path = os.path.join(zip_folder, nombre)
        aspl = None

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for name in z.namelist():
                    if name.endswith(('.mtx', '.edges', '.graph')):
                        z.extract(name, path="temp_graph")
                        graph_path = os.path.join("temp_graph", name)
                        aspl = calculate_aspl(graph_path)
                        os.remove(graph_path)
                        break
        except Exception as e:
            aspl = f"Error: {e}"

        aspl_values.append(aspl)

    df['ASPL'] = aspl_values
    df.to_csv(output_csv, index=False)

    end = time.perf_counter()
    total_time = end - start
    print(f"Tiempo total de procesamiento: {total_time:.2f} segundos")


# -----------------------------
# Proceso principal
# -----------------------------

inicio = time.perf_counter()
with open(RUTA_SALIDA, "w", newline="", encoding="utf-8") as f_out:
    writer = None

    for archivo_txt in RUTA_CONFIG.glob("*.txt"):
        print(f"\n Procesando: {archivo_txt.name}")
        with open(archivo_txt, "r", encoding="utf-8") as f_in:
            for linea in f_in:
                if "http" not in linea or ".zip" not in linea:
                    continue

                url_zip = linea.strip().strip(",").strip('"').strip("'")
                nombre_base = url_zip.split("/")[-1].replace(".zip", "")
                url_php = f"https://networkrepository.com/{nombre_base.replace('_', '-')}.php"

                descargado = descargar_zip(url_zip, RUTA_DESTINO)
                try:
                    estadisticas = extraer_estadisticas_red(url_php)
                except Exception as e:
                    estadisticas = {}
                    print(f"Error al extraer estadísticas de {url_php}: {e}")

                aspl = None
                ruta_zip = RUTA_DESTINO / f"{nombre_base}.zip"
                try:
                    with zipfile.ZipFile(ruta_zip, 'r') as z:
                        for archivo in z.namelist():
                            if archivo.endswith(('.mtx', '.edges', '.graph')):
                                z.extract(archivo, path="temp_graph")
                                ruta_grafo = os.path.join("temp_graph", archivo)
                                aspl = calculate_aspl(ruta_grafo)
                                os.remove(ruta_grafo)
                                break
                except Exception as e:
                    aspl = f"Error: {e}"

                fila = {
                    "nombre": nombre_base,
                    "url_zip": url_zip,
                    "url_php": url_php,
                    "descargado": descargado,
                    **estadisticas
                }

                fila["ASPL"] = aspl
                
                if writer is None:
                    writer = csv.DictWriter(f_out, fieldnames=fila.keys())
                    writer.writeheader()
                writer.writerow(fila)
fin = time.perf_counter()
print(f"\n⏱️ Tiempo total de etapa 2 (con ASPL): {fin - inicio:.2f} segundos")
