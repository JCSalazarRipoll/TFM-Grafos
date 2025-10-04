# etapa_1_descarga_masivos
# -----------------------------
# Descargar librerías
# -----------------------------
# Librerías estándar
import os, zipfile
# Librería externa
import requests

# -----------------------------
# Funciones auxiliares
# -----------------------------
def descargar_y_descomprimir(nombre, url, carpeta_descarga="data/grafos_masivos"):
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
# Datos Grafos Masivos
# -----------------------------
grafos_masivos = {
    "soc-flickr": "https://nrvis.com/download/data/soc/soc-flickr.zip",
    "soc-youtube-snap": "https://nrvis.com/download/data/soc/soc-youtube-snap.zip",
    "ca-dblp-2012": "https://nrvis.com/download/data/ca/ca-dblp-2012.zip"
}

if __name__ == "__main__":
    for nombre, url in grafos_masivos.items():
        ruta_final = descargar_y_descomprimir(nombre, url)
        print(f"Grafo listo: {ruta_final}")


 
 
 

