#Obtener_Metadatos
# -----------------------------
# Librerías
# -----------------------------
import os
import pandas as pd

RUTA_SALIDA_DIR = Path("data/metadata/descargas_etapa1")
RUTA_SALIDA_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Función auxiliar
# -----------------------------
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

# -----------------------------
# Datos Grafos Masivos
# -----------------------------
grafos_masivos = {
    "soc-flickr": "https://networkrepository.com/soc-flickr.php",
    "soc-youtube-snap": "https://networkrepository.com/soc-youtube-snap.php",
    "ca-dblp-2012": "https://networkrepository.com/ca-dblp-2012.php"
}

# -----------------------------
# Ejecución principal
# -----------------------------
if __name__ == "__main__":
    registros = []
    for nombre, url in grafos_masivos.items():
        estadisticas = extraer_estadisticas_red(nombre, url)
        fila = {
                "nombre": nombre,
                "url": url
            }
        fila.update(estadisticas)
        registros.append(fila)
    df_final = pd.DataFrame(registros)
    salida_csv = RUTA_SALIDA_DIR / f"{nombre}.csv"
    df_final.to_csv(salida_csv, index=False)
