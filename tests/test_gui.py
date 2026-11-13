"""Display-free GUI coordination tests; only fictional temporary vaults."""

import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch

from securelock_app.gui.controller import AppError, VaultController
from securelock_app.gui.main_window import DEFAULT_VAULT, SecureLockApp


MASTER = "fictional master phrase"


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / "data" / "fictional.vault"
        self.app = VaultController(self.path)

    def setup_vault(self):
        self.app.setup(MASTER, MASTER)

    def test_setup_confirmation_and_policy(self):
        self.assertFalse(self.app.vault_exists())
        for password, confirmation in ((MASTER, "different"), ("short", "short"), ("        ", "        ")):
            with self.assertRaises(AppError):
                self.app.setup(password, confirmation)
            self.assertIsNone(self.app.session)
            self.assertFalse(self.path.exists())
        self.setup_vault()
        self.assertTrue(self.app.vault_exists())

    def test_existing_setup_never_overwrites(self):
        self.setup_vault()
        before = self.path.read_bytes()
        with self.assertRaises(AppError):
            VaultController(self.path).setup(MASTER, MASTER)
        self.assertEqual(self.path.read_bytes(), before)

    def test_crud_search_statistics_and_restart(self):
        self.setup_vault()
        first = self.app.add("fictional.example", "fake-user", "weak")
        second = self.app.add("other.example", "fake-user", "weak")
        self.assertEqual(self.app.statistics()["reused"], 2)
        self.assertEqual(self.app.records("FICTIONAL"), [first])
        self.app.update(first.id, "changed.example", "new-user", "Raven372!xyzt")
        self.app.delete(second.id)
        self.app.lock()
        self.assertIsNone(self.app.session)
        reopened = VaultController(self.path)
        reopened.login(MASTER)
        self.assertEqual(reopened.records()[0].website, "changed.example")
        self.assertEqual(reopened.statistics(), dict(total=1, weak=0, moderate=0, strong=1, reused=0))
        encrypted = self.path.read_bytes()
        for value in (MASTER, "Raven372!xyzt", "changed.example", "new-user"):
            self.assertNotIn(value.encode(), encrypted)

    def test_display_filters_sort_and_preserve_storage_order(self):
        self.setup_vault()
        weak = self.app.add("zeta", "user", "tiny")
        strong = self.app.add("Alpha", "user", "Raven372!xyzt")
        moderate = self.app.add("beta", "user", "Abc492xy")
        duplicate = self.app.add("Gamma", "user", "tiny")
        original = self.app.records()
        self.assertEqual(self.app.filtered_records(), [strong, moderate, duplicate, weak])
        self.assertEqual(self.app.filtered_records(" ALP "), [strong])
        self.assertEqual(self.app.filtered_records("no match"), [])
        self.assertEqual(self.app.filtered_records(strength="Weak"), [duplicate, weak])
        self.assertEqual(self.app.filtered_records(strength="Moderate"), [moderate])
        self.assertEqual(self.app.filtered_records(strength="Strong"), [strong])
        self.assertEqual(self.app.filtered_records(strength="Reused"), [duplicate, weak])
        self.assertEqual(self.app.filtered_records("z", "Reused"), [weak])
        self.assertEqual(self.app.filtered_records(alphabetical=False), original)
        self.assertEqual(self.app.records(), original)
        self.app.lock()
        self.app.login(MASTER)
        self.assertEqual(self.app.records(), original)

    def test_recommendations_follow_statistics(self):
        self.setup_vault()
        self.assertIn("first credential", " ".join(self.app.recommendations()))
        first = self.app.add("one", "user", "tiny")
        second = self.app.add("two", "user", "tiny")
        messages = " ".join(self.app.recommendations())
        self.assertIn("2 weak", messages)
        self.assertIn("2 credentials with reused", messages)
        self.app.update(first.id, "one", "user", "Raven372!xyzt")
        self.app.delete(second.id)
        messages = " ".join(self.app.recommendations())
        self.assertIn("Good progress", messages)
        self.assertIn("estimate", messages)
        self.app.add("three", "user", "Abc492xy")
        self.assertIn("1 moderate", " ".join(self.app.recommendations()))

    def test_three_wrong_attempts_block_even_correct_password(self):
        self.setup_vault()
        self.app.lock()
        for attempt in range(3):
            with self.assertRaises(AppError):
                self.app.login("fictional incorrect phrase")
            self.assertEqual(self.app.failed_attempts, attempt + 1)
            self.assertIsNone(self.app.session)
        with patch("securelock_app.gui.controller.authentication.unlock_vault") as unlock:
            with self.assertRaises(AppError):
                self.app.login(MASTER)
            unlock.assert_not_called()
        fresh = VaultController(self.path)
        fresh.login(MASTER)
        self.assertIsNotNone(fresh.session)

    def test_success_resets_attempt_count_and_lock_requires_login(self):
        self.setup_vault()
        self.app.lock()
        with self.assertRaises(AppError):
            self.app.login("fictional wrong")
        self.app.login(MASTER)
        self.assertEqual(self.app.failed_attempts, 0)
        self.app.lock()
        for operation in (self.app.records, self.app.statistics,
                          lambda: self.app.add("fake", "fake", "fake")):
            with self.assertRaises(AppError):
                operation()

    def test_save_failures_restore_add_edit_delete(self):
        self.setup_vault()
        record = self.app.add("fake.example", "fake-user", "fake-secret")
        before = self.app.records()
        disk = self.path.read_bytes()
        original_list = self.app.session.vault.credentials
        operations = (lambda: self.app.add("new.example", "fake", "new-secret"),
                      lambda: self.app.update(record.id, "changed", "changed", "changed"),
                      lambda: self.app.delete(record.id))
        with patch("securelock_app.gui.controller.authentication.save_vault", side_effect=OSError("sensitive detail")):
            for operation in operations:
                with self.assertRaises(AppError) as caught:
                    operation()
                self.assertIn("undone", str(caught.exception))
                self.assertNotIn("sensitive detail", str(caught.exception))
                self.assertEqual(self.app.records(), before)
                self.assertIs(self.app.session.vault.credentials, original_list)
                self.assertEqual(self.path.read_bytes(), disk)

    def test_missing_file_is_not_recreated_on_save(self):
        self.setup_vault()
        self.path.unlink()
        with self.assertRaises(AppError):
            self.app.add("fake", "fake", "fake")
        self.assertFalse(self.path.exists())
        self.assertEqual(self.app.records(), [])

    def test_corrupt_missing_and_inaccessible_login(self):
        self.setup_vault()
        self.app.lock()
        self.path.write_bytes(b"fictional corrupt vault")
        with self.assertRaisesRegex(AppError, "damaged"):
            self.app.login(MASTER)
        self.assertIsNone(self.app.session)
        self.path.unlink()
        with self.assertRaisesRegex(AppError, "missing"):
            self.app.login(MASTER)
        with patch("securelock_app.gui.controller.authentication.unlock_vault", side_effect=PermissionError("private")):
            with self.assertRaisesRegex(AppError, "permissions"):
                self.app.login(MASTER)
        with patch.object(Path, "lstat", side_effect=PermissionError("private")):
            with self.assertRaises(AppError):
                self.app.vault_exists()

    def test_invalid_change_and_no_terminal_output(self):
        self.setup_vault()
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            with self.assertRaises(AppError):
                self.app.add("", "fake", "fictional secret")
        self.assertEqual(output.getvalue(), "")
        self.assertEqual(self.app.records(), [])

    def test_missing_record_reports_selection_error_without_saving(self):
        self.setup_vault()
        before = self.path.read_bytes()
        with patch("securelock_app.gui.controller.authentication.save_vault") as save:
            for operation in (lambda: self.app.delete("missing"),
                              lambda: self.app.update("missing", "fake", "fake", "fake")):
                with self.assertRaisesRegex(AppError, "no longer available"):
                    operation()
            save.assert_not_called()
        self.assertEqual(self.app.records(), [])
        self.assertEqual(self.path.read_bytes(), before)


class ViewCoordinationTests(unittest.TestCase):
    def test_typing_search_refreshes_without_submit_and_reset_restores_defaults(self):
        app = SecureLockApp.__new__(SecureLockApp)
        app.root = Mock()
        app.shell = Mock()
        app.secret = Mock()
        app.button = Mock()
        app.refresh_table = Mock()
        with patch("securelock_app.gui.main_window.tk.StringVar", side_effect=[Mock(), Mock()]), \
                patch("securelock_app.gui.main_window.tk.BooleanVar"), \
                patch("securelock_app.gui.main_window.ttk.Frame"), \
                patch("securelock_app.gui.main_window.ttk.Label"), \
                patch("securelock_app.gui.main_window.ttk.Entry"), \
                patch("securelock_app.gui.main_window.ttk.Combobox"), \
                patch("securelock_app.gui.main_window.ttk.Checkbutton"), \
                patch("securelock_app.gui.main_window.ttk.Treeview"), \
                patch("securelock_app.gui.main_window.ttk.Scrollbar"):
            app.vault_page()
        app.refresh_table.reset_mock()
        # Exercise the write callback registered on the actual query widget variable.
        mode, callback = app.query.trace_add.call_args.args
        self.assertEqual(mode, "write")
        callback("query", "", "write")
        app.refresh_table.assert_called_once_with()
        app.strength_filter.set("Weak")
        app.alphabetical.set(False)
        app.reset_filters()
        app.query.set.assert_called_once_with("")
        app.strength_filter.set.assert_called_with("All")
        app.alphabetical.set.assert_called_with(True)

    def test_all_session_pages_redirect_when_locked(self):
        app = SecureLockApp.__new__(SecureLockApp)
        app.controller = Mock(session=None)
        app.show_login = Mock()
        app.clear_page = Mock()
        with patch("securelock_app.gui.main_window.ttk.Frame") as frame:
            for page in (app.dashboard, app.vault_page, app.generator_page, app.about_page):
                with self.subTest(page=page.__name__):
                    app.show_login.reset_mock()
                    page()
                    app.show_login.assert_called_once_with()
            frame.assert_not_called()
        app.clear_page.assert_not_called()

    def test_about_content_and_unlocked_navigation(self):
        app = SecureLockApp.__new__(SecureLockApp)
        app.root = Mock()
        app.controller = Mock()
        app.clear_page = Mock()
        with patch("securelock_app.gui.main_window.ttk.Frame"), \
                patch("securelock_app.gui.main_window.ttk.Label") as label, \
                patch("securelock_app.gui.main_window.ttk.Button") as button:
            app.about_page()
            texts = [call.kwargs["text"] for call in label.call_args_list]
            content = "\n".join(texts)
            for expected in (
                "SecureLock — Personal Digital Security Management System",
                "Python Programming — Project-Based Learning (PBL)",
                "1. Nikunj Joshi — 25/SET/BCSE/137",
                "2. Khushi — 25/SET/BCSE/148",
                "3. Mansi — 25/SET/BCSE/131",
                "4. Sumit Kumar — 25/SET/BCSE/145",
                "Programme: B.Tech Computer Science and Engineering",
                "Subject: Python Programming",
                "Subject Code: 5.0CE202E02H",
                "Under the Guidance of:\nDr. Rosy Madan (Professor)",
                "Development Build",
                "Developed as part of the Python Programming PBL.",
            ):
                self.assertIn(expected, content)
            self.assertEqual(
                [(call.kwargs["text"], call.kwargs["command"]) for call in button.call_args_list],
                [("Dashboard", app.dashboard), ("Credential Vault", app.vault_page),
                 ("Password Generator", app.generator_page),
                 ("About & Credits", app.about_page), ("Lock Vault", app.lock)],
            )
            active = [call.kwargs["text"] for call in button.call_args_list
                      if call.kwargs.get("style") == "Active.TButton"]
            self.assertEqual(active, ["About & Credits"])
        app.clear_page.assert_called_once_with()
        app.controller.assert_not_called()

    def test_about_requires_unlock_and_lock_returns_to_login(self):
        app = SecureLockApp.__new__(SecureLockApp)
        app.controller = Mock(session=None)
        app.show_login = Mock()
        app.shell = Mock()
        app.about_page()
        app.shell.assert_not_called()
        app.show_login.assert_called_once_with()
        app.show_login.reset_mock()
        app.lock()
        app.controller.lock.assert_called_once_with()
        app.show_login.assert_called_once_with()

    def test_form_generation_uses_shared_generator_and_remasks(self):
        password, entry, visible = Mock(), Mock(), Mock()
        with patch("securelock_app.gui.main_window.generate_password", return_value="fictional-generated") as generate:
            SecureLockApp.generate_into_form(password, entry, visible)
        generate.assert_called_once_with()
        password.set.assert_called_once_with("fictional-generated")
        visible.set.assert_called_once_with(False)
        entry.configure.assert_called_once_with(show="•")

    def test_default_location_is_project_data(self):
        self.assertEqual(DEFAULT_VAULT.parent, Path(__file__).resolve().parents[1] / "data")

    def test_clear_page_clears_secrets_closes_dialog_and_drops_widgets(self):
        app = SecureLockApp.__new__(SecureLockApp)
        app.root = Mock()
        widget = Mock()
        app.root.winfo_children.return_value = [widget]
        secret = Mock()
        app.secret_variables = [secret]
        dialog = app.dialog = Mock()
        app.clear_page()
        secret.set.assert_called_once_with("")
        dialog.destroy.assert_called_once()
        widget.destroy.assert_called_once()
        self.assertEqual(app.secret_variables, [])
        self.assertIsNone(app.dialog)
        self.assertIsNone(app.generated)
        self.assertIsNone(app.revealed)

    def test_table_only_receives_safe_columns(self):
        from securelock_app.models import Credential
        app = SecureLockApp.__new__(SecureLockApp)
        app.tree = Mock()
        app.tree.get_children.return_value = []
        app.hide_revealed = Mock()
        app.query = Mock()
        app.query.get.return_value = ""
        app.feedback = Mock()
        app.controller = Mock()
        app.strength_filter = Mock()
        app.strength_filter.get.return_value = "All"
        app.alphabetical = Mock()
        app.alphabetical.get.return_value = True
        app.controller.filtered_records.return_value = [Credential("fake-id", "fake.example", "fake-user", "fictional-secret")]
        app.refresh_table()
        app.tree.insert.assert_called_once_with("", "end", iid="fake-id", values=("fake.example", "fake-user", "moderate"))


if __name__ == "__main__":
    unittest.main()
