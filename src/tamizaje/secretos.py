"""Genera los secretos de la demo FUERA del repositorio (por defecto ~/.tamizaje):

- CA propia, certificado del servicio de riesgo (SAN: servicio, localhost, 127.0.0.1) y certificado
  de cliente del hospital (TLS 1.3 mutuo).
- Llave de 32 bytes de la bóveda AES-256-GCM.

Dos máquinas (servicio en una VM, hospital en otra):
  --servicio-san IP_O_NOMBRE  agrega la IP pública o el nombre de la VM del servicio al certificado (repetible);
                              sin esto el hospital rechaza la conexión porque el nombre no coincide.
  --exportar-hospital DIR     MUEVE el certificado y la llave de cliente del hospital (más ca.pem) a DIR para
                              llevarlos a la otra máquina; la VM del servicio se queda sin credenciales de hospital
                              y no se genera llave de bóveda (la bóveda es del hospital).

Uso: python -m tamizaje.secretos [directorio] [--servicio-san IP ...] [--exportar-hospital DIR]
"""
import argparse, datetime, ipaddress, os, shutil, sys
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from . import boveda
from .rutas import RAIZ

DEFECTO = os.environ.get("TAMIZAJE_SECRETOS", os.path.expanduser("~/.tamizaje"))


def _escribir(path, data, modo=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, modo)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def _llave():
    return ec.generate_private_key(ec.SECP256R1())


def _pem_llave(k):
    return k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())


def _cert(sujeto, llave_pub, emisor, llave_emisor, ca=False, san=None, uso=None, dias=30):
    ahora = datetime.datetime.now(datetime.timezone.utc)
    b = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, sujeto)]))
         .issuer_name(emisor).public_key(llave_pub).serial_number(x509.random_serial_number())
         .not_valid_before(ahora - datetime.timedelta(minutes=5)).not_valid_after(ahora + datetime.timedelta(days=dias))
         .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True))
    if san:
        b = b.add_extension(x509.SubjectAlternativeName(san), critical=False)
    if uso:
        b = b.add_extension(x509.ExtendedKeyUsage([uso]), critical=False)
    if ca:
        b = b.add_extension(x509.KeyUsage(True, False, False, False, False, True, True, False, False), critical=True)
    return b.sign(llave_emisor, hashes.SHA256())


def _san(valor):
    try:
        return x509.IPAddress(ipaddress.ip_address(valor))
    except ValueError:
        return x509.DNSName(valor)


def generar(dir_=DEFECTO, san_extra=(), exportar_hospital=None):
    dir_ = os.path.abspath(dir_)
    if dir_.startswith(os.path.realpath(RAIZ) + os.sep):
        sys.exit("los secretos no pueden vivir dentro del repositorio")
    certs = os.path.join(dir_, "certs"); os.makedirs(certs, mode=0o700, exist_ok=True)
    ca_k = _llave(); ca_nombre = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Tamizaje demo CA")])
    ca = _cert("Tamizaje demo CA", ca_k.public_key(), ca_nombre, ca_k, ca=True)
    sv_k = _llave()
    sv = _cert("servicio", sv_k.public_key(), ca_nombre, ca_k, uso=ExtendedKeyUsageOID.SERVER_AUTH,
               san=[x509.DNSName("servicio"), x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
               + [_san(v) for v in san_extra if v not in ("servicio", "localhost", "127.0.0.1")])
    ho_k = _llave()
    ho = _cert("hospital", ho_k.public_key(), ca_nombre, ca_k, uso=ExtendedKeyUsageOID.CLIENT_AUTH)
    pem = lambda c: c.public_bytes(serialization.Encoding.PEM)
    _escribir(os.path.join(certs, "ca.pem"), pem(ca), 0o644)
    _escribir(os.path.join(certs, "servicio.pem"), pem(sv), 0o644)
    _escribir(os.path.join(certs, "servicio.key"), _pem_llave(sv_k))
    _escribir(os.path.join(certs, "hospital.pem"), pem(ho), 0o644)
    _escribir(os.path.join(certs, "hospital.key"), _pem_llave(ho_k))
    if exportar_hospital:
        destino = os.path.abspath(exportar_hospital)
        if destino.startswith(os.path.realpath(RAIZ) + os.sep):
            sys.exit("el paquete del hospital no puede vivir dentro del repositorio")
        os.makedirs(destino, mode=0o700, exist_ok=True)
        shutil.copy2(os.path.join(certs, "ca.pem"), os.path.join(destino, "ca.pem"))
        for n in ("hospital.pem", "hospital.key"):
            shutil.move(os.path.join(certs, n), os.path.join(destino, n))
        print("paquete del hospital en", destino, "(ca.pem, hospital.pem, hospital.key): cópialo a la otra máquina y bórralo de aquí")
    else:
        llave_boveda = os.path.join(dir_, "boveda.key")
        if not os.path.exists(llave_boveda):
            boveda.crear_llave(llave_boveda)
    # La llave de la CA no se guarda: solo sirve para firmar estos certificados.
    print("secretos en", dir_, "· SAN del servicio:", ", ".join(["servicio", "localhost", "127.0.0.1", *san_extra]))
    return dir_


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("directorio", nargs="?", default=DEFECTO)
    ap.add_argument("--servicio-san", action="append", default=[], metavar="IP_O_NOMBRE")
    ap.add_argument("--exportar-hospital", metavar="DIR")
    a = ap.parse_args()
    generar(a.directorio, a.servicio_san, a.exportar_hospital)
