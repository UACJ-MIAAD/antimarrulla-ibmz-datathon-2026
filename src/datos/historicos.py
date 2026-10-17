"""Agrega muertes por diabetes 2017–2024 y egresos de la base sectorial 2018–2024 (DGIS).
Entrada: DEFUN_{año}.zip y sectorial_egresos_{año}.zip en data/raw/hist/ (2024 en data/raw/defunciones y data/raw/egresos_sector). Salida: data/historicos/.

Escrito durante el IBM Z Datathon 2026 (17 oct 2026). Solo biblioteca estándar de Python.
"""
import zipfile, io, csv, sys, collections, re, os
csv.field_size_limit(10**9)
REPO = sys.argv[1]; R = f"{REPO}/data/raw"; OUT = f"{REPO}/data/historicos"; os.makedirs(OUT, exist_ok=True)
DM = ('E10','E11','E12','E13','E14')

def biggest_member(zf):
    best = None
    for info in zf.infolist():
        if info.is_dir(): continue
        if best is None or info.file_size > best.file_size: best = info
    return best

def open_table(path):
    zf = zipfile.ZipFile(path)
    m = biggest_member(zf)
    raw = zf.open(m)
    if m.filename.lower().endswith('.zip'):
        inner = zipfile.ZipFile(io.BytesIO(raw.read())); m2 = biggest_member(inner); raw = inner.open(m2); name = m2.filename
    else: name = m.filename
    txt = io.TextIOWrapper(raw, encoding='latin1', newline='')
    first = txt.readline()
    delim = '|' if first.count('|') > first.count(',') else ','
    header = [h.replace('ï»¿', '').replace('﻿', '').strip().strip('"').lower() for h in first.rstrip('\r\n').split(delim)]
    return name, header, csv.reader(txt, delimiter=delim)

def edad_agru_from(edad):
    try: e = int(float(edad))
    except: return ''
    if e >= 4000 and e < 4998: a = e - 4000
    elif e >= 1000 and e < 4000: a = 0
    else: return ''
    return '20-59' if 20 <= a < 60 else ('60+' if a >= 60 else '<20')

# ---------------- Defunciones ----------------
dm_agg = collections.Counter(); tot_agg = collections.Counter(); natl = collections.Counter()
files = [(y, f"{R}/hist/DEFUN_{y}.zip") for y in range(2017, 2024)] + [(2024, f"{R}/defunciones/DEFUN_2024.zip")]
for y, f in files:
    name, h, rd = open_table(f); ix = {k: i for i, k in enumerate(h)}
    need = ['causa_def', 'ent_resid', 'sexo', 'anio_ocur']
    miss = [k for k in need if k not in ix]
    if miss: print("FALTAN columnas", y, miss, h[:20]); continue
    has_ea = 'edad_agru' in ix
    for r in rd:
        if len(r) < len(h) - 2: continue
        ent = r[ix['ent_resid']].strip().zfill(2); sx = r[ix['sexo']].strip()
        tot_agg[(y, ent, sx)] += 1
        c = r[ix['causa_def']].strip().upper()
        if c.startswith(DM) or c.startswith('O24'):
            ea = r[ix['edad_agru']].strip().zfill(2) if has_ea else ''
            g = edad_agru_from(r[ix['edad']]) if 'edad' in ix else ''
            dm_agg[(y, r[ix['anio_ocur']].strip(), ent, sx, g, c[:3])] += 1
            if c.startswith(DM): natl[y] += 1
    print(f"defunciones {y}: archivo {name} | diabetes E10-E14 = {natl[y]:,}")
with open(f"{OUT}/defunciones_diabetes_2017_2024.csv", 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['anio_registro', 'anio_ocurrencia', 'cve_ent_residencia', 'sexo', 'grupo_edad', 'causa_cie3', 'defunciones'])
    for k, v in sorted(dm_agg.items()): w.writerow(list(k) + [v])
with open(f"{OUT}/defunciones_todas_causas_2017_2024.csv", 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['anio_registro', 'cve_ent_residencia', 'sexo', 'defunciones'])
    for k, v in sorted(tot_agg.items()): w.writerow(list(k) + [v])

# ---------------- Egresos sector ----------------
eg = collections.Counter(); dias = collections.Counter(); egt = collections.Counter(); natl_e = collections.Counter()
files = [(y, f"{R}/hist/sectorial_egresos_{y}.zip") for y in range(2018, 2024)] + [(2024, f"{R}/egresos_sector/sectorial_egresos_2024.zip")]
def pick(ix, *names):
    for n in names:
        if n in ix: return ix[n]
    return None
for y, f in files:
    name, h, rd = open_table(f); ix = {k: i for i, k in enumerate(h)}
    i_af = pick(ix, 'afecprin4', 'afecprin', 'afecprin3'); i_dh = pick(ix, 'dh', 'institucion'); i_ent = pick(ix, 'cedocve', 'entidad', 'cve_ent')
    i_sx = pick(ix, 'sexo'); i_ge = pick(ix, 'gpo_edad'); i_ed = pick(ix, 'edad1', 'edad'); i_ce = pick(ix, 'clave_edad', 'cveedad'); i_mo = pick(ix, 'motivo_egreso', 'motegre'); i_di = pick(ix, 'dias_esta')
    if None in (i_af, i_dh, i_ent, i_sx): print("FALTAN columnas egresos", y, h); continue
    for r in rd:
        if len(r) <= max(i_af, i_dh, i_ent, i_sx): continue
        dh = r[i_dh].strip(); ent = r[i_ent].strip().zfill(2)
        egt[(y, ent, dh)] += 1
        a = r[i_af].strip().upper()
        if a.startswith(DM):
            ga = ''
            try:
                ed = int(float(r[i_ed])); ce = r[i_ce].strip() if i_ce is not None else '5'
                if ce == '5' and ed < 150: ga = '20-59' if 20 <= ed < 60 else ('60+' if ed >= 60 else '<20')
                elif ce in ('2', '3', '4'): ga = '<20'
            except: pass
            k = (y, ent, dh, r[i_sx].strip(), r[i_ge].strip() if i_ge is not None else '', ga, r[i_mo].strip() if i_mo is not None else '', a[:3])
            eg[k] += 1; natl_e[y] += 1
            try: dias[k] += int(float(r[i_di]))
            except: pass
    print(f"egresos {y}: archivo {name} | diabetes = {natl_e[y]:,}")
with open(f"{OUT}/egresos_diabetes_2018_2024.csv", 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['anio', 'cve_ent_atencion', 'institucion_dh', 'sexo', 'gpo_edad_dgis', 'grupo_edad', 'motivo_egreso', 'afeccion_cie3', 'egresos', 'dias_estancia_total'])
    for k, v in sorted(eg.items()): w.writerow(list(k) + [v, dias[k]])
with open(f"{OUT}/egresos_todas_causas_2018_2024.csv", 'w', newline='') as fo:
    w = csv.writer(fo); w.writerow(['anio', 'cve_ent_atencion', 'institucion_dh', 'egresos'])
    for k, v in sorted(egt.items()): w.writerow(list(k) + [v])
print("listo")
