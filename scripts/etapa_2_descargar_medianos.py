import os, requests
from pathlib import Path

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
    ruta_archivo = destino / nombre

    if ruta_archivo.exists():
        print(f"✅ Ya existe: {nombre}")
        return nombre

    try:
        print(f"⬇️ Descargando: {nombre}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(ruta_archivo, "wb") as f:
            f.write(response.content)
        return nombre
    except Exception as e:
        print(f"❌ Error al descargar {nombre}: {e}")
        return None

# -----------------------------
# Proceso principal
# -----------------------------
descargados = []

for archivo_txt in RUTA_CONFIG.glob("*.txt"):
    print(f"\n📄 Procesando archivo: {archivo_txt.name}")
    with open(archivo_txt, "r", encoding="utf-8") as f:
        for linea in f:
            url = linea.strip()
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
