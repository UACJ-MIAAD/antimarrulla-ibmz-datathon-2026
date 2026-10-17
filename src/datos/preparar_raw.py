"""Deja data/raw/ con la estructura que esperan recortes_2024.py e historicos.py.

1. Acomoda los tres ZIP del Release datos-2024 (descargados planos en data/raw/) en su subcarpeta.
2. Extrae DEFUN_2024.zip y ssa_egresos_2024.zip ahí mismo.
3. Descarga de la DGIS los históricos que falten: DEFUN_2017..2023 y sectorial_egresos_2018..2023 en data/raw/hist/.

Uso: python src/datos/preparar_raw.py .
Escrito durante el IBM Z Datathon 2026 (17 oct 2026). Solo biblioteca estándar de Python.
"""
import os, shutil, sys, urllib.request, zipfile
REPO = sys.argv[1]; R = f"{REPO}/data/raw"
DGIS = "http://www.dgis.salud.gob.mx/descargas/datosabiertos"
DESTINO = {"DEFUN_2024.zip": "defunciones", "ssa_egresos_2024.zip": "egresos_ssa", "sectorial_egresos_2024.zip": "egresos_sector"}
EXTRAER = {"DEFUN_2024.zip": "REGISTROS/conjunto_de_datos/conjunto_de_datos_defunciones_registradas24_csv.csv",
           "ssa_egresos_2024.zip": "Registros/Egresos.txt"}

for name, sub in DESTINO.items():
    os.makedirs(f"{R}/{sub}", exist_ok=True)
    plano, final = f"{R}/{name}", f"{R}/{sub}/{name}"
    if os.path.exists(plano) and not os.path.exists(final): shutil.move(plano, final)
    if not os.path.exists(final): sys.exit(f"Falta {final}: gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw")
    if name in EXTRAER and not os.path.exists(f"{R}/{sub}/{EXTRAER[name]}"):
        print("extrayendo", final); zipfile.ZipFile(final).extractall(f"{R}/{sub}")

os.makedirs(f"{R}/hist", exist_ok=True)
for y in range(2017, 2024):
    for name, url in ((f"DEFUN_{y}.zip", f"{DGIS}/defunciones/registro/DEFUN_{y}.zip"),
                      (f"sectorial_egresos_{y}.zip", f"{DGIS}/egresos/sectorial_egresos_{y}.zip")):
        if name.startswith("sectorial") and y == 2017: continue
        dest = f"{R}/hist/{name}"
        if not os.path.exists(dest):
            print("descargando", url); urllib.request.urlretrieve(url, dest + ".part"); os.replace(dest + ".part", dest)
print("data/raw listo")
