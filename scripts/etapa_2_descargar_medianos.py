# Librerías estándar
import os, re, csv, time, zipfile
from pathlib import Path

# Librerías externas
import requests
from bs4 import BeautifulSoup
import pandas as pd
import networkx as nx
import re

# -----------------------------
# Configuración de rutas
# -----------------------------
RUTA_CONFIG = Path("config/")
RUTA_DESTINO = Path("data/grafos_medianos/")
RUTA_DESTINO.mkdir(parents=True, exist_ok=True)
RUTA_SALIDA = Path("data/metadata/descargas_etapa2.csv")
RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
RUTA_SALIDA_DIR = Path("data/metadata/descargas_etapa2")
RUTA_SALIDA_DIR.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Funciones auxiliares
# -----------------------------
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

    try:
        response = requests.get(url_php, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error al acceder a {url_php}: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    # Encuentra el panel con el título correcto
    panel = soup.find("div", class_="panel panel-red margin-bottom-40 bg-stats-table")
    if not panel:
        print("No se encontró el panel de estadísticas.")
        return {}

    tabla = panel.find("table", id="sortTableExample")
    if not tabla:
        print("No se encontró la tabla dentro del panel.")
        return {}

    resultados = {}
    for fila in tabla.find_all("tr"):
        celdas = fila.find_all("td")
        if len(celdas) == 2:
            clave = celdas[0].get_text(strip=True)
            valor = celdas[1].get_text(strip=True)
            try:
                resultados[clave] = normalizar_valor(valor)
            except ValueError:
                continue

    print(f"Extraídas {len(resultados)} métricas de {url_php}")
    return resultados

def estadisticas_completas(estadisticas: dict) -> bool:
    METRICAS_ESPERADAS = [
        "Nodes", "Edges", "Density", "Maximum degree", "Minimum degree",
        "Average degree", "Assortativity", "Number of triangles",
        "Average number of triangles", "Maximum number of triangles",
        "Average clustering coefficient", "Fraction of closed triangles",
        "Maximum k-core", "Lower bound of Maximum Clique"
    ]
    return all(m in estadisticas for m in METRICAS_ESPERADAS)

def calcular_aspl(path_grafo):
    G = cargar_grafo(path_grafo)
    if G.number_of_nodes() == 0 or G.number_of_edges() == 0:
        return None  # grafo vacío
    if not nx.is_connected(G):
        return None  # grafo no conexo
    return nx.average_shortest_path_length(G)

def cargar_grafo(path):
    with open(path, 'r') as f:
        lines = [line for line in f if not line.strip().startswith('%') and line.strip()]
    columnas = [line.strip().split() for line in lines]

    edges = []
    for c in columnas:
        if len(c) >= 2:
            try:
                edges.append((int(c[0]), int(c[1])))
            except ValueError:
                continue  # Ignora líneas mal formateadas
    
    G = nx.Graph()
    G.add_edges_from(edges)
    return G

def normalizar_valor(valor: str) -> float:
    valor = valor.replace(",", "")
    if valor.endswith("K"):
        return float(valor[:-1]) * 1_000
    elif valor.endswith("M"):
        return float(valor[:-1]) * 1_000_000
    else:
        return float(valor)


def reparar_aspl_en_csv(csv_path, zip_folder, output_csv):
    df = pd.read_csv(csv_path)
    filas_actualizadas = []
    start = time.perf_counter()

    for _, row in df.iterrows():
        nombre = row['nombre']
        aspl_actual = row.get('ASPL', None)

        # Verifica si el ASPL es válido (float)
        if isinstance(aspl_actual, float) and not pd.isna(aspl_actual):
            filas_actualizadas.append(row)
            continue  # No necesita reparación

        zip_path = os.path.join(zip_folder, nombre)
        aspl_nuevo = None

        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for name in z.namelist():
                    if name.endswith(('.mtx', '.edges', '.graph')):
                        z.extract(name, path="temp_graph")
                        graph_path = os.path.join("temp_graph", name)
                        aspl_nuevo = calcular_aspl(graph_path)
                        os.remove(graph_path)
                        break
        except Exception as e:
            print(f"Error al procesar {nombre}: {e}")
            filas_actualizadas.append(row)
            continue

        if isinstance(aspl_nuevo, float):
            fila = row.copy()
            fila['ASPL'] = aspl_nuevo
            filas_actualizadas.append(fila)
            print(f"ASPL reparado para: {nombre}")
        else:
            print(f"No se pudo reparar ASPL para: {nombre}")
            filas_actualizadas.append(row)

    df_final = pd.DataFrame(filas_actualizadas)
    df_final.to_csv(output_csv, index=False)
    end = time.perf_counter()
    print(f"Reparación completada en {end - start:.2f} segundos")
    print(f"Total de grafos procesados: {len(df_final)}")


def extraer_grafos(path):
    patron = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)$')
    grafos = []

    with open(path, 'r', encoding='utf-8') as archivo:
        for linea in archivo:
            linea = linea.strip()
            match = patron.match(linea)
            if match:
                nombre, url_php, url_zip = match.groups()
                grafos.append((nombre, url_php, url_zip))
            else:
                print(f"Línea ignorada: {linea}")
    return grafos
# -----------------------------
# Funciones principales
# -----------------------------
def etapa_2_completa(config_path, carpeta_zip, salida_csv):
    registros = []
    start = time.perf_counter()

    # Regex que detecta tres bloques separados por espacios o tabulaciones
    patron_linea = re.compile(r'^(\S+)\s+(\S+)\s+(\S+)$')
    
    with open(config_path, 'r') as f:
        for linea in f:
            if not linea.strip():
                continue
            print(linea.strip())  # Para trazabilidad
    
            match = patron_linea.match(linea.strip())
            if not match:
                print(f"Línea mal formateada: {linea.strip()}")
                continue
    
            nombre, url_php, url_zip = match.groups()

            zip_filename = url_zip.split("/")[-1]  
            zip_path = carpeta_zip / zip_filename  


            # Descargar ZIP si no existe
            descargado = descargar_zip(url_zip, carpeta_zip)
            if not descargado:
                print(f"No se pudo descargar: {nombre}")
                continue

            # Extraer estadísticas desde la web
            estadisticas = extraer_estadisticas_red(url_php)
            if not estadisticas_completas(estadisticas):
                print(f"Estadísticas incompletas: {nombre}")

            # Calcular ASPL si es posible
            aspl = None
            try:
                with zipfile.ZipFile(zip_path, 'r') as z:
                    for name in z.namelist():
                        if name.endswith(('.mtx', '.edges', '.graph')):
                            z.extract(name, path="temp_graph")
                            graph_path = os.path.join("temp_graph", name)
                            aspl = calcular_aspl(graph_path)
                            os.remove(graph_path)
                            break
            except Exception as e:
                print(f"Error al calcular ASPL para {nombre}: {e}")

            fila = {
                "nombre": nombre,
                "url_php": url_php,
                "url_zip": url_zip,
                "ASPL": aspl
            }
            fila.update(estadisticas)
            registros.append(fila)
            print(f"Procesado: {nombre}")

    df_final = pd.DataFrame(registros)
    df_final.to_csv(salida_csv, index=False)

    end = time.perf_counter()
    print(f"Etapa 2 completada en {end - start:.2f} segundos")
    print(f"Total de grafos procesados: {len(df_final)}")


# -----------------------------
# Main
# -----------------------------
import glob

if __name__ == "__main__":
    print(f"Ruta de salida: {RUTA_SALIDA}")
    print(f"¿Existe carpeta de salida?: {RUTA_SALIDA.parent.exists()}")

    # Si no existe, la creamos explícitamente
    RUTA_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    
    for config_file in RUTA_CONFIG.glob("*.txt"):
        print(f"\n📂 Procesando archivo: {config_file.name}")
        salida_individual = RUTA_SALIDA_DIR / f"{config_file.stem}.csv"


        etapa_2_completa(
            config_path=config_file,
            carpeta_zip=RUTA_DESTINO,
            salida_csv=salida_individual
        )


