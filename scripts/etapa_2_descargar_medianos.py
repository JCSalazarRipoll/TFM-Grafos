import os, requests
from pathlib import Path
import zipfile

def descargar_y_descomprimir(nombre, url, carpeta_descarga="data/grafos_medianos"):
    os.makedirs(carpeta_descarga, exist_ok=True)
    zip_path = os.path.join(carpeta_descarga, f"{nombre}.zip")
    destino_dir = os.path.join(carpeta_descarga, f"{nombre}_descomprimido")

    if not os.path.exists(zip_path):
        print(f"Descargando {nombre}...")
        r = requests.get(url)
        with open(zip_path, 'wb') as f:
            f.write(r.content)
    else:
        print(f"Ya descargado: {zip_path}")

    if not os.path.exists(destino_dir):
        print(f"Descomprimiendo en: {destino_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(destino_dir)
    else:
        print(f"Ya descomprimido: {destino_dir}")

    return destino_dir

# -----------------------------
# Configuración de rutas
# -----------------------------
RUTA_CONFIG = Path("config/")
RUTA_DESTINO = Path("data/grafos_medianos/")
RUTA_DESTINO.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Función para descargar un .zip
# -----------------------------
def descargar_zip(url, destino):
    nombre = url.split("/")[-1]
    descargar_y_descomprimir(nombre, url)

# -----------------------------
# Proceso principal
# -----------------------------
descargados = []

for archivo_txt in RUTA_CONFIG.glob("*.txt"):
    print(f"\n Procesando archivo: {archivo_txt.name}")
    with open(archivo_txt, "r", encoding="utf-8") as f:
        for linea in f:
            if "http" in linea and ".zip" in linea:
                url = linea.strip().strip(',').strip('"').strip("'")
                print(url)
                if url.startswith("http") and url.endswith(".zip"):
                    nombre = descargar_zip(url, RUTA_DESTINO)
                    if nombre:
                        descargados.append(nombre)

# -----------------------------
# Registro de descargas
# -----------------------------
if descargados:
    with open(RUTA_DESTINO / "descargas_registradas.txt", "w", encoding="utf-8") as f:
        for nombre in descargados:
            f.write(nombre + "\n")
    print(f"\n📁 Se registraron {len(descargados)} descargas en descargas_registradas.txt")
else:
    print("\n⚠️ No se descargó ningún archivo nuevo.")
