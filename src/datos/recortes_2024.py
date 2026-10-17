"""Recorta defunciones 2024 y egresos SSA 2024 (DGIS) a diabetes (E10–E14; O24 en defunciones).
Entrada: data/raw/defunciones/ y data/raw/egresos_ssa/ (Release datos-2024). Salida: data/defunciones/ y data/egresos_ssa/.

Escrito durante el IBM Z Datathon 2026 (17 oct 2026). Solo biblioteca estándar de Python.
"""
import csv, sys
REPO = sys.argv[1]; R = f"{REPO}/data/raw"; DM = ('E10','E11','E12','E13','E14')
# Defunciones
src = f"{R}/defunciones/REGISTROS/conjunto_de_datos/conjunto_de_datos_defunciones_registradas24_csv.csv"
n = 0
with open(src, encoding='utf-8-sig', errors='replace', newline='') as fi, open(f"{REPO}/data/defunciones/defunciones_diabetes_2024.csv", 'w', newline='', encoding='utf-8') as fo:
    rd = csv.reader(fi); h = next(rd); ix = h.index('causa_def'); w = csv.writer(fo); w.writerow(h)
    for r in rd:
        if r[ix].upper().startswith(DM) or r[ix].upper().startswith('O24'): w.writerow(r); n += 1
print("defunciones diabetes (E10-E14 + O24):", n)
# Egresos
ids = set(); n = 0
with open(f"{R}/egresos_ssa/Registros/Egresos.txt", encoding='latin1', newline='') as fi, open(f"{REPO}/data/egresos_ssa/egresos_diabetes_2024.csv", 'w', newline='', encoding='utf-8') as fo:
    rd = csv.reader(fi, delimiter='|'); h = [x.replace('ï»¿', '') for x in next(rd)]; ix = h.index('AFECPRIN'); w = csv.writer(fo); w.writerow(h)
    for r in rd:
        if len(r) > ix and r[ix].upper().startswith(DM): w.writerow(r); ids.add(r[0]); n += 1
print("egresos diabetes principal:", n)
for name in ('Afecciones', 'Procedimientos'):
    m = 0
    with open(f"{R}/egresos_ssa/Registros/{name}.txt", encoding='latin1', newline='') as fi, open(f"{REPO}/data/egresos_ssa/{name.lower()}_diabetes_2024.csv", 'w', newline='', encoding='utf-8') as fo:
        rd = csv.reader(fi, delimiter='|'); h = [x.replace('ï»¿', '') for x in next(rd)]; w = csv.writer(fo); w.writerow(h)
        for r in rd:
            if r and r[0] in ids: w.writerow(r); m += 1
    print(f"{name.lower()} de esos egresos:", m)
