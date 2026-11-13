"""Tkinter desktop UI. Importing this module never opens a window."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from .controller import AppError, VaultController
from ..password_tools import estimate_strength, generate_password


BACKGROUND = "#171b22"
PANEL = "#222833"
TEXT = "#edf1f7"
MUTED = "#a6b2c4"
DEFAULT_VAULT = Path(__file__).resolve().parents[2] / "data" / "securelock.vault"


class SecureLockApp:
    """One root window; navigation destroys the previous page's secret widgets."""

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.secret_variables = []
        self.dialog = None
        root.title("SecureLock • Personal Security")
        root.geometry("1080x720")
        root.minsize(900, 620)
        root.configure(background=BACKGROUND)
        root.protocol("WM_DELETE_WINDOW", self.close)
        # Avoid Tk's default terminal tracebacks with unlocked data in scope.
        root.report_callback_exception = self.callback_error
        self.style()
        self.show_login()

    def style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BACKGROUND, foreground=TEXT, font=("Segoe UI", 11))
        style.configure("TFrame", background=BACKGROUND)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", padding=(0, 4))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Title.TLabel", font=("Segoe UI", 26, "bold"))
        style.configure("Heading.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Panel.TLabel", background=PANEL)
        style.configure("Number.TLabel", font=("Segoe UI", 28, "bold"), foreground="#78aeff", background=PANEL)
        style.configure("TButton", background=PANEL, padding=(16, 10), borderwidth=0)
        style.map("TButton", background=[("active", "#354255"), ("disabled", "#252a32")],
                  foreground=[("disabled", "#687384")])
        style.configure("Accent.TButton", background="#3478d4")
        style.map("Accent.TButton", background=[("active", "#4389e8")])
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT, padding=9)
        style.map("TEntry", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXT)])
        style.configure("TSpinbox", fieldbackground=PANEL, foreground=TEXT,
                        insertcolor=TEXT, padding=8, arrowcolor=TEXT)
        style.configure("TCheckbutton", padding=8)
        style.map("TCheckbutton", background=[("active", BACKGROUND)])
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=38, borderwidth=0)
        style.configure("Treeview.Heading", background="#2e3745", foreground=TEXT,
                        padding=10, font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[("selected", "#244e80")], foreground=[("selected", "white")])

    def callback_error(self, *_):
        self.lock()
        messagebox.showerror("SecureLock", "An unexpected error occurred. The vault was locked. Restart if the problem continues.", parent=self.root)

    def secret(self, value=""):
        variable = tk.StringVar(self.root, value=value)
        self.secret_variables.append(variable)
        return variable

    def clear_page(self):
        for variable in self.secret_variables:
            variable.set("")
        self.secret_variables.clear()
        if self.dialog is not None:
            self.dialog.destroy()
            self.dialog = None
        for child in self.root.winfo_children():
            child.destroy()
        self.revealed = None
        self.generated = None
        self.tree = None

    def button(self, parent, text, command, accent=False):
        button = ttk.Button(parent, text=text, command=command,
                            style="Accent.TButton" if accent else "TButton")
        button.pack(side="left", padx=(0, 10), pady=8)
        return button

    def show_login(self):
        self.clear_page()
        card = ttk.Frame(self.root, padding=48)
        card.place(relx=.5, rely=.5, anchor="center", width=520)
        ttk.Label(card, text="SecureLock", style="Title.TLabel").pack(anchor="w")
        try:
            setup = not self.controller.vault_exists()
        except AppError as error:
            ttk.Label(card, text=str(error), wraplength=420).pack(pady=20)
            ttk.Button(card, text="Retry", command=self.show_login).pack(anchor="w")
            return
        ttk.Label(card, text="Create your encrypted vault" if setup else "Welcome back. Unlock your vault.",
                  style="Heading.TLabel").pack(anchor="w", pady=(8, 20))
        password = self.secret()
        confirmation = self.secret()
        ttk.Label(card, text="Master password").pack(anchor="w")
        entry = ttk.Entry(card, textvariable=password, show="•")
        entry.pack(fill="x", pady=(0, 12))
        if setup:
            ttk.Label(card, text="Confirm master password").pack(anchor="w")
            ttk.Entry(card, textvariable=confirmation, show="•").pack(fill="x")
            ttk.Label(card, text="At least 8 characters. Prefer a long, unique passphrase.",
                      style="Muted.TLabel", wraplength=420).pack(anchor="w", pady=10)
        feedback = ttk.Label(card, text="", wraplength=420, foreground="#ffb3ad")
        feedback.pack(fill="x", pady=10)

        def submit():
            try:
                if setup:
                    self.controller.setup(password.get(), confirmation.get())
                else:
                    self.controller.login(password.get())
            except AppError as error:
                feedback.configure(text=str(error))
                if self.controller.failed_attempts >= 3:
                    action.state(["disabled"])
                    entry.state(["disabled"])
            else:
                self.dashboard()
            finally:
                password.set("")
                confirmation.set("")

        action = ttk.Button(card, text="Create vault" if setup else "Unlock vault",
                            style="Accent.TButton", command=submit)
        action.pack(fill="x", pady=8)
        for child in card.winfo_children():
            if isinstance(child, ttk.Entry):
                child.bind("<Return>", lambda event: submit())
        ttk.Label(card, text="Local encrypted storage • No cloud account",
                  style="Muted.TLabel").pack(pady=(20, 0))
        entry.focus_set()

    def shell(self, title, subtitle):
        self.clear_page()
        sidebar = ttk.Frame(self.root, padding=22, style="Panel.TFrame")
        sidebar.pack(side="left", fill="y")
        ttk.Label(sidebar, text="SecureLock", style="Heading.TLabel").pack(pady=(6, 28))
        for text, command in (("Dashboard", self.dashboard), ("Credential Vault", self.vault_page),
                              ("Password Generator", self.generator_page)):
            ttk.Button(sidebar, text=text, command=command).pack(fill="x", pady=6)
        ttk.Button(sidebar, text="Lock Vault", command=self.lock).pack(side="bottom", fill="x", pady=12)
        body = ttk.Frame(self.root, padding=30)
        body.pack(side="left", fill="both", expand=True)
        ttk.Label(body, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(body, text=subtitle, style="Muted.TLabel", wraplength=650).pack(anchor="w", pady=(4, 22))
        return body

    def dashboard(self):
        body = self.shell("Welcome to SecureLock", "Your personal security overview")
        stats = self.controller.statistics()
        cards = ttk.Frame(body)
        cards.pack(fill="x", pady=20)
        for index, (key, label) in enumerate((("total", "Saved credentials"), ("strong", "Strong passwords"),
                                               ("weak", "Weak passwords"), ("reused", "Reused passwords"))):
            cards.columnconfigure(index % 2, weight=1)
            card = ttk.Frame(cards, padding=20, style="Panel.TFrame")
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=8, pady=8)
            ttk.Label(card, text=str(stats[key]), style="Number.TLabel").pack(anchor="w")
            ttk.Label(card, text=label, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(body, text="Choose unique passwords for every service.\nStrength ratings are estimates, not security guarantees.",
                  style="Muted.TLabel").pack(anchor="w", pady=20)
        actions = ttk.Frame(body)
        actions.pack(anchor="w")
        self.button(actions, "Open vault", self.vault_page, True)
        self.button(actions, "Generate password", self.generator_page)

    def vault_page(self):
        body = self.shell("Credential Vault", "Passwords stay hidden. Select a record to edit, delete or reveal it.")
        search = ttk.Frame(body)
        search.pack(fill="x")
        self.query = tk.StringVar(self.root)
        entry = ttk.Entry(search, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.button(search, "Search", self.refresh_table)
        self.button(search, "Clear", self.clear_search)
        entry.bind("<Return>", lambda event: self.refresh_table())
        table = ttk.Frame(body)
        table.pack(fill="both", expand=True, pady=16)
        self.tree = ttk.Treeview(table, columns=("website", "username", "strength"), show="headings", selectmode="browse")
        for name, title, width in (("website", "Website / Service", 230), ("username", "Username", 200),
                                   ("strength", "Strength", 100)):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width, minwidth=80)
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda event: self.hide_revealed())
        actions = ttk.Frame(body)
        actions.pack(anchor="w")
        self.button(actions, "Add", self.credential_form, True)
        self.button(actions, "Edit", self.edit_selected)
        self.button(actions, "Delete", self.delete_selected)
        self.button(actions, "Reveal / Hide", self.toggle_revealed)
        self.revealed = self.secret()
        self.reveal_entry = ttk.Entry(body, textvariable=self.revealed, show="•", state="readonly")
        self.reveal_entry.pack(fill="x", pady=8)
        self.feedback = ttk.Label(body, text="", style="Muted.TLabel")
        self.feedback.pack(anchor="w")
        self.refresh_table()

    def clear_search(self):
        self.query.set("")
        self.refresh_table()

    def hide_revealed(self):
        if self.revealed is not None:
            self.revealed.set("")
            self.reveal_entry.configure(show="•")

    def refresh_table(self):
        self.hide_revealed()
        self.tree.delete(*self.tree.get_children())
        records = self.controller.records(self.query.get())
        for record in records:
            self.tree.insert("", "end", iid=record.id,
                             values=(record.website, record.username, estimate_strength(record.password)))
        self.feedback.configure(text=f"{len(records)} credentials shown")

    def selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Select a credential", "Select a row in the vault first.", parent=self.root)
            return None
        return next((record for record in self.controller.records() if record.id == selection[0]), None)

    def toggle_revealed(self):
        if self.revealed.get():
            self.hide_revealed()
            return
        record = self.selected()
        if record is not None:
            self.revealed.set(record.password)
            self.reveal_entry.configure(show="")

    def edit_selected(self):
        record = self.selected()
        if record is not None:
            self.credential_form(record)

    def delete_selected(self):
        self.hide_revealed()
        record = self.selected()
        if record is None or not messagebox.askyesno("Delete credential", "Delete the selected credential? This cannot be undone.", parent=self.root):
            return
        try:
            self.controller.delete(record.id)
        except AppError as error:
            messagebox.showerror("Not saved", str(error), parent=self.root)
        else:
            self.refresh_table()
            self.feedback.configure(text="Credential deleted and saved.")

    def credential_form(self, record=None, initial_password=""):
        if self.dialog is not None:
            self.dialog.lift()
            return
        self.hide_revealed()
        dialog = tk.Toplevel(self.root)
        self.dialog = dialog
        dialog.title("Edit credential" if record else "Add credential")
        dialog.configure(background=BACKGROUND)
        dialog.geometry("500x540")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        form = ttk.Frame(dialog, padding=28)
        form.pack(fill="both", expand=True)
        website = self.secret(record.website if record else "")
        username = self.secret(record.username if record else "")
        password = self.secret(record.password if record else initial_password)
        record_id = record.id if record else None
        variables = (website, username, password)
        entries = []
        for label, variable in zip(("Website / Service", "Username", "Password"), variables):
            ttk.Label(form, text=label).pack(anchor="w")
            entry = ttk.Entry(form, textvariable=variable, show="•" if variable is password else "")
            entry.pack(fill="x", pady=(0, 10))
            entries.append(entry)
        visible = tk.BooleanVar(dialog, value=False)
        ttk.Checkbutton(form, text="Show password", variable=visible,
                        command=lambda: entries[2].configure(show="" if visible.get() else "•")).pack(anchor="w")
        feedback = ttk.Label(form, text="", wraplength=420, foreground="#ffb3ad")
        feedback.pack(fill="x")

        def dismiss():
            for variable in variables:
                variable.set("")
                if variable in self.secret_variables:
                    self.secret_variables.remove(variable)
            dialog.destroy()
            self.dialog = None

        def save():
            try:
                if record_id is None:
                    self.controller.add(website.get(), username.get(), password.get())
                else:
                    self.controller.update(record_id, website.get(), username.get(), password.get())
            except AppError as error:
                feedback.configure(text=str(error))
                entries[2].configure(show="•")
                visible.set(False)
            else:
                dismiss()
                self.vault_page()
                self.feedback.configure(text="Credential saved successfully.")

        actions = ttk.Frame(form)
        actions.pack(anchor="w", pady=8)
        self.button(actions, "Save credential", save, True)
        self.button(actions, "Cancel", dismiss)
        dialog.protocol("WM_DELETE_WINDOW", dismiss)
        dialog.bind("<Escape>", lambda event: dismiss())
        entries[0].focus_set()

    def generator_page(self):
        body = self.shell("Password Generator", "Create a unique password locally. Nothing is copied to your clipboard.")
        ttk.Label(body, text="Password length (8–128)").pack(anchor="w")
        length = tk.StringVar(self.root, value="16")
        ttk.Spinbox(body, from_=8, to=128, textvariable=length, width=10).pack(anchor="w", pady=8)
        symbols = tk.BooleanVar(self.root, value=True)
        ttk.Checkbutton(body, text="Include symbols", variable=symbols).pack(anchor="w")
        self.generated = self.secret()
        display = ttk.Entry(body, textvariable=self.generated, show="•", state="readonly")
        display.pack(fill="x", pady=(24, 8))
        visible = tk.BooleanVar(self.root, value=False)
        ttk.Checkbutton(body, text="Show generated password", variable=visible,
                        command=lambda: display.configure(show="" if visible.get() else "•")).pack(anchor="w")
        strength = ttk.Label(body, text="Generate a password to begin.", style="Muted.TLabel")
        strength.pack(anchor="w", pady=10)

        def generate():
            try:
                password = generate_password(int(length.get()), use_symbols=symbols.get())
            except (ValueError, TypeError):
                messagebox.showerror("Invalid length", "Enter a whole number from 8 to 128.", parent=self.root)
                return
            self.generated.set(password)
            display.configure(show="•")
            visible.set(False)
            strength.configure(text=f"Estimated strength: {estimate_strength(password).title()}")
            use.state(["!disabled"])

        def use_password():
            password = self.generated.get()
            if password:
                self.vault_page()
                self.credential_form(initial_password=password)

        actions = ttk.Frame(body)
        actions.pack(anchor="w", pady=12)
        self.button(actions, "Generate password", generate, True)
        use = self.button(actions, "Use in Add Credential", use_password)
        use.state(["disabled"])

    def lock(self):
        self.controller.lock()
        self.show_login()

    def close(self):
        self.controller.lock()
        self.clear_page()
        self.root.destroy()


def main() -> None:
    """Launch using a project-relative, ignored encrypted vault location."""
    root = tk.Tk()
    SecureLockApp(root, VaultController(DEFAULT_VAULT))
    root.mainloop()
