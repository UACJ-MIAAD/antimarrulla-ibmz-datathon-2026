"""Mediciones del recorrido cifrado y evidencia del entorno.

1. Piloto de 20 pacientes para estimar el costo; con eso se elige el tamaño de la muestra (presupuesto de tiempo).
2. Muestra estratificada y reproducible de la partición de PRUEBA (misma prevalencia, semilla fija).
3. Sobre los mismos registros: flotante, punto fijo (enteros) y cifrado (Paillier) → métricas y errores.
4. Tiempos por fase (cifrar, evaluar, descifrar) en proceso, y recorrido completo por HTTPS con TLS 1.3 mutuo.
5. Bóveda AES-256-GCM medida con la misma biblioteca que usa la app.
6. Entorno: arquitectura, CPU, versiones, OpenSSL (CLI y cryptography), commit y hashes.

Uso: python -m tamizaje.medir [--presupuesto-s 600] [--max 2000] [--https 100]
"""
import argparse, datetime, json, math, os, platform, random, shutil, statistics, subprocess, tempfile, threading, time
import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score
from . import contrato, datos, esquema, hospital, protocolo, secretos, servicio
from .rutas import MEDICIONES, MODELO_JSON, PARTICIONES, RAIZ

SEMILLA_MUESTRA = 2026


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, max(0, math.ceil(q / 100 * len(xs)) - 1))]


def resumen(xs):
    return {"n": len(xs), "p50_ms": round(pct(xs, 50), 3), "p95_ms": round(pct(xs, 95), 3), "media_ms": round(statistics.mean(xs), 3)}


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
        "uname": cmd("uname", "-a"), "commit": cmd("git", "-C", RAIZ, "rev-parse", "HEAD") or os.environ.get("TAMIZAJE_COMMIT"),
        "cambios_sin_commit": bool(cmd("git", "-C", RAIZ, "status", "--porcelain", "--untracked-files=no")) if os.path.isdir(os.path.join(RAIZ, ".git")) else os.environ.get("TAMIZAJE_CAMBIOS") == "1",
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--presupuesto-s", type=float, default=600, help="tiempo máximo para la parte en proceso")
    ap.add_argument("--max", type=int, default=2000)
    ap.add_argument("--https", type=int, default=100, help="recorridos completos por HTTPS")
    a = ap.parse_args()

    modelo = json.load(open(MODELO_JSON)); part = json.load(open(PARTICIONES))
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

    # 1) calentamiento y piloto
    for x in Xte[:5].tolist():
        uno(x)
    t = time.perf_counter()
    for x in Xte[5:25].tolist():
        uno(x)
    por_paciente = (time.perf_counter() - t) / 20
    n = int(min(a.max, max(100, a.presupuesto_s / por_paciente)))
    n = min(n, len(idte))
    print(f"piloto: {por_paciente * 1e3:.1f} ms por paciente → muestra de {n}")

    # 2-3) muestra estratificada: flotante, punto fijo y cifrado sobre los mismos registros
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
    exactos = sum(int(a == b) for a, b in zip(zs, z_ref))
    lf = np.array([sum(w * v for w, v in zip(wf, x)) + bf for x in xs])
    lq = np.array([int(z) / contrato.S_W for z in z_ref]); lc = np.array([int(z) / contrato.S_W for z in zs])
    sig = lambda v: 1 / (1 + np.exp(-v))
    err = np.abs(lc - lf); cotas = np.array([contrato.cota_error_logit(x) for x in xs])

    # 4) recorrido completo por HTTPS (TLS 1.3 mutuo, conexión nueva por solicitud)
    tmp = tempfile.mkdtemp(prefix="tamizaje-medir-")
    secretos.generar(tmp); c = os.path.join(tmp, "certs")
    srv, _ = servicio.crear_servidor("127.0.0.1", 0, modelo, f"{c}/servicio.pem", f"{c}/servicio.key", f"{c}/ca.pem")
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    cli = hospital.ClienteServicio(f"https://localhost:{srv.server_address[1]}", f"{c}/ca.pem", f"{c}/hospital.pem", f"{c}/hospital.key")
    from . import boveda
    bov = boveda.Boveda(os.path.join(tmp, "boveda.jsonl"), boveda.cargar_llave(os.path.join(tmp, "boveda.key")))
    clin = hospital.Clinica(modelo, cli, bov)
    rec = []
    for i in muestra[: a.https]:
        t0 = time.perf_counter(); r = clin.evaluar(dict(zip(esquema.NOMBRES, Xte[fila[i]].tolist())), "medición"); rec.append((time.perf_counter() - t0) * 1e3)
    srv.shutdown(); shutil.rmtree(tmp, ignore_errors=True)

    # 5) bóveda AES-256-GCM con la biblioteca de la app
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    aes = AESGCM(AESGCM.generate_key(bit_length=256)); bloque = os.urandom(1 << 20)
    t0 = time.perf_counter()
    for _ in range(50):
        aes.encrypt(os.urandom(12), bloque, None)
    mb_s = 50 / (time.perf_counter() - t0)

    ahora = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    env = entorno()
    etiqueta = "linuxone-s390x" if env["es_linuxone_s390x"] else f"local-{env['sistema'].lower()}-{env['maquina']}"
    out = {
        "fecha_utc": ahora.isoformat().replace("+00:00", "Z"), "entorno_etiqueta": etiqueta,
        "advertencia": None if env["es_linuxone_s390x"] else "Medición LOCAL: no es LinuxONE. No usar como velocidad de IBM Z.",
        "comando": "python -m tamizaje.medir " + " ".join(f"--{k.replace('_', '-')} {v}" for k, v in vars(a).items()),
        "modelo": modelo["modelo"], "modelo_sha256": datos.sha256(MODELO_JSON), "particiones_sha256": datos.sha256(PARTICIONES),
        "llave_paillier_bits": h.pub.n.bit_length(), "concurrencia": 1, "calentamiento": 5,
        "piloto": {"pacientes": 20, "ms_por_paciente": round(por_paciente * 1e3, 2), "presupuesto_s": a.presupuesto_s},
        "muestra": {"origen": "partición de prueba", "semilla": SEMILLA_MUESTRA, "n": n, "positivos": int(ys.sum()),
                    "prevalencia": round(float(ys.mean()), 4), "ids_sha256": __import__("hashlib").sha256(json.dumps(muestra).encode()).hexdigest()},
        "exactitud": {"enteros_identicos": exactos, "de": n, "error_max_logit_vs_flotante": float(err.max()),
                      "cota_max_aplicable": float(cotas.max()), "todos_dentro_de_cota": bool(np.all(err <= cotas)),
                      "error_max_probabilidad": float(np.abs(sig(lc) - sig(lf)).max())},
        "metricas_misma_muestra": {"flotante": metricas(ys, sig(lf), umbral), "punto_fijo": metricas(ys, sig(lq), umbral), "cifrado": metricas(ys, sig(lc), umbral)},
        "tiempos_en_proceso": {"cifrar_hospital": resumen(cif), "evaluar_servicio": resumen(ev), "descifrar_hospital": resumen(des),
                               "pacientes_por_minuto_secuencial": round(n / t_total * 60, 1)},
        "recorrido_https_tls13": {**resumen(rec), "pacientes_por_minuto_secuencial": round(len(rec) / (sum(rec) / 1e3) * 60, 1),
                                  "nota": "incluye cifrado, handshake TLS 1.3 mutuo por solicitud, evaluación, descifrado y escritura en la bóveda"},
        "tamanos_bytes": {"solicitud_p50": int(pct(b_in, 50)), "respuesta_p50": int(pct(b_out, 50))},
        "boveda_aes256gcm_mb_s": round(mb_s, 1),
        "entorno": env,
    }
    os.makedirs(MEDICIONES, exist_ok=True)
    base = os.path.join(MEDICIONES, f"medicion_{etiqueta}_{ahora.strftime('%Y%m%dT%H%M%SZ')}")
    with open(base + ".json", "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    tp = out["tiempos_en_proceso"]; mc = out["metricas_misma_muestra"]["cifrado"]
    md = f"""# Medición · {etiqueta} · {out['fecha_utc']}

{('> ⚠️ ' + out['advertencia']) if out['advertencia'] else '> Ejecutado en LinuxONE (s390x).'}

- Commit: `{env['commit']}`{' (con cambios sin commit)' if env['cambios_sin_commit'] else ''} · modelo `{out['modelo_sha256'][:16]}` · particiones `{out['particiones_sha256'][:16]}`
- Máquina: {env['maquina']} · {env['plataforma']} · {env['cpus']} CPU · contenedor: {env['contenedor']}
- Python {env['python']} · phe {env['versiones']['phe']} · gmpy2 {env['versiones']['gmpy2']} · cryptography {env['versiones']['cryptography']} ({env['openssl_de_cryptography']}) · OpenSSL CLI: {(env['openssl_cli'] or 'n/d').splitlines()[0]}
- Comando: `{out['comando']}` · llave Paillier {out['llave_paillier_bits']} bits · concurrencia 1 · calentamiento 5

| Muestra (prueba, estratificada, semilla {SEMILLA_MUESTRA}) | Valor |
|---|---|
| Pacientes | {n} ({out['muestra']['positivos']} positivos, prevalencia {out['muestra']['prevalencia']}) |
| Enteros descifrados idénticos a la referencia | {exactos} de {n} |
| Error máximo del logit vs. flotante | {out['exactitud']['error_max_logit_vs_flotante']:.3e} (cota {out['exactitud']['cota_max_aplicable']:.3e}) |
| ROC-AUC flotante / punto fijo / cifrado | {out['metricas_misma_muestra']['flotante']['roc_auc']} / {out['metricas_misma_muestra']['punto_fijo']['roc_auc']} / {mc['roc_auc']} |
| Sensibilidad · especificidad (cifrado, umbral {umbral:.4f}) | {mc['sensibilidad']} · {mc['especificidad']} |

| Fase | p50 (ms) | p95 (ms) |
|---|---:|---:|
| Cifrar 21 variables (hospital) | {tp['cifrar_hospital']['p50_ms']} | {tp['cifrar_hospital']['p95_ms']} |
| Evaluar sobre cifrados (servicio) | {tp['evaluar_servicio']['p50_ms']} | {tp['evaluar_servicio']['p95_ms']} |
| Descifrar (hospital) | {tp['descifrar_hospital']['p50_ms']} | {tp['descifrar_hospital']['p95_ms']} |
| Recorrido completo HTTPS + bóveda ({len(rec)} solicitudes) | {out['recorrido_https_tls13']['p50_ms']} | {out['recorrido_https_tls13']['p95_ms']} |

Pacientes por minuto (secuencial, en proceso): {tp['pacientes_por_minuto_secuencial']} · por HTTPS: {out['recorrido_https_tls13']['pacientes_por_minuto_secuencial']} · solicitud {out['tamanos_bytes']['solicitud_p50']} bytes · respuesta {out['tamanos_bytes']['respuesta_p50']} bytes · bóveda AES-256-GCM {out['boveda_aes256gcm_mb_s']} MB/s.
"""
    with open(base + ".md", "w") as f:
        f.write(md)
    print(md)
    print("guardado en", base + ".json")


if __name__ == "__main__":
    main()
