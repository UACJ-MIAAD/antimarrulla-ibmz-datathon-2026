"""Prepare the data/raw layout expected by extract_2024.py and history.py.
Move the three downloaded datos-2024 release ZIPs into their source subdirectories.
Extract DEFUN_2024.zip and ssa_egresos_2024.zip there. Download missing DGIS historical
ZIPs into data/raw/hist with a 60-second timeout, three attempts and ZIP-integrity checks.
Run: python src/data_prep/prepare_raw.py .
Uses the Python standard library. Original source filenames/columns are preserved.
"""
import os, shutil, sys, time, urllib.request, zipfile
REPO = sys.argv[1]; R = f"{REPO}/data/raw"
DGIS = "http://www.dgis.salud.gob.mx/descargas/datosabiertos"
DESTINATION = {"DEFUN_2024.zip": "defunciones", "ssa_egresos_2024.zip": "egresos_ssa", "sectorial_egresos_2024.zip": "egresos_sector"}
EXTRACT = {"DEFUN_2024.zip": "REGISTROS/conjunto_de_datos/conjunto_de_datos_defunciones_registradas24_csv.csv",
           "ssa_egresos_2024.zip": "Registros/Egresos.txt"}

def valid_zip(path):
    try:
        with zipfile.ZipFile(path) as z: return z.testzip() is None and len(z.infolist()) > 0
    except (zipfile.BadZipFile, OSError): return False

def download(url, dest, attempts=3, timeout=60):
    "Download into dest.part with bounded retries; promote only a valid, integrity-checked ZIP."
    tmp = dest + ".part"
    for k in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r, open(tmp, "wb") as f: shutil.copyfileobj(r, f)
            if valid_zip(tmp): os.replace(tmp, dest); return
            print(f"  intento {k}: file is not a valid ZIP")
        except OSError as e:
            print(f"  intento {k}: {e}")
        if os.path.exists(tmp): os.remove(tmp)
        time.sleep(5 * k)
    sys.exit(f"could not download {url} tras {attempts} intentos")

for name, sub in DESTINATION.items():
    os.makedirs(f"{R}/{sub}", exist_ok=True)
    plaintext, final = f"{R}/{name}", f"{R}/{sub}/{name}"
    if os.path.exists(plaintext) and not os.path.exists(final): shutil.move(plaintext, final)
    if os.path.exists(final) and not valid_zip(final): sys.exit(f"{final} is not a valid ZIP; download it again from the release")
    if not os.path.exists(final): sys.exit(f"Missing {final}: gh release download datos-2024 --repo UACJ-MIAAD/antimarrulla-ibmz-datathon-2026 --dir data/raw")
    if name in EXTRACT and not os.path.exists(f"{R}/{sub}/{EXTRACT[name]}"):
        print("extrayendo", final); zipfile.ZipFile(final).extractall(f"{R}/{sub}")

os.makedirs(f"{R}/hist", exist_ok=True)
for y in range(2017, 2024):
    for name, url in ((f"DEFUN_{y}.zip", f"{DGIS}/defunciones/registro/DEFUN_{y}.zip"),
                      (f"sectorial_egresos_{y}.zip", f"{DGIS}/egresos/sectorial_egresos_{y}.zip")):
        if name.startswith("sectorial") and y == 2017: continue
        dest = f"{R}/hist/{name}"
        if os.path.exists(dest) and not valid_zip(dest): print("Invalid ZIP; downloading again:", dest); os.remove(dest)
        if not os.path.exists(dest):
            print("descargando", url); download(url, dest)
print("data/raw listo")
