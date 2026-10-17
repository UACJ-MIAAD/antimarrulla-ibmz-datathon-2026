"""Generate demo secrets OUTSIDE the repository (default ~/.screening).
Create a local CA, service certificate, hospital client certificate for mutual TLS 1.3,
and a 32-byte AES-256-GCM vault key. Do not retain the CA signing key.
For two hosts, --service-san adds the service VM IP/hostname (repeatable).
--export-hospital DIR moves the hospital certificate/key and CA certificate to DIR
for secure transfer; no hospital credentials or vault key remain on the service host.
Run: python -m screening.secrets_setup [directory] [--service-san HOST] [--export-hospital DIR]
"""
import argparse, datetime, ipaddress, os, shutil, sys
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
from . import vault
from .paths import ROOT

DEFAULT = os.environ.get("SCREENING_SECRETS", os.path.expanduser("~/.screening"))


def _write(path, data, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, mode)
    with os.fdopen(fd, "wb") as f:
        f.write(data)


def _key():
    return ec.generate_private_key(ec.SECP256R1())


def _pem_key(k):
    return k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())


def _cert(subject, key_pub, issuer, key_issuer, ca=False, san=None, use=None, days=30):
    now = datetime.datetime.now(datetime.timezone.utc)
    b = (x509.CertificateBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, subject)]))
         .issuer_name(issuer).public_key(key_pub).serial_number(x509.random_serial_number())
         .not_valid_before(now - datetime.timedelta(minutes=5)).not_valid_after(now + datetime.timedelta(days=days))
         .add_extension(x509.BasicConstraints(ca=ca, path_length=None), critical=True))
    if san:
        b = b.add_extension(x509.SubjectAlternativeName(san), critical=False)
    if use:
        b = b.add_extension(x509.ExtendedKeyUsage([use]), critical=False)
    if ca:
        b = b.add_extension(x509.KeyUsage(True, False, False, False, False, True, True, False, False), critical=True)
    return b.sign(key_issuer, hashes.SHA256())


def _san(value):
    try:
        return x509.IPAddress(ipaddress.ip_address(value))
    except ValueError:
        return x509.DNSName(value)


def generate(dir_=DEFAULT, san_extra=(), export_hospital=None):
    dir_ = os.path.abspath(dir_)
    if dir_.startswith(os.path.realpath(ROOT) + os.sep):
        sys.exit("secrets must remain outside the repository")
    certs = os.path.join(dir_, "certs"); os.makedirs(certs, mode=0o700, exist_ok=True)
    ca_k = _key(); ca_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Screening demo CA")])
    ca = _cert("Screening demo CA", ca_k.public_key(), ca_name, ca_k, ca=True)
    sv_k = _key()
    sv = _cert("service", sv_k.public_key(), ca_name, ca_k, use=ExtendedKeyUsageOID.SERVER_AUTH,
               san=[x509.DNSName("service"), x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
               + [_san(v) for v in san_extra if v not in ("service", "localhost", "127.0.0.1")])
    ho_k = _key()
    ho = _cert("hospital", ho_k.public_key(), ca_name, ca_k, use=ExtendedKeyUsageOID.CLIENT_AUTH)
    pem = lambda c: c.public_bytes(serialization.Encoding.PEM)
    _write(os.path.join(certs, "ca.pem"), pem(ca), 0o644)
    _write(os.path.join(certs, "service.pem"), pem(sv), 0o644)
    _write(os.path.join(certs, "service.key"), _pem_key(sv_k))
    _write(os.path.join(certs, "hospital.pem"), pem(ho), 0o644)
    _write(os.path.join(certs, "hospital.key"), _pem_key(ho_k))
    if export_hospital:
        destination = os.path.abspath(export_hospital)
        if destination.startswith(os.path.realpath(ROOT) + os.sep):
            sys.exit("the hospital credential bundle must remain outside the repository")
        os.makedirs(destination, mode=0o700, exist_ok=True)
        shutil.copy2(os.path.join(certs, "ca.pem"), os.path.join(destination, "ca.pem"))
        for n in ("hospital.pem", "hospital.key"):
            shutil.move(os.path.join(certs, n), os.path.join(destination, n))
        print("hospital credential bundle:", destination, "(ca.pem, hospital.pem, hospital.key): transfer securely to the hospital host, then remove the transfer copy")
    else:
        vault_key = os.path.join(dir_, "vault.key")
        if not os.path.exists(vault_key):
            vault.create_key(vault_key)
    # Do not retain the CA key; it is used only to sign these certificates.
    print("secrets directory:", dir_, "· service SANs:", ", ".join(["service", "localhost", "127.0.0.1", *san_extra]))
    return dir_


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("directory", nargs="?", default=DEFAULT)
    ap.add_argument("--service-san", action="append", default=[], metavar="HOSTNAME_OR_IP")
    ap.add_argument("--export-hospital", metavar="DIR")
    a = ap.parse_args()
    generate(a.directory, a.service_san, a.export_hospital)
