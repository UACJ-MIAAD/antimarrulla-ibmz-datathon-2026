"""Bóveda AES-256-GCM del hospital: guarda cada resultado cifrado en reposo.

- La llave (32 bytes) vive fuera del repositorio; se rechaza una llave dentro del repo.
- Nonce aleatorio de 96 bits por registro; la bóveda verifica que no se repita.
- El id del registro va como dato asociado (AAD): si se altera el id o el cifrado, el descifrado falla.
"""
import base64, json, os, threading
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .rutas import RAIZ


class BovedaError(RuntimeError):
    pass


def cargar_llave(path):
    real = os.path.realpath(path)
    if real.startswith(os.path.realpath(RAIZ) + os.sep):
        raise BovedaError("la llave de la bóveda no puede estar dentro del repositorio")
    with open(real, "rb") as f:
        k = f.read()
    if len(k) != 32:
        raise BovedaError("la llave debe tener 32 bytes (AES-256)")
    return k


def crear_llave(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(AESGCM.generate_key(bit_length=256))


class Boveda:
    def __init__(self, archivo, llave):
        self.archivo, self._aes, self._nonces, self._lock = archivo, AESGCM(llave), set(), threading.Lock()
        os.makedirs(os.path.dirname(archivo) or ".", exist_ok=True)
        if os.path.exists(archivo):
            for linea in open(archivo):
                self._nonces.add(json.loads(linea)["nonce"])

    def guardar(self, rid, obj):
        datos = json.dumps(obj, ensure_ascii=False).encode()
        with self._lock:
            nonce = os.urandom(12)
            n64 = base64.b64encode(nonce).decode()
            if n64 in self._nonces:
                raise BovedaError("nonce repetido")
            self._nonces.add(n64)
            ct = self._aes.encrypt(nonce, datos, rid.encode())
            with open(self.archivo, "a") as f:
                f.write(json.dumps({"id": rid, "nonce": n64, "ct": base64.b64encode(ct).decode()}) + "\n")
                f.flush(); os.fsync(f.fileno())

    def leer(self):
        out = []
        for linea in open(self.archivo):
            r = json.loads(linea)
            pt = self._aes.decrypt(base64.b64decode(r["nonce"]), base64.b64decode(r["ct"]), r["id"].encode())
            out.append((r["id"], json.loads(pt)))
        return out
