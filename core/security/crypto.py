"""Atlas OS - encryption-at-rest helpers (opt-in).

Implements symmetric encryption of arbitrary blobs using AES-GCM with a
passphrase-derived key (scrypt KDF). Encrypted output is a self-contained
JSON envelope (``salt``, ``nonce``, ``ciphertext``, ``v``).

Used by ``EncryptedMemory`` to provide an optional encrypted ``MemoryStore``.
The module is deliberately small: it crosses one crypto library boundary
plus a SHA-256-stretch fallback so tests can exercise the surface without
``cryptography`` installed.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
from typing import Any, Dict, Tuple, Optional

_VERSION = 1
_SALT_BYTES = 16
_NONCE_BYTES = 12
_KEY_BYTES = 32
_SCRYPT_N = 2 ** 14       # default cost; small for dev, raise in prod
_SCRYPT_R = 8
_SCRYPT_P = 1


def _passphrase_to_key(passphrase: str, salt: bytes) -> bytes:
    """Derive a 32-byte key from ``passphrase`` and ``salt``.

    Tries ``hashlib.scrypt`` first; falls back to a ``hashlib.pbkdf2_hmac``
    loop so the surface is testable on systems without ``scrypt``.
    """
    try:
        return hashlib.scrypt(
            passphrase.encode("utf-8"),
            salt=salt,
            n=_SCRYPT_N,
            r=_SCRYPT_R,
            p=_SCRYPT_P,
            dklen=_KEY_BYTES,
        )
    except Exception:
        # Fallback: SHA-256 stretch (NOT as strong as scrypt).
        h = hashlib.sha256(salt + passphrase.encode("utf-8")).digest()
        for _ in range(50_000):
            h = hashlib.sha256(h + salt).digest()
        return h[:_KEY_BYTES]


def _aesgcm_encrypt(key: bytes, nonce: bytes, plaintext: bytes) -> bytes:
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
        return AESGCM(key).encrypt(nonce, plaintext, associated_data=None)
    except Exception:
        # No real AES-GCM available: refuse rather than fake-encrypt.
        raise RuntimeError(
            "AESGCM unavailable. Install `cryptography` to enable encrypted memory."
        )


def _aesgcm_decrypt(key: bytes, nonce: bytes, ciphertext: bytes) -> bytes:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # type: ignore
    return AESGCM(key).decrypt(nonce, ciphertext, associated_data=None)


def encrypt_blob(plaintext: bytes, passphrase: str) -> Dict[str, str]:
    """Encrypt ``plaintext`` and return a JSON-serialisable envelope."""
    salt = secrets.token_bytes(_SALT_BYTES)
    nonce = secrets.token_bytes(_NONCE_BYTES)
    key = _passphrase_to_key(passphrase, salt)
    ciphertext = _aesgcm_encrypt(key, nonce, plaintext)
    return {
        "v": _VERSION,
        "kdf": "scrypt-fallback" if _passphrase_to_key is not None else "scrypt",
        "salt_b64": base64.b64encode(salt).decode("ascii"),
        "nonce_b64": base64.b64encode(nonce).decode("ascii"),
        "ciphertext_b64": base64.b64encode(ciphertext).decode("ascii"),
    }


def decrypt_blob(envelope: Dict[str, str], passphrase: str) -> bytes:
    if int(envelope.get("v", 0)) != _VERSION:
        raise ValueError(f"unsupported envelope version: {envelope.get('v')}")
    salt = base64.b64decode(envelope["salt_b64"])
    nonce = base64.b64decode(envelope["nonce_b64"])
    ciphertext = base64.b64decode(envelope["ciphertext_b64"])
    key = _passphrase_to_key(passphrase, salt)
    return _aesgcm_decrypt(key, nonce, ciphertext)


class EncryptedMemory:
    """Drop-in encrypted MemoryStore.

    Backed by a plain ``MemoryStore``-style JSON file but every entry is
    AES-GCM-encrypted. The passphrase is supplied once at construction
    or via the ``ATLAS_MEMORY_PASSPHRASE`` env var.
    """

    def __init__(self, path: str, passphrase: str) -> None:
        self.path = path
        self.passphrase = passphrase
        self.data = self._load()

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return {"history": []}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                envelope = json.load(f)
            blob = decrypt_blob(envelope, self.passphrase)
            data = json.loads(blob.decode("utf-8"))
            return data
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(
                f"Could not decrypt {self.path}: {exc}. "
                "Set ATLAS_MEMORY_PASSPHRASE or remove the file to start over."
            )

    def save(self) -> None:
        plaintext = json.dumps(self.data, indent=2).encode("utf-8")
        envelope = encrypt_blob(plaintext, self.passphrase)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2)

    def add(self, entry: Dict[str, Any]) -> None:
        self.data.setdefault("history", []).append(entry)
        self.save()

    def get_recent(self, n: int = 5) -> list:
        return self.data.get("history", [])[-n:]

    def clear(self) -> None:
        self.data = {"history": []}
        self.save()
