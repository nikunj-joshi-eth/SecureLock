"""Security integration tests with entirely fictional credentials."""

import json
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from securelock_app.authentication import create_vault, save_vault, unlock_vault
from securelock_app.crypto_utils import (AAD_V1, DecryptionError, decrypt,
                                         derive_key, encrypt, generate_salt)
from securelock_app.models import Credential
from securelock_app.storage import (EncryptedEnvelope, VaultFormatError,
                                    read_envelope, write_envelope)


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "fictional.vault"
        self.password = "fictional master password"

    def create(self):
        return create_vault(self.path, self.password)

    def test_create_and_unlock(self):
        session = self.create()
        reopened = unlock_vault(self.path, self.password)
        self.assertEqual(reopened.vault.credentials, [])
        self.assertEqual(reopened.key, session.key)
        self.assertEqual(set(json.loads(self.path.read_text())),
                         {"version", "salt", "nonce", "ciphertext"})
        self.assertNotIn(self.password, repr(session))

    def test_wrong_password(self):
        self.create()
        with self.assertRaises(DecryptionError):
            unlock_vault(self.path, "wrong fictional password")

    def test_save_round_trip_and_no_plaintext(self):
        session = self.create()
        original = read_envelope(self.path)
        record = Credential("fake-id", "fictional.example", "imaginary-user",
                            "fictional credential password")
        session.vault.credentials.append(record)
        save_vault(self.path, session)
        saved = read_envelope(self.path)
        self.assertEqual(original.salt, saved.salt)
        self.assertNotEqual(original.nonce, saved.nonce)
        self.assertEqual(unlock_vault(self.path, self.password).vault.credentials, [record])
        data = self.path.read_bytes()
        for value in (self.password, record.website, record.username, record.password):
            self.assertNotIn(value.encode(), data)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [self.path])

    def test_existing_file_refused(self):
        self.path.write_bytes(b"existing fictional content")
        with self.assertRaises(FileExistsError):
            self.create()
        self.assertEqual(self.path.read_bytes(), b"existing fictional content")

    def test_setup_race_refuses_overwrite(self):
        real_link = os.link
        def competing_link(source, target):
            Path(target).write_bytes(b"competing vault")
            return real_link(source, target)
        with patch("securelock_app.storage.os.link", side_effect=competing_link):
            with self.assertRaises(FileExistsError):
                self.create()
        self.assertEqual(self.path.read_bytes(), b"competing vault")
        self.assertEqual(list(Path(self.directory.name).iterdir()), [self.path])

    def test_ciphertext_nonce_and_salt_tampering(self):
        self.create()
        envelope = read_envelope(self.path)
        for field in ("ciphertext", "nonce", "salt"):
            value = getattr(envelope, field)
            modified = bytes([value[0] ^ 1]) + value[1:]
            write_envelope(self.path, replace(envelope, **{field: modified}))
            with self.assertRaises(DecryptionError):
                unlock_vault(self.path, self.password)

    def test_malformed_envelope_before_kdf(self):
        self.create()
        original = json.loads(self.path.read_text())
        cases = [b"not JSON", b"\xff", b"[]", b'{"version":1,"version":1}',
                 json.dumps({**original, "extra": "field"}).encode()]
        for field, value in (("version", True), ("version", 2), ("salt", "!"),
                             ("salt", "AA=="), ("nonce", None),
                             ("ciphertext", "AA==")):
            cases.append(json.dumps({**original, field: value}).encode())
        for data in cases:
            with self.subTest(data=data):
                self.path.write_bytes(data)
                with patch("securelock_app.authentication.derive_key") as kdf:
                    with self.assertRaises(VaultFormatError):
                        unlock_vault(self.path, self.password)
                    kdf.assert_not_called()

    def test_invalid_session_does_not_corrupt(self):
        session = self.create()
        previous = self.path.read_bytes()
        session.key = b"bad"
        with self.assertRaises(ValueError):
            save_vault(self.path, session)
        session.key = bytes(32)
        session.vault.credentials.append("invalid")
        with self.assertRaises(TypeError):
            save_vault(self.path, session)
        self.assertEqual(self.path.read_bytes(), previous)
        with self.assertRaises(VaultFormatError):
            write_envelope(self.path, EncryptedEnvelope(True, bytes(16), bytes(12), bytes(16)))
        self.assertEqual(self.path.read_bytes(), previous)

    def test_failed_replace_preserves_file_and_cleans_stage(self):
        session = self.create()
        previous = self.path.read_bytes()
        with patch("securelock_app.storage.os.replace", side_effect=OSError("simulated I/O failure")):
            with self.assertRaises(OSError):
                save_vault(self.path, session)
        self.assertEqual(self.path.read_bytes(), previous)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [self.path])

    def test_invalid_decrypted_payload(self):
        session = self.create()
        for payload in (b"not JSON", b'{"credentials":{}}',
                        b'{"credentials":[{"password":"fictional"}]}',
                        b'{"credentials":[],"extra":0}'):
            nonce, ciphertext = encrypt(payload, session.key)
            write_envelope(self.path, EncryptedEnvelope(1, session.salt, nonce, ciphertext))
            with self.assertRaises(VaultFormatError):
                unlock_vault(self.path, self.password)

    def test_randomness_and_kdf(self):
        salts = [generate_salt() for _ in range(20)]
        self.assertEqual(len(set(salts)), 20)
        self.assertTrue(all(len(salt) == 16 for salt in salts))
        key = derive_key(self.password, salts[0])
        self.assertEqual(len(key), 32)
        self.assertEqual(key, derive_key(self.password, salts[0]))
        self.assertNotEqual(key, derive_key(self.password, salts[1]))
        encrypted = [encrypt(b"", key) for _ in range(20)]
        self.assertEqual(len({nonce for nonce, _ in encrypted}), 20)
        for nonce, ciphertext in encrypted:
            self.assertEqual(len(nonce), 12)
            self.assertEqual(decrypt(ciphertext, key, nonce), b"")
        nonce, ciphertext = encrypted[0]
        wrong_aad = AESGCM(key).encrypt(nonce, b"fictional", AAD_V1 + b"changed")
        with self.assertRaises(DecryptionError):
            decrypt(wrong_aad, key, nonce)

    def test_envelope_size_limit(self):
        self.path.write_bytes(b" " * 129)
        with patch("securelock_app.storage.MAX_ENVELOPE_BYTES", 128):
            with self.assertRaises(VaultFormatError):
                read_envelope(self.path)
            with self.assertRaises(VaultFormatError):
                write_envelope(self.path, EncryptedEnvelope(1, bytes(16), bytes(12), bytes(100)))
        self.assertEqual(self.path.read_bytes(), b" " * 129)

    def test_unicode_password_error_is_safe(self):
        secret = "fictional" + chr(0xD800)
        with self.assertRaises(ValueError) as caught:
            derive_key(secret, bytes(16))
        self.assertNotIn("fictional", str(caught.exception))

    def test_invalid_inputs(self):
        for password in ("short", "        ", None):
            with self.assertRaises((TypeError, ValueError)):
                create_vault(self.path, password)
            self.assertFalse(self.path.exists())
        with self.assertRaises(TypeError):
            create_vault(str(self.path), self.password)
        for salt in (b"short", "not bytes"):
            with self.assertRaises((TypeError, ValueError)):
                derive_key(self.password, salt)
        with self.assertRaises(ValueError):
            encrypt(b"fictional", b"short")
        with self.assertRaises(TypeError):
            encrypt("fictional", bytes(32))
        with self.assertRaises(ValueError):
            decrypt(bytes(16), bytes(32), b"short")


if __name__ == "__main__":
    unittest.main()
