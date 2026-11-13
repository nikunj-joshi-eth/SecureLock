"""Use fictional sample strings only; no files or real credentials."""

import unittest

from securelock_app.models import (
    Credential, Vault, validate_credential, validate_required_text, validate_vault,
)


class ModelTests(unittest.TestCase):
    def sample(self, identifier="sample-1"):
        return Credential(identifier, "Example", "student", " fake sample ")

    def test_valid_fields_preserved(self):
        credential = self.sample()
        self.assertEqual(credential.password, " fake sample ")
        self.assertIsNone(validate_credential(credential))
        self.assertNotIn(credential.password, repr(credential))

    def test_all_fields_reject_blank_and_wrong_types(self):
        for name in ("id", "website", "username", "password"):
            for value in ("", " \t\n", None, 123, [], b"sample"):
                with self.subTest(field=name, value=value):
                    fields = dict(id="1", website="Example", username="student",
                                  password="fictional")
                    fields[name] = value
                    error = ValueError if isinstance(value, str) else TypeError
                    with self.assertRaises(error):
                        Credential(**fields)

    def test_service_labels_and_unicode_allowed(self):
        self.assertEqual(Credential("1", "कॉलेज", "学生", "x").website, "कॉलेज")

    def test_required_text_does_not_echo_secret(self):
        with self.assertRaises(TypeError) as caught:
            validate_required_text(b"fictional secret", "password")
        self.assertNotIn("fictional secret", str(caught.exception))

    def test_vault_lists_are_independent(self):
        first, second = Vault(), Vault()
        first.credentials.append(self.sample())
        self.assertEqual(second.credentials, [])
        self.assertIsNone(validate_vault(first))

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(ValueError):
            Vault([self.sample(), self.sample()])

    def test_distinct_ids_can_share_login_fields(self):
        self.assertEqual(len(Vault([self.sample("1"), self.sample("2")]).credentials), 2)

    def test_invalid_vault_contents(self):
        for contents in (None, (), {}, ["invalid"], [None]):
            with self.subTest(contents=contents), self.assertRaises(TypeError):
                Vault(contents)

    def test_revalidate_mutated_vault(self):
        vault = Vault([self.sample()])
        vault.credentials.append(self.sample())
        with self.assertRaises(ValueError):
            validate_vault(vault)

    def test_helpers_reject_wrong_models(self):
        with self.assertRaises(TypeError):
            validate_credential({})
        with self.assertRaises(TypeError):
            validate_vault([])


if __name__ == "__main__":
    unittest.main()
