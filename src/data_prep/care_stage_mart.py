"""Build the 32-state, 2017-2024 care-stage mart from CONAPO, SINAVE, IMSS, history and SIS.
Run: python src/data_prep/care_stage_mart.py REPOSITORY_ROOT/data
Uses the Python standard library. Preserve documented data-source output column names.
"""
import csv, sys, collections, zipfile, io, os
csv.field_size_limit(10**9)
D = sys.argv[1]; os.makedirs(f"{D}/marts", exist_ok=True)
ENT = list(csv.DictReader(open(f"{D}/catalogos/entidades.csv", encoding='utf-8')))
cves = [e['cve_ent'] for e in ENT]
deleg = {}
for e in ENT:
    for d in e['delegaciones_imss'].split(';'): deleg[d.strip()] = e['cve_ent']
YEARS = range(2017, 2025)
M = {(c, y): {} for c in cves for y in YEARS}
# CONAPO population: total and age 20+
for r in csv.DictReader(open(f"{D}/conapo/pobproy_quinq1.csv", encoding='utf-8', errors='replace')):
    y = int(r['ANO']); c = r['CLAVE_ENT'].zfill(2)
    if y not in YEARS or c not in cves: continue
    m = M[(c, y)]; m['poblacion'] = m.get('poblacion', 0) + int(r['POB_TOTAL'])
    adult = sum(int(r[k]) for k in r if k.startswith('POB_') and k not in ('POB_TOTAL', 'POB_00_04', 'POB_05_09', 'POB_010_014', 'POB_015_019'))
    m['poblacion_20mas'] = m.get('poblacion_20mas', 0) + adult
# Newly notified SINAVE cases (T1 + T2)
for t, col in (('tipo1', 'casos_nuevos_t1'), ('tipo2', 'casos_nuevos_t2')):
    for r in csv.DictReader(open(f"{D}/sinave/{t}/products.csv")):
        if r['geography_level'] == 'estado' and r['sex'] == 'general' and int(r['epi_year']) in YEARS:
            m = M[(r['geography_id'], int(r['epi_year']))]; m[col] = m.get(col, 0) + float(r['y_cases'])
# IMSS screening encounters
for r in csv.DictReader(open(f"{D}/imss_detecciones/deteccion_diabetes.csv")):
    y = int(r['ano'].strip()[:4]); c = deleg.get(r['delegacion'].strip())
    if c and y in YEARS: m = M[(c, y)]; m['detecciones_imss'] = m.get('detecciones_imss', 0) + int(float(r['detecciones']))
# Deaths occurring in the year, by residence, E10-E14
for r in csv.DictReader(open(f"{D}/historicos/defunciones_diabetes_2017_2024.csv")):
    if r['causa_cie3'] == 'O24' or r['anio_ocurrencia'] != r['anio_registro']: continue
    y = int(r['anio_registro']); c = r['cve_ent_residencia']
    if (c, y) in M: m = M[(c, y)]; m['defunciones'] = m.get('defunciones', 0) + int(r['defunciones'])
# Sector discharges by treatment state
for r in csv.DictReader(open(f"{D}/historicos/egresos_diabetes_2018_2024.csv")):
    y = int(r['anio']); c = r['cve_ent_atencion']
    if (c, y) in M:
        m = M[(c, y)]; m['egresos'] = m.get('egresos', 0) + int(r['egresos'])
        if r['motivo_egreso'] == '5': m['muertes_hospital'] = m.get('muertes_hospital', 0) + int(r['egresos'])
# SIS: monthly averages for treatment/control; annual HbA1c/foot-examination totals
TR = ['ADM08', 'ADM09', 'ADM11', 'ADM12']; CO = ['ADM14', 'ADM15', 'ADM17', 'ADM18']
for y in (2021, 2022, 2023):
    z = zipfile.ZipFile(f"{D}/sis_cronicas/DA_EC_SIS_{y}.zip"); name = max(z.infolist(), key=lambda i: i.file_size).filename
    rd = csv.DictReader(io.TextIOWrapper(z.open(name), encoding='latin1'))
    mon = collections.defaultdict(lambda: [0, 0]); hba = collections.Counter(); pie = collections.Counter()
    num = lambda v: float(v) if v not in ('', 'NULL', None) else 0.0
    for r in rd:
        c = str(r['CLAVE_ENTIDAD']).zfill(2); mo = r['MES']
        mon[(c, mo)][0] += sum(num(r.get(k)) for k in TR); mon[(c, mo)][1] += sum(num(r.get(k)) for k in CO)
        hba[c] += num(r.get('HBA01')); pie[c] += num(r.get('PDM03'))
    for c in cves:
        months = [v for (cc, mo), v in mon.items() if cc == c]
        if months and (c, y) in M:
            m = M[(c, y)]; m['sis_en_tratamiento'] = round(sum(v[0] for v in months) / len(months)); m['sis_controlados'] = round(sum(v[1] for v in months) / len(months))
            m['sis_pruebas_hba1c'] = int(hba[c]); m['sis_pie_diabetico'] = int(pie[c])
cols = ['cve_ent', 'entidad', 'region_sinave', 'anio', 'poblacion', 'poblacion_20mas', 'casos_nuevos_t1', 'casos_nuevos_t2', 'detecciones_imss', 'sis_en_tratamiento', 'sis_controlados', 'sis_pruebas_hba1c', 'sis_pie_diabetico', 'egresos', 'muertes_hospital', 'defunciones',
        'tasa_casos_100k', 'tasa_defunciones_100k', 'defunciones_por_100_casos', 'pct_controlados_sis']
name = {e['cve_ent']: e['nombre_corto'] for e in ENT}; reg = {e['cve_ent']: e['region_sinave'] for e in ENT}
with open(f"{D}/marts/cascada_entidad_anio.csv", 'w', newline='', encoding='utf-8') as fo:
    w = csv.writer(fo); w.writerow(cols)
    for (c, y), m in sorted(M.items()):
        cases = m.get('casos_nuevos_t1', 0) + m.get('casos_nuevos_t2', 0); p = m.get('poblacion')
        row = {'cve_ent': c, 'entidad': name[c], 'region_sinave': reg[c], 'anio': y, **{k: (round(v) if isinstance(v, float) else v) for k, v in m.items()}}
        if p: row['tasa_casos_100k'] = round(cases / p * 1e5, 1); row['tasa_defunciones_100k'] = round(m.get('defunciones', 0) / p * 1e5, 1) if 'defunciones' in m else ''
        if cases and 'defunciones' in m: row['defunciones_por_100_casos'] = round(m['defunciones'] / cases * 100, 1)
        if m.get('sis_en_tratamiento'): row['pct_controlados_sis'] = round(m['sis_controlados'] / m['sis_en_tratamiento'] * 100, 1)
        w.writerow([row.get(k, '') for k in cols])
# National summary
nat = collections.defaultdict(collections.Counter)
for (c, y), m in M.items():
    for k, v in m.items(): nat[y][k] += v
for y in YEARS:
    n = nat[y]; cases = n['casos_nuevos_t1'] + n['casos_nuevos_t2']
    print(y, f"population {n['poblacion']:,} | cases {cases:,.0f} | IMSS screening {n['detecciones_imss']:,} | SIS treatment {n['sis_en_tratamiento']:,} controlled {n['sis_controlados']:,} | discharges {n['egresos']:,} | deaths {n['defunciones']:,}")
