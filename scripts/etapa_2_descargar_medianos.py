import requests, re, csv
from pathlib import Path
from bs4 import BeautifulSoup

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
        print(f"✅ Ya existe: {nombre}")
        return True
    try:
        print(f"⬇️ Descargando: {nombre}")
        response = requests.get(url_zip, timeout=30)
        response.raise_for_status()
        with open(ruta, "wb") as f:
            f.write(response.content)
        return True
    except Exception as e:
        print(f"❌ Error al descargar {nombre}: {e}")
        return False

# -----------------------------
# Proceso principal
# -----------------------------
with open(RUTA_SALIDA, "w", newline="", encoding="utf-8") as f_out:
    writer = None

    for archivo_txt in RUTA_CONFIG.glob("*.txt"):
        print(f"\n📄 Procesando: {archivo_txt.name}")
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
                    print(f"⚠️ Error al extraer estadísticas de {url_php}: {e}")

                fila = {
                    "nombre": nombre_base,
                    "url_zip": url_zip,
                    "url_php": url_php,
                    "descargado": descargado,
                    **estadisticas
                }

                if writer is None:
                    writer = csv.DictWriter(f_out, fieldnames=fila.keys())
                    writer.writeheader()
                writer.writerow(fila)
