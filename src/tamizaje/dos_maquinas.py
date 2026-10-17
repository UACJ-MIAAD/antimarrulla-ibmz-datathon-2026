"""Prueba de dos máquinas con datos reales y auditoría de que el servicio nunca vio datos en claro.

Máquina A (servicio de riesgo, sin llave privada):
    SERVICIO_EVIDENCIA=<dir> python -m tamizaje.servicio      (o `make servicio-remoto-docker`)
Máquina B (hospital, tiene la llave privada Paillier):
    python -m tamizaje.dos_maquinas hospital --servicio https://IP_DE_A:8443 --certs <paquete del hospital> --salida <dir>
  Toma una muestra estratificada y reproducible de la partición de PRUEBA del CDC (registros reales de la encuesta
  BRFSS 2015, públicos y anónimos), cifra cada registro, lo manda por TLS 1.3 mutuo, descifra el resultado y lo compara
  con el cálculo en claro. Guarda bitacora_hospital.jsonl (hashes de los bytes enviados/recibidos y resultados
  descifrados; sin los vectores de entrada) y resumen_hospital.json (métricas, tiempos, entorno y procedencia).
Auditoría (en cualquiera de las dos, con la evidencia de ambas en el mismo disco):
    python -m tamizaje.dos_maquinas auditar --servicio <evidencia de A> --hospital <salida de B>
  Escribe el reporte en submission/evidencias/dos_maquinas/ y termina con código 1 si alguna comprobación falla.

Comprobaciones de la auditoría:
  1. Los bytes que guardó el servicio son exactamente los que mandó y recibió el hospital (SHA-256 en ambos lados) y
     los archivos de evidencia no cambiaron desde que se registraron.
  2. Cada solicitud tiene solo los campos del protocolo: 21 cifrados del tamaño de la llave y ningún valor en claro.
  3. Cifrado aleatorizado: todos los cifrados son distintos, aunque los valores en claro se repiten muchísimo.
  4. Ningún resultado descifrado (entero z, probabilidad) ni ningún vector de 21 enteros pequeños aparece en los logs
     o archivos del servicio.
  5. El proceso del servicio no tenía ninguna llave privada Paillier en memoria (al arrancar y en cada solicitud).
  6. Canal: TLS 1.3 con certificado de cliente "hospital".
  7. Dos máquinas distintas (nombre de host diferente; IP del cliente que no es loopback, salvo túnel SSH).
  8. El hospital obtuvo enteros idénticos al cálculo en claro y las mismas métricas en cifrado y en flotante.
"""
import argparse, datetime, glob, hashlib, json, os, platform, re, shutil, sys, time
from . import contrato, esquema, hospital, procedencia, protocolo, servicio
from .rutas import MODELO_JSON, PARTICIONES, RAIZ

SALIDA_REPORTES = os.path.join(RAIZ, "submission", "evidencias", "dos_maquinas")
CAMPOS_SOLICITUD = {"protocolo", "esquema", "modelo", "id", "llave_publica", "exponente", "cifrados"}
CAMPOS_RESPUESTA = {"protocolo", "esquema", "modelo", "id", "exponente", "resultado", "servicio_ms"}
VECTOR_EN_CLARO = re.compile(r"\[\s*(?:-?\d{1,3}\s*,\s*){20}-?\d{1,3}\s*\]")
CALENTAMIENTO = 3


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _sha_archivo(p):
    with open(p, "rb") as f:
        return _sha(f.read())


def _ahora():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)


def _jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


# ------------------------------------------------------------------ máquina B: hospital

def correr_hospital(a):
    import numpy as np
    from . import datos, medir

    with open(MODELO_JSON, "rb") as f:
        crudo_modelo = f.read()
    modelo = json.loads(crudo_modelo)
    certs = os.path.abspath(a.certs)
    cli = hospital.ClienteServicio(a.servicio, os.path.join(certs, "ca.pem"), os.path.join(certs, "hospital.pem"),
                                   os.path.join(certs, "hospital.key"), timeout=60)
    salud = cli.salud()
    print("servicio:", salud)
    if salud.get("modelo") != modelo["modelo"]:
        raise SystemExit(f"el servicio corre otro modelo ({salud.get('modelo')}) que este hospital ({modelo['modelo']})")
    if not salud.get("evidencia") and not a.sin_evidencia:
        raise SystemExit("el servicio no está guardando evidencia: arráncalo con SERVICIO_EVIDENCIA=<dir> "
                         "(o usa --sin-evidencia si solo quieres medir, sin auditoría)")

    part = json.load(open(PARTICIONES))
    ids, X, y = datos.cargar_cdc()
    Xte, yte, idte = datos.cargar_particion(part, "prueba", ids, X, y)
    fila = {int(i): k for k, i in enumerate(idte)}
    n = min(a.n, len(idte))
    muestra = medir.muestra_estratificada(idte.tolist(), yte.tolist(), n)
    calentamiento = [int(i) for i in idte[:CALENTAMIENTO] if int(i) not in set(muestra)][:CALENTAMIENTO]

    h = protocolo.Hospital(modelo)
    W, B, wf, bf = modelo["pesos_enteros"], modelo["intercepto_entero"], modelo["pesos_flotantes"], modelo["intercepto_flotante"]
    umbral = modelo["umbral"]["probabilidad"]
    os.makedirs(a.salida, exist_ok=True)
    ruta_bit = os.path.join(a.salida, "bitacora_hospital.jsonl")
    if os.path.exists(ruta_bit):
        os.replace(ruta_bit, ruta_bit + "." + _ahora().strftime("%Y%m%dT%H%M%SZ") + ".anterior")

    filas, valores_en_claro = [], set()
    with open(ruta_bit, "w") as bit:
        for k, cdc_id in enumerate(calentamiento + muestra):
            es_cal = k < len(calentamiento)
            x = Xte[fila[cdc_id]].tolist()
            t0 = time.perf_counter()
            sol, xv = h.preparar(dict(zip(esquema.NOMBRES, x)))
            cuerpo = json.dumps(sol).encode()
            t1 = time.perf_counter()
            st, d = cli._pedir("POST", "/v1/evaluar", cuerpo)
            t2 = time.perf_counter()
            if st != 200:
                raise SystemExit(f"el servicio respondió HTTP {st}: {d[:200]!r}")
            z, _ = h.descifrar(json.loads(d))
            t3 = time.perf_counter()
            z_ref = contrato.logit_entero(W, B, xv)
            logit_f = sum(w * v for w, v in zip(wf, xv)) + bf
            e = {"id": sol["id"], "cdc_id": cdc_id, "calentamiento": es_cal, "y": int(yte[fila[cdc_id]]),
                 "sha256_solicitud": _sha(cuerpo), "sha256_respuesta": _sha(d), "bytes_in": len(cuerpo), "bytes_out": len(d),
                 "ms_cifrar": round((t1 - t0) * 1e3, 3), "ms_red_y_servicio": round((t2 - t1) * 1e3, 3),
                 "ms_descifrar": round((t3 - t2) * 1e3, 3), "ms_total": round((t3 - t0) * 1e3, 3),
                 "z_descifrado": str(z), "z_esperado": str(z_ref), "identico": z == z_ref,
                 "probabilidad_cifrado": contrato.sigmoide(contrato.logit_de_entero(z)), "probabilidad_flotante": contrato.sigmoide(logit_f)}
            bit.write(json.dumps(e) + "\n")
            if not es_cal:
                filas.append(e)
                valores_en_claro.update((i, v) for i, v in enumerate(xv))
            if not es_cal and (len(filas) % 25 == 0 or len(filas) == n):
                print(f"  {len(filas)}/{n} · último {e['ms_total']:.0f} ms · idénticos {sum(f['identico'] for f in filas)}/{len(filas)}")

    ys = np.array([f["y"] for f in filas])
    pc = np.array([f["probabilidad_cifrado"] for f in filas]); pf = np.array([f["probabilidad_flotante"] for f in filas])
    env = medir.entorno()
    resumen = {
        "fecha_utc": _ahora().isoformat().replace("+00:00", "Z"), "maquina": platform.node(), "maquina_id": servicio.id_maquina(),
        "arquitectura": platform.machine(),
        "servicio_url": a.servicio, "servicio_salud": salud, "modelo": modelo["modelo"], "modelo_sha256": _sha(crudo_modelo),
        "llave_paillier_bits": h.pub.n.bit_length(), "concurrencia": 1, "calentamiento": len(calentamiento),
        "muestra": {"origen": "partición de prueba del CDC (UCI 891, BRFSS 2015): registros reales, públicos y anónimos",
                    "semilla": medir.SEMILLA_MUESTRA, "n": n, "positivos": int(ys.sum()), "prevalencia": round(float(ys.mean()), 4),
                    "ids_sha256": _sha(json.dumps(muestra).encode())},
        "exactitud": {"enteros_identicos": sum(f["identico"] for f in filas), "de": n,
                      "error_max_probabilidad_vs_flotante": float(np.abs(pc - pf).max())},
        "metricas_misma_muestra": {"flotante": medir.metricas(ys, pf, umbral), "cifrado": medir.metricas(ys, pc, umbral)},
        "tiempos_ms": {k: medir.resumen([f[k] for f in filas]) for k in ("ms_total", "ms_cifrar", "ms_red_y_servicio", "ms_descifrar")},
        "tamanos_bytes": {"solicitud_p50": int(medir.pct([f["bytes_in"] for f in filas], 50)), "respuesta_p50": int(medir.pct([f["bytes_out"] for f in filas], 50))},
        "valores_en_claro_distintos": len(valores_en_claro), "valores_en_claro_total": n * len(esquema.NOMBRES),
        "bitacora_sha256": _sha_archivo(ruta_bit), "procedencia": procedencia.registrar(), "entorno": env,
        "comando": " ".join(["python -m tamizaje.dos_maquinas"] + sys.argv[1:]),
    }
    with open(os.path.join(a.salida, "resumen_hospital.json"), "w") as f:
        json.dump(resumen, f, ensure_ascii=False, indent=1)
    t = resumen["tiempos_ms"]["ms_total"]; mc = resumen["metricas_misma_muestra"]["cifrado"]; mf = resumen["metricas_misma_muestra"]["flotante"]
    print(f"\n{n} registros reales del CDC · enteros idénticos {resumen['exactitud']['enteros_identicos']}/{n} · "
          f"ROC-AUC flotante {mf['roc_auc']} / cifrado {mc['roc_auc']} · p50 {t['p50_ms']} ms · p95 {t['p95_ms']} ms")
    print(f"bitácora en {ruta_bit}\nsiguiente paso: copia la carpeta {os.path.abspath(a.salida)} a la máquina del servicio y corre la auditoría")


# ------------------------------------------------------------------ auditoría

def auditar(a):
    hosp = _jsonl(os.path.join(a.hospital, "bitacora_hospital.jsonl"))
    res_h = json.load(open(os.path.join(a.hospital, "resumen_hospital.json")))
    serv = _jsonl(os.path.join(a.servicio, "auditoria_servicio.jsonl"))
    ini_s = json.load(open(os.path.join(a.servicio, "servicio_inicio.json")))
    dir_sol = os.path.join(a.servicio, "solicitudes")
    por_sha = {e["sha256_solicitud"]: e for e in serv}
    nuestras = [por_sha.get(h["sha256_solicitud"]) for h in hosp]
    checks = []

    def check(clave, titulo, ok, detalle):
        checks.append({"clave": clave, "titulo": titulo, "ok": bool(ok), "detalle": detalle})

    # 1. hashes en ambos lados y archivos intactos
    faltan = sum(1 for s in nuestras if s is None)
    resp_distinta = sum(1 for h, s in zip(hosp, nuestras) if s and (s["sha256_respuesta"] != h["sha256_respuesta"] or s["id"] != h["id"]))
    alterados = 0
    for s in filter(None, nuestras):
        base = os.path.join(dir_sol, s["id"])
        try:
            alterados += (_sha_archivo(base + ".solicitud.json") != s["sha256_solicitud"]) + (_sha_archivo(base + ".respuesta.json") != s["sha256_respuesta"])
        except OSError:
            alterados += 2
    check("bytes", "Lo que guardó el servicio es exactamente lo que envió y recibió el hospital", faltan == 0 and resp_distinta == 0 and alterados == 0,
          f"{len(hosp)} solicitudes del hospital · sin registro en el servicio: {faltan} · respuesta distinta: {resp_distinta} · "
          f"archivos de evidencia alterados o ausentes: {alterados}")

    # 2. estructura: solo cifrados
    malas, bits_min, bits_llave, llaves, todos = [], None, set(), set(), []
    for s in filter(None, nuestras):
        try:
            sol = json.load(open(os.path.join(dir_sol, s["id"] + ".solicitud.json")))
            resp = json.load(open(os.path.join(dir_sol, s["id"] + ".respuesta.json")))
            n_ = int(sol["llave_publica"]["n"]); n2 = n_ * n_
            ok = (set(sol) == CAMPOS_SOLICITUD and set(sol["llave_publica"]) == {"n"} and sol["exponente"] == 0
                  and len(sol["cifrados"]) == len(esquema.NOMBRES) and set(resp) <= CAMPOS_RESPUESTA and resp["exponente"] == 0)
            vals = [int(c) for c in sol["cifrados"]] + [int(resp["resultado"])]
            ok = ok and all(0 < v < n2 for v in vals)
            todos.extend(vals[:-1]); llaves.add(n_); bits_llave.add(n_.bit_length())
            m = min(v.bit_length() for v in vals)
            bits_min = m if bits_min is None else min(bits_min, m)
            if not ok:
                malas.append(s["id"])
        except (OSError, ValueError, KeyError, TypeError):
            malas.append(s["id"])
    check("estructura", "Cada solicitud trae solo los campos del protocolo: 21 cifrados y ningún valor en claro",
          not malas and bits_min is not None and bits_min > 3000,
          f"campos permitidos {sorted(CAMPOS_SOLICITUD)} · llave pública de {sorted(bits_llave)} bits · cifrado más corto: {bits_min} bits · "
          f"solicitudes fuera de protocolo: {len(malas)}")

    # 3. aleatorización
    distintos = len(set(todos))
    vc_d, vc_t = res_h.get("valores_en_claro_distintos"), res_h.get("valores_en_claro_total")
    check("aleatorizacion", "Cifrado aleatorizado: valores iguales en claro producen cifrados distintos", todos and distintos == len(todos),
          f"{len(todos)} cifrados, {distintos} distintos · en claro solo había {vc_d} pares (variable, valor) distintos en {vc_t} valores")

    # 4. ningún resultado en claro del lado del servicio
    patrones, chicos = set(), 0
    for h in hosp:
        z = int(h["z_descifrado"])
        if abs(z) >= 10 ** 6:
            patrones.add(str(abs(z)))
        else:
            chicos += 1
        patrones.add(repr(h["probabilidad_cifrado"])); patrones.add(repr(contrato.logit_de_entero(z)))
    archivos = [os.path.join(a.servicio, "auditoria_servicio.jsonl"), os.path.join(a.servicio, "servicio_inicio.json")]
    archivos += sorted(glob.glob(os.path.join(dir_sol, "*.json"))) + [p for p in a.log_servicio or [] if os.path.exists(p)]
    hallazgos, vectores = [], []
    rx = re.compile(r"(?<![\d.])(?:" + "|".join(re.escape(p) for p in sorted(patrones, key=len, reverse=True)) + r")(?![\d])") if patrones else None
    for p in archivos:
        texto = open(p, errors="replace").read()
        if rx:
            hallazgos += [(os.path.basename(p), m.group(0)) for m in rx.finditer(texto)][:3]
        vectores += [os.path.basename(p) for _ in VECTOR_EN_CLARO.finditer(texto)][:1]
    check("sin_claro", "Ningún resultado descifrado ni vector de entrada en claro aparece del lado del servicio", not hallazgos and not vectores,
          f"{len(patrones)} valores buscados (enteros z, logits y probabilidades del hospital; {chicos} z con menos de 7 dígitos no se buscan) "
          f"en {len(archivos)} archivos · hallazgos: {hallazgos[:5] or 0} · vectores de 21 enteros: {len(vectores)}")

    # 5. llave privada
    con_llave = sum(1 for s in filter(None, nuestras) if s["llave_privada_en_memoria"] is not False)
    check("sin_llave", "El proceso del servicio no tenía ninguna llave privada Paillier en memoria",
          ini_s.get("llave_privada_en_memoria") is False and con_llave == 0 and res_h["servicio_salud"].get("llave_privada") is False,
          f"al arrancar: {ini_s.get('llave_privada_en_memoria')} · solicitudes con llave en memoria: {con_llave} · /salud: llave_privada={res_h['servicio_salud'].get('llave_privada')}")

    # 6. canal
    tls = sorted({s["tls"] for s in filter(None, nuestras)}); cns = sorted({str(s["cliente_cn"]) for s in filter(None, nuestras)})
    check("canal", "Canal TLS 1.3 con certificado de cliente del hospital", tls == ["TLSv1.3"] and cns == ["hospital"],
          f"versiones {tls} · certificado de cliente {cns} · cifrado TLS {sorted({str(s['cifrado_tls']) for s in filter(None, nuestras)})}")

    # 7. dos máquinas
    ips = sorted({s["cliente_ip"] for s in filter(None, nuestras)})
    loop = all(ip.startswith("127.") or ip == "::1" for ip in ips)
    ids_m = (res_h.get("maquina_id"), ini_s.get("maquina_id"))
    distintas = res_h["maquina"] != ini_s["maquina"] or (all(ids_m) and ids_m[0] != ids_m[1])
    detalle = (f"hospital `{res_h['maquina']}` id `{ids_m[0]}` ({res_h['arquitectura']}) · servicio `{ini_s['maquina']}` id `{ids_m[1]}` ({ini_s['arquitectura']}) · "
               f"IP del cliente vista por el servicio: {', '.join(ips)}" + (" (loopback: túnel SSH o misma máquina)" if loop else ""))
    if distintas or not a.permitir_misma_maquina:
        check("dos_maquinas", "Hospital y servicio corrieron en máquinas distintas", distintas, detalle)
    else:
        detalle = "ENSAYO en una sola máquina (--permitir-misma-maquina): " + detalle

    # 8. exactitud y métricas
    ex = res_h["exactitud"]; mf = res_h["metricas_misma_muestra"]["flotante"]; mc = res_h["metricas_misma_muestra"]["cifrado"]
    check("exactitud", "El hospital descifró enteros idénticos al cálculo en claro y las mismas métricas",
          ex["enteros_identicos"] == ex["de"] and all(h["identico"] for h in hosp) and abs(mf["roc_auc"] - mc["roc_auc"]) < 1e-4,
          f"enteros idénticos {ex['enteros_identicos']}/{ex['de']} (+{res_h['calentamiento']} de calentamiento) · ROC-AUC flotante {mf['roc_auc']} / cifrado {mc['roc_auc']} · "
          f"error máx. de probabilidad {ex['error_max_probabilidad_vs_flotante']:.2e}")

    ok = all(c["ok"] for c in checks)
    veredicto = ("APROBADA: el servicio solo manejó cifrados" if ok and "dos_maquinas" in {c["clave"] for c in checks}
                 else "ENSAYO APROBADO (misma máquina; repetir con dos máquinas)" if ok else "FALLIDA")
    s390 = [n for n, arq in (("hospital", res_h["arquitectura"]), ("servicio", ini_s["arquitectura"])) if arq == "s390x"]
    ahora = _ahora()
    t = res_h["tiempos_ms"]
    out = {"fecha_utc": ahora.isoformat().replace("+00:00", "Z"), "veredicto": veredicto, "aprobada": ok, "comprobaciones": checks,
           "hospital": {k: res_h[k] for k in ("maquina", "arquitectura", "servicio_url", "modelo", "modelo_sha256", "llave_paillier_bits", "muestra", "exactitud",
                                              "metricas_misma_muestra", "tiempos_ms", "tamanos_bytes", "procedencia", "bitacora_sha256")},
           "servicio": {**ini_s, "solicitudes_registradas": len(serv), "bitacora_sha256": _sha_archivo(os.path.join(a.servicio, "auditoria_servicio.jsonl"))},
           "linuxone_s390x": s390, "comando": " ".join(["python -m tamizaje.dos_maquinas"] + sys.argv[1:])}
    if "dos_maquinas" not in {c["clave"] for c in checks}:
        out["nota"] = detalle

    adv = (f"> Ejecutado en s390x: {', '.join(s390)}." if s390 else "> ⚠️ Ninguna de las dos máquinas es s390x: no es evidencia de LinuxONE.")
    md = f"""# Auditoría de dos máquinas · {out['fecha_utc']}

**{veredicto}**

{adv}

- Hospital (tiene la llave privada): `{res_h['maquina']}` · {res_h['arquitectura']} · commit `{res_h['procedencia']['commit']}` · código `{res_h['procedencia']['codigo_sha256'][:16]}`
- Servicio de riesgo (sin llave): `{ini_s['maquina']}` · {ini_s['arquitectura']} · {ini_s['plataforma']} · código `{ini_s['codigo_sha256'][:16]}` · contenedor: {ini_s['contenedor']}
- Mismo código en ambos lados: {res_h['procedencia']['codigo_sha256'] == ini_s['codigo_sha256']} · modelo `{res_h['modelo_sha256'][:16]}` (servicio `{(ini_s.get('modelo_sha256') or 'n/d')[:16]}`)
- Muestra: {res_h['muestra']['n']} registros REALES de la partición de prueba del CDC (semilla {res_h['muestra']['semilla']}, {res_h['muestra']['positivos']} positivos) · llave Paillier de {res_h['llave_paillier_bits']} bits
- Recorrido: hospital cifra → TLS 1.3 mutuo por la red → servicio calcula Enc(w·x + b) → hospital descifra · concurrencia 1
""" + (f"- ⚠️ {out['nota']}\n" if "nota" in out else "") + f"""
| # | Comprobación | Resultado | Detalle |
|---|---|---|---|
""" + "".join(f"| {i} | {c['titulo']} | {'✅' if c['ok'] else '❌'} | {c['detalle']} |\n" for i, c in enumerate(checks, 1)) + f"""
| Tiempo por paciente, visto desde el hospital | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
""" + "".join(f"| {k.replace('ms_', '').replace('_', ' ')} | {v['p50_ms']} | {v['p95_ms']} | {v['media_ms']} |\n" for k, v in t.items()) + f"""
Solicitud {res_h['tamanos_bytes']['solicitud_p50']} bytes · respuesta {res_h['tamanos_bytes']['respuesta_p50']} bytes (p50).
Bitácoras: hospital `{res_h['bitacora_sha256'][:16]}` · servicio `{out['servicio']['bitacora_sha256'][:16]}` (SHA-256). La evidencia completa
(bytes exactos de cada solicitud) vive fuera del repo; abajo va una muestra de lo que vio el servicio.
"""
    os.makedirs(a.salida, exist_ok=True)
    base = os.path.join(a.salida, f"auditoria_{ahora.strftime('%Y%m%dT%H%M%SZ')}")
    for s in list(filter(None, nuestras))[CALENTAMIENTO:CALENTAMIENTO + a.muestras]:
        for suf in (".solicitud.json", ".respuesta.json"):
            shutil.copy(os.path.join(dir_sol, s["id"] + suf), base + "_" + s["id"][:8] + suf)
        md += f"\n- Muestra `{s['id'][:8]}`: `{os.path.basename(base)}_{s['id'][:8]}.solicitud.json` y `.respuesta.json`"
    with open(base + ".json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w") as f:
        f.write(md + "\n")
    print(md)
    print("reporte en", base + ".md")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hospital", help="máquina B: cifra registros reales del CDC y los manda al servicio remoto")
    h.add_argument("--servicio", required=True, help="https://IP_DEL_SERVICIO:8443")
    h.add_argument("--certs", required=True, help="carpeta con ca.pem, hospital.pem y hospital.key")
    h.add_argument("--salida", required=True, help="carpeta para bitacora_hospital.jsonl y resumen_hospital.json (fuera del repo)")
    h.add_argument("--n", type=int, default=200, help="registros de la partición de prueba (estratificados)")
    h.add_argument("--sin-evidencia", action="store_true", help="permitir un servicio sin SERVICIO_EVIDENCIA (sin auditoría)")
    u = sub.add_parser("auditar", help="comprueba que el servicio nunca vio datos en claro")
    u.add_argument("--servicio", required=True, help="carpeta SERVICIO_EVIDENCIA de la máquina A")
    u.add_argument("--hospital", required=True, help="carpeta --salida de la máquina B")
    u.add_argument("--log-servicio", action="append", help="log de consola del servicio para revisar también (repetible)")
    u.add_argument("--salida", default=SALIDA_REPORTES)
    u.add_argument("--muestras", type=int, default=1, help="pares solicitud/respuesta que se copian al reporte")
    u.add_argument("--permitir-misma-maquina", action="store_true", help="ensayo local: no exige dos máquinas")
    a = ap.parse_args()
    if a.cmd == "hospital":
        correr_hospital(a)
    else:
        sys.exit(auditar(a))


if __name__ == "__main__":
    main()
