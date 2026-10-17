"""Mediciones con procedencia verificable.

Modo `proceso` (por defecto), todo dentro de UN proceso:
  - Exactitud: muestra estratificada y reproducible de la partición de PRUEBA del CDC; flotante, punto fijo y cifrado
    sobre los mismos registros (enteros idénticos, error vs. flotante, métricas).
  - microbenchmark_en_proceso: cifrar / evaluar / descifrar sin red.
  - microbenchmark_https_mismo_proceso: hospital lógico + servicio HTTPS con TLS 1.3 mutuo + bóveda, en el mismo proceso.
    NO es el recorrido de dos contenedores.
Modo `api` (--url): cliente HTTP → API del hospital desplegado (Compose) → mTLS → servicio → descifrado → bóveda.
  Pacientes sintéticos deterministas; verifica el hash del modelo remoto y el entero esperado de cada respuesta.
Siempre: procedencia (commit, cambios relevantes, hash del código ejecutado, modelo, particiones, imagen) y entorno.
`--final` rechaza la corrida si hay cambios relevantes sin commit.

Uso: python -m tamizaje.medir [--presupuesto-s 600] [--max 2000] [--https 100] [--final]
     python -m tamizaje.medir --modo api --url http://127.0.0.1:8080 [--n 200] [--final]
"""
import argparse, datetime, json, math, os, platform, random, shutil, statistics, subprocess, tempfile, threading, time
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from . import contrato, datos, esquema, hospital, procedencia, protocolo, secretos, servicio, sinteticos
from .rutas import MEDICIONES, MODELO_JSON, PARTICIONES, RAIZ

SEMILLA_MUESTRA = 2026


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, math.ceil(q / 100 * len(xs)) - 1))]


def resumen(xs):
    return {"n": len(xs), "p50_ms": round(pct(xs, 50), 3), "p95_ms": round(pct(xs, 95), 3), "media_ms": round(statistics.mean(xs), 3)}


def benchmark_claro(modelo, xs, repeticiones=10):
    """Tiempo del logit por paciente, sin red, sigmoide ni I/O; misma muestra que el cifrado.

    Usa microsegundos para no redondear a cero el cálculo en claro. No compara un lote
    vectorizado con solicitudes individuales, ni presenta esto como latencia clínica.
    """
    if not xs or repeticiones < 1:
        raise ValueError("se requiere una muestra y al menos una repetición")
    w, b = modelo["pesos_flotantes"], modelo["intercepto_flotante"]
    W, B = modelo["pesos_enteros"], modelo["intercepto_entero"]
    funciones = {"flotante": lambda x: sum(a * v for a, v in zip(w, x)) + b,
                 "punto_fijo": lambda x: contrato.logit_entero(W, B, x)}
    out = {"n_pacientes": len(xs), "repeticiones": repeticiones, "concurrencia": 1,
           "alcance": "solo logit secuencial por paciente, sin cifrar, red, sigmoide, descifrar ni bóveda",
           "muestra_sha256": __import__("hashlib").sha256(json.dumps(xs).encode()).hexdigest()}
    for nombre, fn in funciones.items():
        for x in xs[:5]:
            fn(x)
        tiempos = []
        for _ in range(repeticiones):
            for x in xs:
                t0 = time.perf_counter_ns()
                fn(x)
                tiempos.append((time.perf_counter_ns() - t0) / 1000)
        out[nombre] = {"n_evaluaciones": len(tiempos), "p50_us": round(pct(tiempos, 50), 3),
                       "p95_us": round(pct(tiempos, 95), 3), "media_us": round(statistics.mean(tiempos), 3)}
    return out


def cmd(*a):
    try:
        return subprocess.run(a, capture_output=True, text=True, timeout=20).stdout.strip() or None
    except (OSError, subprocess.SubprocessError):
        return None


def entorno():
    import cryptography, phe, sklearn
    from cryptography.hazmat.backends.openssl.backend import backend
    try:
        import gmpy2; g = gmpy2.version()
    except ImportError:
        g = None
    info = {
        "maquina": platform.machine(), "sistema": platform.system(), "plataforma": platform.platform(),
        "procesador": platform.processor(), "cpus": os.cpu_count(), "python": platform.python_version(),
        "contenedor": os.path.exists("/.dockerenv"),
        "es_linuxone_s390x": platform.machine() == "s390x",
        "versiones": {"phe": phe.__version__ if hasattr(phe, "__version__") else "1.5.0", "gmpy2": g, "cryptography": cryptography.__version__,
                      "numpy": np.__version__, "scikit_learn": sklearn.__version__},
        "openssl_cli": cmd("openssl", "version", "-a"), "openssl_de_cryptography": backend.openssl_version_text(),
        "uname": cmd("uname", "-a"),
    }
    if platform.system() == "Linux":
        info["lscpu"] = cmd("lscpu")
        info["cpacfinfo"] = cmd("cpacfinfo", "-a") if shutil.which("cpacfinfo") else "cpacfinfo no instalado"
        try:
            info["cpuinfo_features"] = [l for l in open("/proc/cpuinfo") if l.startswith(("features", "Features", "flags"))][:1]
        except OSError:
            pass
    elif platform.system() == "Darwin":
        info["cpu"] = cmd("sysctl", "-n", "machdep.cpu.brand_string")
        info["memoria_bytes"] = cmd("sysctl", "-n", "hw.memsize")
    return info


def muestra_estratificada(ids_prueba, y_prueba, n):
    rnd = random.Random(SEMILLA_MUESTRA)
    pos = [i for i, v in zip(ids_prueba, y_prueba) if v == 1]
    neg = [i for i, v in zip(ids_prueba, y_prueba) if v == 0]
    n_pos = round(n * len(pos) / len(ids_prueba))
    return sorted(rnd.sample(pos, n_pos) + rnd.sample(neg, n - n_pos))


def metricas(y, p, umbral):
    pred = p >= umbral
    tp = int(np.sum(pred & (y == 1))); fn = int(np.sum(~pred & (y == 1))); tn = int(np.sum(~pred & (y == 0))); fp = int(np.sum(pred & (y == 0)))
    return {"roc_auc": round(float(roc_auc_score(y, p)), 6), "average_precision": round(float(average_precision_score(y, p)), 6),
            "sensibilidad": round(tp / (tp + fn), 4), "especificidad": round(tn / (tn + fp), 4),
            "matriz_confusion": {"vn": tn, "fp": fp, "fn": fn, "vp": tp}}


def _guardar(out, modo, etiqueta, ahora, md):
    os.makedirs(MEDICIONES, exist_ok=True)
    base = os.path.join(MEDICIONES, f"medicion_{modo}_{etiqueta}_{ahora.strftime('%Y%m%dT%H%M%SZ')}")
    with open(base + ".json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    with open(base + ".md", "w") as f:
        f.write(md)
    print(md)
    print("guardado en", base + ".json")


def _encabezado(out, env, prov):
    adv = ("> ⚠️ " + out["advertencia"]) if out["advertencia"] else "> Ejecutado en s390x (verificar identidad de LinuxONE Community Cloud con la evidencia de la VM)."
    sucio = "**con cambios relevantes sin commit**: " + ", ".join(prov["cambios_relevantes"]) if prov["limpio"] is False else ("limpio" if prov["limpio"] else "estado no declarado")
    return f"""{adv}

- Commit `{prov['commit']}` ({prov['fuente_commit']}, {sucio}) · código `{prov['codigo_sha256'][:16]}` ({prov['codigo_archivos']} archivos) · modelo `{prov['modelo_sha256'][:16]}` · particiones `{prov['particiones_sha256'][:16]}`{' · imagen `' + prov['imagen'] + '`' if prov['imagen'] else ''}
- Máquina: {env['maquina']} · {env['plataforma']} · {env['cpus']} CPU · contenedor: {env['contenedor']}
- Python {env['python']} · phe {env['versiones']['phe']} · gmpy2 {env['versiones']['gmpy2']} · cryptography {env['versiones']['cryptography']} ({env['openssl_de_cryptography']}) · OpenSSL CLI: {(env['openssl_cli'] or 'n/d').splitlines()[0]}
- Comando: `{out['comando']}` · concurrencia 1
"""


def modo_api(a, modelo, prov, env, ahora, etiqueta):
    import hashlib, urllib.request
    local = procedencia.sha256(MODELO_JSON)
    with urllib.request.urlopen(a.url + "/api/estado", timeout=30) as r:
        estado = json.loads(r.read())
    if estado.get("modelo_sha256") != local:
        raise SystemExit(f"el hospital en {a.url} corre otro modelo ({estado.get('modelo_sha256')}) que el local ({local})")
    if a.final and estado.get("codigo_sha256") != prov["codigo_sha256"]:
        raise SystemExit("modo final: el código del hospital desplegado no coincide con el cliente")
    W, B = modelo["pesos_enteros"], modelo["intercepto_entero"]

    def pedir(paciente):
        cuerpo = json.dumps({"paciente": paciente}).encode()
        req = urllib.request.Request(a.url + "/api/evaluar", data=cuerpo, headers={"Content-Type": "application/json"})
        t0 = time.perf_counter()
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
        return resp, (time.perf_counter() - t0) * 1e3

    pacientes = [sinteticos.aleatorio(SEMILLA_MUESTRA + k) for k in range(a.n + 3)]
    for p in pacientes[:3]:
        pedir(p)  # calentamiento
    cliente, comp, exactos = [], {}, 0
    t_ini = time.perf_counter()
    for p in pacientes[3:]:
        resp, ms = pedir(p)
        cliente.append(ms)
        esperado = contrato.logit_entero(W, B, [p[nm] for nm in esquema.NOMBRES])
        exactos += int(int(resp["hospital"]["z_entero"]) == esperado)
        for k, v in resp["tiempos_ms"].items():
            comp.setdefault(k, []).append(v)
    pared = time.perf_counter() - t_ini
    out = {
        "modo": "api", "fecha_utc": ahora.isoformat().replace("+00:00", "Z"), "entorno_etiqueta": etiqueta,
        "advertencia": None if env["es_linuxone_s390x"] else "Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.",
        "comando": f"python -m tamizaje.medir --modo api --url {a.url} --n {a.n}" + (" --final" if a.final else ""),
        "recorrido": "cliente HTTP → API del hospital desplegado → TLS 1.3 mutuo → servicio de riesgo → descifrado → interpretación → bóveda AES-256-GCM con fsync (sin navegador)",
        "hospital_remoto": {"url": a.url, "maquina": estado.get("maquina"), "sistema": estado.get("sistema"), "modelo_sha256": estado.get("modelo_sha256"),
                            "codigo_sha256": estado.get("codigo_sha256"), "codigo_igual_al_cliente": estado.get("codigo_sha256") == prov["codigo_sha256"], "llave_bits": estado.get("llave_bits")},
        "muestra": {"tipo": "pacientes sintéticos deterministas (sinteticos.aleatorio)", "semilla_inicial": SEMILLA_MUESTRA, "n": a.n, "calentamiento": 3,
                    "sha256": hashlib.sha256(json.dumps(pacientes[3:]).encode()).hexdigest()},
        "exactitud": {"enteros_identicos": exactos, "de": a.n},
        "cliente_ms": resumen(cliente), "componentes_en_hospital_ms": {k: resumen(v) for k, v in comp.items()},
        "pacientes_por_minuto": round(a.n / pared * 60, 1), "concurrencia": 1, "procedencia": prov, "entorno": env,
    }
    c = out["componentes_en_hospital_ms"]
    md = f"# Medición API del hospital · {etiqueta} · {out['fecha_utc']}\n\n" + _encabezado(out, env, prov) + f"""- Recorrido: {out['recorrido']}
- Hospital remoto: {a.url} · máquina {estado.get('maquina')} ({estado.get('sistema')}) · modelo `{local[:16]}` verificado
- Código remoto igual al cliente: {estado.get('codigo_sha256') == prov['codigo_sha256']}

Muestra: {a.n} pacientes sintéticos deterministas (semilla {SEMILLA_MUESTRA}) · enteros idénticos al esperado: {exactos} de {a.n}

| Tramo | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
| Cliente: solicitud completa | {out['cliente_ms']['p50_ms']} | {out['cliente_ms']['p95_ms']} | {out['cliente_ms']['media_ms']} |
""" + "".join(f"| Hospital: {k} | {v['p50_ms']} | {v['p95_ms']} | {v['media_ms']} |\n" for k, v in c.items()) + f"""
Rendimiento secuencial: {out['pacientes_por_minuto']} pacientes/min (n / tiempo de pared).
"""
    _guardar(out, "api", etiqueta, ahora, md)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--modo", choices=["proceso", "api"], default="proceso")
    ap.add_argument("--url", default=None, help="URL de la API del hospital (modo api)")
    ap.add_argument("--n", type=int, default=200, help="solicitudes en modo api")
    ap.add_argument("--presupuesto-s", type=float, default=600, help="tiempo máximo para la parte en proceso")
    ap.add_argument("--max", type=int, default=2000)
    ap.add_argument("--https", type=int, default=100, help="recorridos en el microbenchmark HTTPS del mismo proceso")
    ap.add_argument("--final", action="store_true", help="falla si hay cambios relevantes sin commit")
    a = ap.parse_args()
    if a.n < 2 or a.max < 8 or a.https < 1 or a.presupuesto_s <= 0:
        ap.error("--n debe ser >= 2 y --max >= 8; --https y --presupuesto-s deben ser positivos")

    prov = procedencia.registrar()
    if a.final:
        procedencia.exigir_limpio(prov)
    env = entorno()
    ahora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    etiqueta = ("s390x" if env["es_linuxone_s390x"] else f"local-{env['sistema'].lower()}-{env['maquina']}") + ("-contenedor" if env["contenedor"] else "")
    modelo = json.load(open(MODELO_JSON))
    if a.modo == "api":
        if not a.url:
            raise SystemExit("--modo api requiere --url")
        return modo_api(a, modelo, prov, env, ahora, etiqueta)

    part = json.load(open(PARTICIONES))
    ids, X, y = datos.cargar_cdc()
    Xte, yte, idte = datos.cargar_particion(part, "prueba", ids, X, y)
    fila = {int(i): k for k, i in enumerate(idte)}
    h = protocolo.Hospital(modelo)
    s = protocolo.ServicioRiesgo(protocolo.ModeloCuantizado.desde_json(modelo))
    W, B, wf, bf, umbral = modelo["pesos_enteros"], modelo["intercepto_entero"], modelo["pesos_flotantes"], modelo["intercepto_flotante"], modelo["umbral"]["probabilidad"]

    def uno(x):
        reg = dict(zip(esquema.NOMBRES, x))
        t0 = time.perf_counter(); sol, xv = h.preparar(reg); t1 = time.perf_counter()
        cuerpo = json.dumps(sol); sol2 = json.loads(cuerpo)
        t2 = time.perf_counter(); resp = s.evaluar(sol2); t3 = time.perf_counter()
        rcuerpo = json.dumps(resp)
        t4 = time.perf_counter(); z, _ = h.descifrar(json.loads(rcuerpo)); t5 = time.perf_counter()
        return z, (t1 - t0) * 1e3, (t3 - t2) * 1e3, (t5 - t4) * 1e3, len(cuerpo.encode()), len(rcuerpo.encode())

    for x in Xte[:5].tolist():
        uno(x)
    t = time.perf_counter()
    for x in Xte[5:25].tolist():
        uno(x)
    por_paciente = (time.perf_counter() - t) / 20
    n = min(int(min(a.max, max(100, a.presupuesto_s / por_paciente))), len(idte))
    print(f"piloto: {por_paciente * 1e3:.1f} ms por paciente → muestra de {n}")

    muestra = muestra_estratificada(idte.tolist(), yte.tolist(), n)
    cif, ev, des, b_in, b_out, zs, xs, ys = [], [], [], [], [], [], [], []
    t_ini = time.perf_counter()
    for i in muestra:
        x = Xte[fila[i]].tolist()
        z, a1, a2, a3, bi, bo = uno(x)
        cif.append(a1); ev.append(a2); des.append(a3); b_in.append(bi); b_out.append(bo); zs.append(z); xs.append(x); ys.append(int(yte[fila[i]]))
    t_total = time.perf_counter() - t_ini
    ys = np.array(ys)
    z_ref = [contrato.logit_entero(W, B, x) for x in xs]
    exactos = sum(int(a_ == b_) for a_, b_ in zip(zs, z_ref))
    lf = np.array([sum(w * v for w, v in zip(wf, x)) + bf for x in xs])
    lq = np.array([int(z) / contrato.S_W for z in z_ref]); lc = np.array([int(z) / contrato.S_W for z in zs])
    sig = lambda v: 1 / (1 + np.exp(-v))
    err = np.abs(lc - lf); cotas = np.array([contrato.cota_error_logit(x) for x in xs])
    claro = benchmark_claro(modelo, xs)

    tmp = tempfile.mkdtemp(prefix="tamizaje-medir-")
    secretos.generar(tmp); c = os.path.join(tmp, "certs")
    srv, _ = servicio.crear_servidor("127.0.0.1", 0, modelo, f"{c}/servicio.pem", f"{c}/servicio.key", f"{c}/ca.pem")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    cli = hospital.ClienteServicio(f"https://localhost:{srv.server_address[1]}", f"{c}/ca.pem", f"{c}/hospital.pem", f"{c}/hospital.key")
    from . import boveda
    bov = boveda.Boveda(os.path.join(tmp, "boveda.jsonl"), boveda.cargar_llave(os.path.join(tmp, "boveda.key")))
    clin = hospital.Clinica(modelo, cli, bov)
    rec, comp = [], {}
    t_https = time.perf_counter()
    for i in muestra[: a.https]:
        t0 = time.perf_counter(); r = clin.evaluar(dict(zip(esquema.NOMBRES, Xte[fila[i]].tolist())), "medición"); rec.append((time.perf_counter() - t0) * 1e3)
        for k, v in r["tiempos_ms"].items():
            comp.setdefault(k, []).append(v)
    pared_https = time.perf_counter() - t_https
    srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)

    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aes = AESGCM(AESGCM.generate_key(bit_length=256)); bloque = os.urandom(1 << 20)
    t0 = time.perf_counter()
    for _ in range(50):
        aes.encrypt(os.urandom(12), bloque, None)
    mb_s = 50 / (time.perf_counter() - t0)

    out = {
        "modo": "proceso", "fecha_utc": ahora.isoformat().replace("+00:00", "Z"), "entorno_etiqueta": etiqueta,
        "advertencia": None if env["es_linuxone_s390x"] else "Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.",
        "comando": "python -m tamizaje.medir " + " ".join(f"--{k.replace('_', '-')} {v}" for k, v in vars(a).items() if k not in ("modo", "url", "n", "final")) + (" --final" if a.final else ""),
        "modelo": modelo["modelo"], "llave_paillier_bits": h.pub.n.bit_length(), "concurrencia": 1, "calentamiento": 5,
        "piloto": {"pacientes": 20, "ms_por_paciente": round(por_paciente * 1e3, 2), "presupuesto_s": a.presupuesto_s},
        "muestra": {"origen": "partición de prueba del CDC", "semilla": SEMILLA_MUESTRA, "n": n, "positivos": int(ys.sum()),
                    "prevalencia": round(float(ys.mean()), 4), "ids_sha256": __import__("hashlib").sha256(json.dumps(muestra).encode()).hexdigest()},
        "exactitud": {"enteros_identicos": exactos, "de": n, "error_max_logit_vs_flotante": float(err.max()),
                      "cota_max_aplicable": float(cotas.max()), "todos_dentro_de_cota": bool(np.all(err <= cotas)),
                      "error_max_probabilidad": float(np.abs(sig(lc) - sig(lf)).max())},
        "metricas_misma_muestra": {"flotante": metricas(ys, sig(lf), umbral), "punto_fijo": metricas(ys, sig(lq), umbral), "cifrado": metricas(ys, sig(lc), umbral)},
        "benchmark_claro": claro,
        "microbenchmark_en_proceso": {"cifrar_hospital": resumen(cif), "evaluar_servicio": resumen(ev), "descifrar_hospital": resumen(des),
                                      "pacientes_por_minuto_secuencial": round(n / t_total * 60, 1), "nota": "sin red ni bóveda"},
        "microbenchmark_https_mismo_proceso": {"solicitud_completa": resumen(rec), "componentes": {k: resumen(v) for k, v in comp.items()},
                                               "pacientes_por_minuto_secuencial": round(len(rec) / pared_https * 60, 1),
                                               "nota": "hospital lógico y servicio HTTPS (TLS 1.3 mutuo, conexión nueva por solicitud) en el MISMO proceso, con bóveda y fsync; no es el recorrido de dos contenedores ni incluye navegador"},
        "tamanos_bytes": {"solicitud_p50": int(pct(b_in, 50)), "respuesta_p50": int(pct(b_out, 50))},
        "aes256gcm_microbenchmark_mb_s": round(mb_s, 1), "procedencia": prov, "entorno": env,
    }
    tp = out["microbenchmark_en_proceso"]; mh = out["microbenchmark_https_mismo_proceso"]; mc = out["metricas_misma_muestra"]["cifrado"]
    md = f"# Medición en proceso · {etiqueta} · {out['fecha_utc']}\n\n" + _encabezado(out, env, prov) + f"""
| Muestra (prueba del CDC, estratificada, semilla {SEMILLA_MUESTRA}) | Valor |
|---|---|
| Pacientes | {n} ({out['muestra']['positivos']} positivos, prevalencia {out['muestra']['prevalencia']}) |
| Enteros descifrados idénticos a la referencia | {exactos} de {n} |
| Error máximo del logit vs. flotante | {out['exactitud']['error_max_logit_vs_flotante']:.3e} (cota {out['exactitud']['cota_max_aplicable']:.3e}) |
| ROC-AUC flotante / punto fijo / cifrado | {out['metricas_misma_muestra']['flotante']['roc_auc']} / {out['metricas_misma_muestra']['punto_fijo']['roc_auc']} / {mc['roc_auc']} |
| Sensibilidad · especificidad (cifrado, umbral {umbral:.4f}) | {mc['sensibilidad']} · {mc['especificidad']} |

| Microbenchmark | p50 (ms) | p95 (ms) | media (ms) |
|---|---:|---:|---:|
| En proceso · cifrar 21 variables | {tp['cifrar_hospital']['p50_ms']} | {tp['cifrar_hospital']['p95_ms']} | {tp['cifrar_hospital']['media_ms']} |
| En proceso · evaluar sobre cifrados | {tp['evaluar_servicio']['p50_ms']} | {tp['evaluar_servicio']['p95_ms']} | {tp['evaluar_servicio']['media_ms']} |
| En proceso · descifrar | {tp['descifrar_hospital']['p50_ms']} | {tp['descifrar_hospital']['p95_ms']} | {tp['descifrar_hospital']['media_ms']} |
| HTTPS en el mismo proceso + bóveda ({len(rec)} solicitudes) | {mh['solicitud_completa']['p50_ms']} | {mh['solicitud_completa']['p95_ms']} | {mh['solicitud_completa']['media_ms']} |

Rendimiento secuencial: {tp['pacientes_por_minuto_secuencial']} pacientes/min sin red; {mh['pacientes_por_minuto_secuencial']} con HTTPS en el mismo proceso (n / tiempo de pared). Solicitud {out['tamanos_bytes']['solicitud_p50']} bytes · respuesta {out['tamanos_bytes']['respuesta_p50']} bytes · AES-256-GCM (microbenchmark de la biblioteca) {out['aes256gcm_microbenchmark_mb_s']} MB/s.

Referencia en claro sobre los mismos {n} pacientes ({claro['repeticiones']} repeticiones, solo logit):
flotante p50 {claro['flotante']['p50_us']} µs, p95 {claro['flotante']['p95_us']} µs;
punto fijo p50 {claro['punto_fijo']['p50_us']} µs, p95 {claro['punto_fijo']['p95_us']} µs.
Comparar con evaluar_servicio para el costo del logit cifrado; el recorrido HTTPS además incluye cifrado, red y bóveda.
"""
    _guardar(out, "proceso", etiqueta, ahora, md)


if __name__ == "__main__":
    main()
