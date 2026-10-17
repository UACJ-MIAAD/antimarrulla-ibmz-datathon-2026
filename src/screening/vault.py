"""Hospital AES-256-GCM vault: encrypt each result at rest.
The 32-byte key must remain outside the repository. Use a random 96-bit nonce per record
and reject reuse. Bind the record ID as associated data so altered IDs/ciphertexts fail authentication.
"""
import base64, json, os, threading
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .paths import ROOT


class VaultError(RuntimeError):
    pass


def load_key(path):
    current = os.path.realpath(path)
    if current.startswith(os.path.realpath(ROOT) + os.sep):
        raise VaultError("the vault key must remain outside the repository")
    with open(current, "rb") as f:
        k = f.read()
    if len(k) != 32:
        raise VaultError("the key must contain 32 bytes for AES-256")
    return k


def create_key(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as f:
        f.write(AESGCM.generate_key(bit_length=256))


class Vault:
    def __init__(self, file, key):
        self.file, self._aes, self._nonces, self._lock = file, AESGCM(key), set(), threading.Lock()
        os.makedirs(os.path.dirname(file) or ".", exist_ok=True)
        if os.path.exists(file):
            for line in open(file):
                self._nonces.add(json.loads(line)["nonce"])

    def save(self, rid, obj):
        data = json.dumps(obj, ensure_ascii=False).encode()
        with self._lock:
            nonce = os.urandom(12)
            n64 = base64.b64encode(nonce).decode()
            if n64 in self._nonces:
                raise VaultError("nonce repetido")
            self._nonces.add(n64)
            ct = self._aes.encrypt(nonce, data, rid.encode())
            with open(self.file, "a") as f:
                f.write(json.dumps({"id": rid, "nonce": n64, "ct": base64.b64encode(ct).decode()}) + "\n")
                f.flush(); os.fsync(f.fileno())

    def read(self):
        out = []
        for line in open(self.file):
            r = json.loads(line)
            pt = self._aes.decrypt(base64.b64decode(r["nonce"]), base64.b64decode(r["ct"]), r["id"].encode())
            out.append((r["id"], json.loads(pt)))
        return out
