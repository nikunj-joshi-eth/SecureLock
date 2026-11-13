"""Password tools tests using fictional credentials only."""

import contextlib
import copy
import io
import logging
import string
import unittest
from unittest.mock import patch

from securelock_app.models import Credential, Vault
from securelock_app.password_tools import (
    estimate_strength, find_duplicate_passwords, generate_password,
    security_statistics,
)


def make_vault(*passwords):
    return Vault([Credential(str(i), "fictional.example", "fake-user", password)
                  for i, password in enumerate(passwords)])


class GenerationTests(unittest.TestCase):
    def test_lengths_and_categories(self):
        for length in (8, 16, 128):
            for _ in range(10):
                password = generate_password(length)
                self.assertEqual(len(password), length)
                for category in (string.ascii_lowercase, string.ascii_uppercase,
                                 string.digits, string.punctuation):
                    self.assertTrue(any(c in category for c in password))
        self.assertEqual(len(generate_password()), 16)

    def test_without_symbols(self):
        for length in (8, 16, 128):
            password = generate_password(length, use_symbols=False)
            self.assertTrue(set(password) <= set(string.ascii_letters + string.digits))
            self.assertTrue(any(c.islower() for c in password))
            self.assertTrue(any(c.isupper() for c in password))
            self.assertTrue(any(c.isdigit() for c in password))

    def test_invalid_lengths(self):
        for value in (-1, 0, 7, 129):
            with self.assertRaises(ValueError):
                generate_password(value)

    def test_invalid_types(self):
        for value in (True, False, 16.0, "16", None, [], b"16"):
            with self.assertRaises(TypeError):
                generate_password(value)
        for value in (0, 1, "yes", None, []):
            with self.assertRaises(TypeError):
                generate_password(use_symbols=value)

    def test_rejects_candidate_missing_categories(self):
        with patch("securelock_app.password_tools.secrets.choice",
                   side_effect=list("aaaaaaaa" + "kR7!mT2?")) as choice:
            self.assertEqual(generate_password(8), "kR7!mT2?")
            self.assertEqual(choice.call_count, 16)


class StrengthTests(unittest.TestCase):
    def test_classifications_and_boundaries(self):
        cases = {"": "weak", "aB3!": "weak", "abcdefghijklmno": "weak",
                 "Raven372": "moderate", "Raven372!xy": "moderate",
                 "Raven372!xyz": "strong", "Raven372!xyzt": "strong",
                 "Ravenforesttrail": "moderate", "Élan雪7!Orbi": "moderate",
                 "Élan雪7!Orbit": "strong", "        ": "weak"}
        for password, expected in cases.items():
            self.assertEqual(estimate_strength(password), expected)

    def test_common_and_repeated_patterns(self):
        for password in ("PASSWORD!9037", "Xqwerty!98765", "LetMeIn!9087",
                         "Welcome!9087", "Admin!9087", "X123456!abcd",
                         "Xabcdef!9087", "aB3!aB3!aB3!", "abABabAB",
                         "777777777777", "xyxyxyxyxyxy"):
            self.assertEqual(estimate_strength(password), "weak")

    def test_invalid_types(self):
        for value in (None, 123, True, [], b"fictional"):
            with self.assertRaises(TypeError):
                estimate_strength(value)


class VaultToolsTests(unittest.TestCase):
    def test_two_and_three_matches(self):
        self.assertEqual(find_duplicate_passwords(make_vault("fake-a", "fake-a")),
                         [["0", "1"]])
        self.assertEqual(find_duplicate_passwords(make_vault("fake-a", "fake-a", "fake-a")),
                         [["0", "1", "2"]])

    def test_multiple_groups_first_occurrence_order(self):
        vault = make_vault("fake-a", "fake-b", "fake-b", "fake-a", "fake-c", "fake-b")
        self.assertEqual(find_duplicate_passwords(vault), [["0", "3"], ["1", "2", "5"]])

    def test_unique_and_empty(self):
        self.assertEqual(find_duplicate_passwords(make_vault("fake-a", "fake-b")), [])
        self.assertEqual(find_duplicate_passwords(Vault()), [])

    def test_unicode_case_and_spaces_exact(self):
        vault = make_vault("É雪", "é雪", "e\u0301雪", "É雪", "É雪 ")
        self.assertEqual(find_duplicate_passwords(vault), [["0", "3"]])

    def test_empty_statistics(self):
        self.assertEqual(security_statistics(Vault()),
                         dict(total=0, weak=0, moderate=0, strong=0, reused=0))

    def test_mixed_statistics(self):
        vault = make_vault("fake", "fake", "Raven372", "Raven372!xyzt",
                           "Raven372!xyzt", "Raven372!xyzt")
        counts = security_statistics(vault)
        self.assertEqual(counts, dict(total=6, weak=2, moderate=1, strong=3, reused=5))
        self.assertEqual(sum(counts[key] for key in ("weak", "moderate", "strong")),
                         counts["total"])

    def test_no_mutation_and_independent_results(self):
        vault = make_vault("fake-a", "fake-a", "Raven372!xyzt")
        before = copy.deepcopy(vault)
        original_list = vault.credentials
        find_duplicate_passwords(vault)[0].clear()
        security_statistics(vault)
        self.assertEqual(vault, before)
        self.assertIs(vault.credentials, original_list)
        self.assertEqual(find_duplicate_passwords(vault), [["0", "1"]])

    def test_invalid_vaults(self):
        invalid = make_vault("fake-a")
        invalid.credentials.append(invalid.credentials[0])
        for function in (find_duplicate_passwords, security_statistics):
            for value in (None, [], "vault"):
                with self.assertRaises(TypeError):
                    function(value)
            with self.assertRaises(ValueError):
                function(invalid)

    def test_no_output_logging_or_file_access(self):
        vault = make_vault("fictional-secret", "fictional-secret")
        output = io.StringIO()
        # These pure operations must not access files, even to save plaintext.
        with patch("builtins.open", side_effect=AssertionError("unexpected file access")), \
                patch("io.open", side_effect=AssertionError("unexpected file access")), \
                patch.object(logging.Logger, "_log") as log, \
                contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            generated = generate_password()
            estimate_strength(generated)
            find_duplicate_passwords(vault)
            security_statistics(vault)
        log.assert_not_called()
        self.assertEqual(output.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
