"""Real CTk widget integration with temporary fictional vaults. Requires a display."""
import tempfile
from pathlib import Path
import tkinter as tk
import unittest
from unittest.mock import patch
import customtkinter as ctk

from securelock_app.gui.controller import VaultController
from securelock_app.gui.main_window import SecureLockApp


def descendants(parent):
    for child in parent.winfo_children():
        yield child
        yield from descendants(child)


class CustomTkinterTests(unittest.TestCase):
    def setUp(self):
        ctk.set_appearance_mode("dark")
        try:
            self.root = ctk.CTk()
        except tk.TclError as error:
            self.skipTest(f"Desktop display unavailable: {error}")
        self.root.withdraw()
        self.addCleanup(self.destroy_root)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.controller = VaultController(Path(self.temp.name) / "test.vault")
        self.app = SecureLockApp(self.root, self.controller)
        # Surface callback errors as failures instead of a blocking native dialog.
        self.root.report_callback_exception = lambda kind, error, trace: (_ for _ in ()).throw(error)

    def destroy_root(self):
        # Cancel CTk's pending DPI/titlebar callbacks before disposing a test root.
        for job in self.root.tk.call("after", "info"):
            self.root.after_cancel(job)
        self.root.destroy()

    def test_vault_actions_fit_minimum_window(self):
        self.unlock()
        for number in range(12):
            self.controller.add(f"fictional-{number}", "user", "tiny")
        self.app.vault_page()
        self.root.geometry("1000x620")
        self.root.deiconify()
        self.root.update()
        for text in ("Show / Hide", "Edit", "Delete", "+ Add credential", "Reset filters"):
            widget = next(w for w in self.widgets(ctk.CTkButton) if w.cget("text") == text)
            self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(), self.root.winfo_rooty() + self.root.winfo_height())
            self.assertLessEqual(widget.winfo_rootx() + widget.winfo_width(), self.root.winfo_rootx() + self.root.winfo_width())

    def widgets(self, kind):
        return [w for w in descendants(self.root) if isinstance(w, kind)]

    def click(self, text):
        next(w for w in self.widgets(ctk.CTkButton) if w.cget("text") == text).invoke()
        self.root.update_idletasks()

    def unlock(self):
        self.controller.setup("fictional master phrase", "fictional master phrase")
        self.app.dashboard()

    def texts(self):
        return "\n".join(w.cget("text") for w in self.widgets(ctk.CTkLabel))

    def test_setup_login_and_three_attempt_limit(self):
        fields = self.widgets(ctk.CTkEntry)
        self.assertEqual(len(fields), 2)
        self.assertTrue(all(w.cget("show") == "•" for w in fields))
        fields[0].insert(0, "fictional master phrase")
        fields[1].insert(0, "different")
        self.click("Create vault  →")
        self.assertIn("do not match", self.texts())
        self.assertFalse(self.controller.path.exists())
        for field in fields:
            field.insert(0, "fictional master phrase")
        self.click("Create vault  →")
        self.assertIsNotNone(self.controller.session)
        self.app.lock()
        for _ in range(3):
            self.widgets(ctk.CTkEntry)[0].insert(0, "wrong")
            self.click("Unlock vault  →")
        self.assertEqual(self.widgets(ctk.CTkEntry)[0].cget("state"), "disabled")

    def test_dashboard_counts_and_about(self):
        self.unlock()
        self.assertIn("No passwords yet", self.texts())
        self.controller.add("fake", "user", "tiny")
        self.controller.add("other", "user", "Raven372!xyzt")
        self.app.dashboard()
        self.assertIn("50% strong", self.texts())
        self.assertIn("1 strong / 2 total", self.texts())
        self.app.about_page()
        for expected in ("Nikunj Joshi", "Khushi", "Mansi", "Sumit Kumar", "5.0CE202E02H", "Dr. Rosy Madan"):
            self.assertIn(expected, self.texts())

    def test_search_filters_reveal_and_cleanup(self):
        self.unlock()
        first = self.controller.add("zeta", "user", "tiny")
        second = self.controller.add("Alpha", "user", "Raven372!xyzt")
        self.app.vault_page()
        self.assertEqual(list(self.app.row_buttons), [second.id, first.id])
        self.app.select_record(first.id)
        self.app.toggle_revealed()
        revealed = self.app.revealed
        self.assertEqual(revealed.get(), "tiny")
        self.app.select_record(second.id)
        self.assertEqual(revealed.get(), "")
        self.app.query.set("ALP")
        self.assertEqual(list(self.app.row_buttons), [second.id])
        self.app.strength_filter.set("Weak")
        self.app.refresh_table()
        self.assertEqual(self.app.row_buttons, {})
        self.assertIn("No credentials found", self.texts())
        self.app.reset_filters()
        self.assertEqual(len(self.app.row_buttons), 2)
        self.app.lock()
        self.assertEqual(revealed.get(), "")
        self.assertIsNone(self.controller.session)

    def test_generator_masking_limits_and_use(self):
        self.unlock()
        self.app.generator_page()
        use = next(w for w in self.widgets(ctk.CTkButton) if w.cget("text") == "Use in Add Credential")
        self.assertEqual(use.cget("state"), "disabled")
        slider = self.widgets(ctk.CTkSlider)[0]
        for length in (8, 128):
            slider.set(length)
            self.click("Generate password")
            self.assertEqual(len(self.app.generated.get()), length)
            self.assertEqual(self.widgets(ctk.CTkEntry)[0].cget("show"), "•")
        show = next(w for w in self.widgets(ctk.CTkSwitch) if w.cget("text") == "Show password")
        show.toggle()
        self.assertEqual(self.widgets(ctk.CTkEntry)[0].cget("show"), "")
        self.click("Generate password")
        value = self.app.generated.get()
        old = self.app.generated
        self.click("Use in Add Credential")
        self.assertEqual(old.get(), "")
        self.assertEqual(self.app.secret_variables[-1].get(), value)
        self.assertEqual(self.widgets(ctk.CTkEntry)[-1].cget("show"), "•")
        self.click("Cancel")
        self.assertIsNone(self.app.dialog)

    def test_form_validation_save_failure_edit_and_delete(self):
        self.unlock()
        self.app.credential_form()
        self.click("Save credential")
        self.assertIn("Website / Service is required", self.texts())
        fields = self.widgets(ctk.CTkEntry)
        for field, value in zip(fields, ("fictional.example", "fake-user", "tiny")):
            field.insert(0, value)
        with patch("securelock_app.gui.controller.authentication.save_vault", side_effect=OSError):
            self.click("Save credential")
        self.assertIsNotNone(self.app.dialog)
        self.assertIn("undone", self.texts())
        self.assertEqual(self.controller.records(), [])
        self.click("Save credential")
        record = self.controller.records()[0]
        self.app.select_record(record.id)
        self.click("Edit")
        self.assertEqual(self.widgets(ctk.CTkEntry)[-1].cget("show"), "•")
        self.click("Generate Password")
        self.click("Save credential")
        self.assertNotEqual(self.controller.records()[0].password, "tiny")
        self.app.select_record(record.id)
        with patch("securelock_app.gui.main_window.messagebox.askyesno", return_value=False):
            self.click("Delete")
        self.assertEqual(len(self.controller.records()), 1)
        with patch("securelock_app.gui.main_window.messagebox.askyesno", return_value=True):
            self.click("Delete")
        self.assertEqual(self.controller.records(), [])
