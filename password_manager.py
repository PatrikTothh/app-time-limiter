
import hashlib
import json
import secrets

from config import APP_DIR


class PasswordManager:
    ITERATIONS = 600_000

    def __init__(self):
        self.password_file = APP_DIR / "password.json"

    def has_password(self):
        return self.password_file.exists()

    def _hash_password(self, password, salt):
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            self.ITERATIONS,
        ).hex()

    def set_password(self, password):
        APP_DIR.mkdir(parents=True, exist_ok=True)

        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)

        data = {
            "salt": salt,
            "hash": password_hash,
            "iterations": self.ITERATIONS,
        }

        self.password_file.write_text(
            json.dumps(data),
            encoding="utf-8",
        )

    def verify_password(self, password):
        if not self.has_password():
            return False

        try:
            data = json.loads(
                self.password_file.read_text(encoding="utf-8")
            )

            password_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(data["salt"]),
                data["iterations"],
            ).hex()

            return secrets.compare_digest(
                password_hash,
                data["hash"],
            )

        except (OSError, ValueError, KeyError, TypeError):
            return False
