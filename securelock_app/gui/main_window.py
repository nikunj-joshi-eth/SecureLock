"""Tkinter desktop UI. Importing this module never opens a window."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

from .controller import AppError, VaultController
from ..password_tools import estimate_strength, generate_password


# Shared visual tokens; security and persistence live in the controller.
BACKGROUND = "#141c29"
SIDEBAR = "#1b2636"
PANEL = "#233044"
BORDER = "#39485c"
ACCENT = "#3d70ad"
ACTIVE = "#2c4c72"
HOVER = "#35465c"
ACCENT_HOVER = "#4b7eb8"
DISABLED = "#252e3b"
DISABLED_TEXT = "#718096"
DANGER = "#49323b"
DANGER_HOVER = "#62404a"
TEXT = "#e8edf4"
MUTED = "#a4b2c5"
SUCCESS = "#94bda6"
ERROR = "#d99b9b"
FONT = "Segoe UI"
SPACE = 8
PAGE_PAD = SPACE * 3
DEFAULT_VAULT = Path(__file__).resolve().parents[2] / "data" / "securelock.vault"


class SecureLockApp:
    """One root window; navigation destroys the previous page's secret widgets."""

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.secret_variables = []
        self.dialog = None
        root.title("SecureLock • Personal Security")
        root.geometry("1180x720")
        root.minsize(1000, 680)
        root.configure(background=BACKGROUND)
        root.protocol("WM_DELETE_WINDOW", self.close)
        # Avoid Tk's default terminal tracebacks with unlocked data in scope.
        root.report_callback_exception = self.callback_error
        self.style()
        self.show_login()

    def style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure(".", background=BACKGROUND, foreground=TEXT, font=(FONT, 10))
        style.configure("TFrame", background=BACKGROUND)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Sidebar.TFrame", background=SIDEBAR)
        style.configure("Sidebar.TLabel", background=SIDEBAR, foreground=MUTED,
                        font=(FONT, 9))
        style.configure("Danger.TButton", background=DANGER, foreground=ERROR)
        style.map("Danger.TButton", background=[("active", DANGER_HOVER)])
        style.configure("TSeparator", background=BORDER)
        style.configure("TLabel", padding=(0, 4))
        style.configure("Muted.TLabel", foreground=MUTED)
        style.configure("Title.TLabel", font=(FONT, 24, "bold"))
        style.configure("Heading.TLabel", font=(FONT, 16, "bold"))
        style.configure("Panel.TLabel", background=PANEL)
        style.configure("Number.TLabel", font=(FONT, 28, "bold"), foreground=TEXT, background=PANEL)
        style.configure("TButton", background=PANEL, padding=(16, 10), borderwidth=0)
        style.map("TButton", background=[("disabled", DISABLED), ("active", HOVER)],
                  foreground=[("disabled", DISABLED_TEXT)])
        style.configure("Active.TButton", background=ACTIVE, foreground=TEXT, anchor="w")
        style.configure("Nav.TButton", background=SIDEBAR, anchor="w", padding=(14, 12))
        style.configure("Active.TButton", padding=(14, 12))
        style.map("Active.TButton", background=[("active", ACTIVE)])
        style.configure("Brand.TLabel", background=SIDEBAR, foreground=TEXT,
                        font=(FONT, 18, "bold"))
        style.configure("Caption.TLabel", background=PANEL, foreground=MUTED,
                        font=(FONT, 10))
        style.configure("TCombobox", fieldbackground=PANEL, foreground=TEXT, padding=8)
        style.map("TCombobox", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXT)])
        style.configure("Accent.TButton", background=ACCENT)
        style.map("Accent.TButton", background=[("disabled", DISABLED), ("active", ACCENT_HOVER)])
        style.configure("TEntry", fieldbackground=PANEL, foreground=TEXT, insertcolor=TEXT,
                        padding=9, bordercolor=BORDER, lightcolor=BORDER, darkcolor=BORDER)
        style.map("TEntry", bordercolor=[("focus", ACCENT)])
        style.map("TEntry", fieldbackground=[("readonly", PANEL)], foreground=[("readonly", TEXT)])
        style.configure("TSpinbox", fieldbackground=PANEL, foreground=TEXT,
                        insertcolor=TEXT, padding=8, arrowcolor=TEXT)
        style.configure("TCheckbutton", padding=8)
        style.map("TCheckbutton", background=[("active", BACKGROUND)])
        style.configure("Panel.TCheckbutton", background=PANEL)
        style.map("Panel.TCheckbutton", background=[("active", PANEL)])
        self.root.option_add("*TCombobox*Listbox.background", PANEL)
        self.root.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox.selectBackground", ACTIVE)
        self.root.option_add("*TCombobox*Listbox.selectForeground", TEXT)
        style.configure("Treeview", background=PANEL, fieldbackground=PANEL,
                        foreground=TEXT, rowheight=38, borderwidth=0)
        style.configure("Treeview.Heading", background=SIDEBAR, foreground=TEXT,
                        padding=10, font=(FONT, 11, "bold"))
        style.map("Treeview", background=[("selected", ACTIVE)], foreground=[("selected", TEXT)])

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

    def button(self, parent, text, command, accent=False, danger=False):
        button = ttk.Button(parent, text=text, command=command,
                            style="Danger.TButton" if danger else ("Accent.TButton" if accent else "TButton"))
        button.pack(side="left", padx=(0, 10), pady=8)
        return button

    def show_login(self):
        self.clear_page()
        card = ttk.Frame(self.root, padding=32, style="Panel.TFrame")
        card.place(relx=.5, rely=.5, anchor="center", width=520)
        ttk.Label(card, text="SecureLock", style="Panel.TLabel", font=(FONT, 24, "bold")).pack(anchor="w")
        try:
            setup = not self.controller.vault_exists()
        except AppError as error:
            ttk.Label(card, text=str(error), style="Panel.TLabel", foreground=ERROR, wraplength=420).pack(pady=20)
            ttk.Button(card, text="Retry", command=self.show_login).pack(anchor="w")
            return
        ttk.Label(card, text="Create your encrypted vault" if setup else "Welcome back. Unlock your vault.",
                  style="Panel.TLabel", font=(FONT, 14, "bold")).pack(anchor="w", pady=(8, 20))
        password = self.secret()
        confirmation = self.secret()
        ttk.Label(card, text="Master password", style="Panel.TLabel").pack(anchor="w")
        entry = ttk.Entry(card, textvariable=password, show="•")
        entry.pack(fill="x", pady=(0, 12))
        if setup:
            ttk.Label(card, text="Confirm master password", style="Panel.TLabel").pack(anchor="w")
            ttk.Entry(card, textvariable=confirmation, show="•").pack(fill="x")
            ttk.Label(card, text="At least 8 characters. Prefer a long, unique passphrase.",
                      style="Caption.TLabel", wraplength=420).pack(anchor="w", pady=10)
        feedback = ttk.Label(card, text="", style="Panel.TLabel", wraplength=420, foreground=ERROR)
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
                  style="Caption.TLabel").pack(pady=(20, 0))
        entry.focus_set()

    def shell(self, title, subtitle):
        if self.controller.session is None:
            self.show_login()
            return None
        self.clear_page()
        sidebar = ttk.Frame(self.root, padding=(18, 24), width=232, style="Sidebar.TFrame")
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Label(sidebar, text="SecureLock", style="Brand.TLabel").pack(anchor="w", pady=(6, 0))
        ttk.Label(sidebar, text="PERSONAL SECURITY", style="Sidebar.TLabel").pack(anchor="w", pady=(0, 28))
        for text, command in (("Dashboard", self.dashboard), ("Credential Vault", self.vault_page),
                              ("Password Generator", self.generator_page),
                              ("About & Credits", self.about_page)):
            ttk.Button(sidebar, text=text, command=command,
                       style="Active.TButton" if (text == title or
                       (text == "Dashboard" and title == "Welcome to SecureLock"))
                       else "Nav.TButton", takefocus=True).pack(fill="x", pady=4)
        ttk.Button(sidebar, text="Lock Vault", command=self.lock).pack(side="bottom", fill="x", pady=(16, 0))
        ttk.Label(sidebar, text="LOCAL ENCRYPTED VAULT", style="Sidebar.TLabel").pack(side="bottom", anchor="w", pady=(16, 0))
        ttk.Separator(sidebar).pack(side="bottom", fill="x", pady=(24, 0))
        body = ttk.Frame(self.root, padding=PAGE_PAD)
        body.pack(side="left", fill="both", expand=True)
        ttk.Label(body, text=title, style="Title.TLabel").pack(anchor="w")
        ttk.Label(body, text=subtitle, style="Muted.TLabel", wraplength=650).pack(anchor="w", pady=(4, 16))
        body.bind("<Configure>", lambda event: self.wrap_labels(body, event.width))
        return body

    @staticmethod
    def wrap_labels(body, width):
        """Keep descriptive text inside the available page width on resize."""
        for child in body.winfo_children():
            if isinstance(child, ttk.Label) and child.cget("wraplength"):
                child.configure(wraplength=max(200, width - 60))

    def about_page(self):
        if self.controller.session is None:
            self.show_login()
            return
        body = self.shell("About & Credits", "SecureLock — Personal Digital Security Management System")
        ttk.Label(body, padding=0, text="Python Programming — Project-Based Learning (PBL)",
                  style="Heading.TLabel", wraplength=600).pack(anchor="w")
        ttk.Label(body, padding=0, text="Development Build", style="Muted.TLabel").pack(anchor="w", pady=(0, 8))
        ttk.Label(body, padding=0, text="A desktop application for managing personal credentials in a local encrypted vault, "
                  "generating passwords and reviewing password strength.",
                  wraplength=600).pack(anchor="w", pady=(0, 12))
        credits = ttk.Frame(body, padding=(18, 10), style="Panel.TFrame")
        credits.pack(fill="x")
        ttk.Label(credits, padding=0, text="Developed By", style="Panel.TLabel",
                  font=(FONT, 13, "bold")).pack(anchor="w")
        for member in ("1. Nikunj Joshi — 25/SET/BCSE/137", "2. Khushi — 25/SET/BCSE/148",
                       "3. Mansi — 25/SET/BCSE/131", "4. Sumit Kumar — 25/SET/BCSE/145"):
            ttk.Label(credits, padding=0, text=member, style="Panel.TLabel").pack(anchor="w", pady=3)
        academic = ttk.Frame(body, padding=(18, 12), style="Panel.TFrame")
        academic.pack(fill="x", pady=(12, 0))
        ttk.Label(academic, padding=0, text="Academic Details", style="Panel.TLabel", font=(FONT, 13, "bold")).pack(anchor="w", pady=(8, 0))
        ttk.Label(academic, padding=0, text="Programme: B.Tech Computer Science and Engineering\n"
                  "Subject: Python Programming\n"
                  "Subject Code: 5.0CE202E02H\n"
                  "Under the Guidance of:\nDr. Rosy Madan (Professor)",
                  wraplength=600, justify="left", style="Panel.TLabel").pack(anchor="w")
        ttk.Label(body, padding=0, text="Developed as part of the Python Programming PBL.",
                  style="Muted.TLabel", wraplength=600).pack(anchor="w", pady=(8, 0))

    def dashboard(self):
        body = self.shell("Welcome to SecureLock", "Your personal security overview")
        if body is None:
            return
        stats = self.controller.statistics()
        cards = ttk.Frame(body)
        cards.pack(fill="x", pady=(0, 8))
        for index, (key, label) in enumerate((("total", "Saved credentials"), ("strong", "Strong passwords"),
                                               ("weak", "Weak passwords"), ("reused", "Reused passwords"))):
            cards.columnconfigure(index % 2, weight=1, uniform="statistics")
            card = ttk.Frame(cards, padding=(20, 12), style="Panel.TFrame")
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=(0, SPACE) if index % 2 == 0 else (SPACE, 0), pady=SPACE)
            ttk.Label(card, text=str(stats[key]), style="Number.TLabel").pack(anchor="w")
            ttk.Label(card, text=label, style="Panel.TLabel").pack(anchor="w")
        ttk.Label(body, text="Security recommendations", style="Heading.TLabel").pack(anchor="w", pady=(12, 4))
        recommendations = ttk.Frame(body, padding=(16, 10), style="Panel.TFrame")
        recommendations.pack(fill="x", pady=(4, 12))
        recommendations.bind("<Configure>", lambda event:
                             self.wrap_labels(recommendations, event.width))
        for recommendation in self.controller.recommendations():
            label = ttk.Label(recommendations, text=recommendation, wraplength=650,
                              style="Caption.TLabel")
            label.pack(anchor="w", fill="x")
        actions = ttk.Frame(body)
        actions.pack(anchor="w")
        self.button(actions, "Open vault", self.vault_page, True)
        self.button(actions, "Generate password", self.generator_page)

    def vault_page(self):
        body = self.shell("Credential Vault", "Passwords stay hidden. Select a record to edit, delete or reveal it.")
        if body is None:
            return
        toolbar = ttk.Frame(body, padding=(12, 4), style="Panel.TFrame")
        toolbar.pack(fill="x")
        search = ttk.Frame(toolbar, style="Panel.TFrame")
        search.pack(fill="x")
        self.query = tk.StringVar(self.root)
        ttk.Label(search, text="Find website", style="Panel.TLabel").pack(side="left", padx=(0, 10))
        entry = ttk.Entry(search, textvariable=self.query)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.button(search, "Clear", self.clear_search)
        self.button(search, "Reset", self.reset_filters)
        filters = ttk.Frame(toolbar, style="Panel.TFrame")
        filters.pack(fill="x", pady=(8, 0))
        ttk.Label(filters, text="Show", style="Panel.TLabel").pack(side="left", padx=(0, 10))
        self.strength_filter = tk.StringVar(self.root, value="All")
        choice = ttk.Combobox(filters, textvariable=self.strength_filter, state="readonly",
                              values=("All", "Weak", "Moderate", "Strong", "Reused"), width=14)
        choice.pack(side="left")
        self.alphabetical = tk.BooleanVar(self.root, value=True)
        ttk.Checkbutton(filters, text="Website A–Z", style="Panel.TCheckbutton", variable=self.alphabetical,
                        command=self.refresh_table).pack(side="left", padx=12)
        choice.bind("<<ComboboxSelected>>", lambda event: self.refresh_table())
        self.query.trace_add("write", lambda *_: self.refresh_table())
        entry.bind("<Return>", lambda event: self.refresh_table())
        table = ttk.Frame(body)
        table.pack(fill="both", expand=True, pady=16)
        table.rowconfigure(0, weight=1)
        table.columnconfigure(0, weight=1)
        self.tree = ttk.Treeview(table, height=5, columns=("website", "username", "strength"), show="headings", selectmode="browse")
        for name, title, width in (("website", "Website / Service", 230), ("username", "Username", 200),
                                   ("strength", "Strength", 100)):
            self.tree.heading(name, text=title)
            self.tree.column(name, width=width, minwidth=80)
        scroll = ttk.Scrollbar(table, orient="vertical", command=self.tree.yview)
        horizontal = ttk.Scrollbar(table, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scroll.set, xscrollcommand=horizontal.set)
        scroll.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", lambda event: self.hide_revealed())
        actions = ttk.Frame(body)
        actions.pack(anchor="w")
        self.button(actions, "Add", self.credential_form, True)
        self.button(actions, "Edit", self.edit_selected)
        self.button(actions, "Delete", self.delete_selected, danger=True)
        self.button(actions, "Reveal / Hide", self.toggle_revealed)
        self.revealed = self.secret()
        self.reveal_entry = ttk.Entry(body, textvariable=self.revealed, show="•", state="readonly")
        self.reveal_entry.pack(fill="x", pady=8)
        self.feedback = ttk.Label(body, text="", style="Muted.TLabel", wraplength=650)
        self.feedback.pack(anchor="w")
        self.refresh_table()

    def reset_filters(self):
        self.strength_filter.set("All")
        self.alphabetical.set(True)
        self.clear_search()

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
        records = self.controller.filtered_records(
            self.query.get(), self.strength_filter.get(), self.alphabetical.get())
        for record in records:
            self.tree.insert("", "end", iid=record.id,
                             values=(record.website, record.username, estimate_strength(record.password)))
        self.feedback.configure(foreground=MUTED, text=(f"{len(records)} credentials shown" if records else
                                      "No credentials match. Clear or reset filters, or add your first credential."))

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
            self.feedback.configure(text="Credential deleted and saved.", foreground=SUCCESS)

    def credential_form(self, record=None, initial_password=""):
        if self.dialog is not None:
            self.dialog.lift()
            return
        self.hide_revealed()
        dialog = tk.Toplevel(self.root)
        self.dialog = dialog
        dialog.title("Edit credential" if record else "Add credential")
        dialog.configure(background=BACKGROUND)
        dialog.geometry("560x620")
        dialog.minsize(520, 620)
        dialog.transient(self.root)
        dialog.grab_set()
        form = ttk.Frame(dialog, padding=PAGE_PAD)
        form.pack(fill="both", expand=True)
        ttk.Label(form, text="Edit credential" if record else "Add credential",
                  style="Heading.TLabel").pack(anchor="w", pady=(0, 14))
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
        strength = ttk.Label(form, style="Muted.TLabel")
        strength.pack(anchor="w")
        def update_strength(*_):
            rating = estimate_strength(password.get())
            strength.configure(text=f"Estimated strength: {rating.title()}",
                               foreground=self.strength_color(rating))
        password.trace_add("write", update_strength)
        update_strength()
        ttk.Button(form, text="Generate Password", command=lambda: self.generate_into_form(
            password, entries[2], visible)).pack(anchor="w", pady=8)
        feedback = ttk.Label(form, text="", wraplength=420, foreground=ERROR)
        feedback.pack(fill="x")

        def dismiss():
            for variable in variables:
                variable.set("")
                if variable in self.secret_variables:
                    self.secret_variables.remove(variable)
            dialog.destroy()
            self.dialog = None

        def save():
            for label, variable, entry in zip(("Website / Service", "Username", "Password"), variables, entries):
                if not variable.get().strip():
                    feedback.configure(text=f"{label} is required. Enter non-space content.")
                    entries[2].configure(show="•")
                    visible.set(False)
                    entry.focus_set()
                    return
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
                self.feedback.configure(text="Credential saved successfully.", foreground=SUCCESS)

        actions = ttk.Frame(form)
        actions.pack(anchor="e", pady=8)
        self.button(actions, "Save credential", save, True)
        self.button(actions, "Cancel", dismiss)
        dialog.protocol("WM_DELETE_WINDOW", dismiss)
        dialog.bind("<Escape>", lambda event: dismiss())
        dialog.bind("<Return>", lambda event: save())
        entries[0].focus_set()

    @staticmethod
    def strength_color(rating):
        return {"strong": SUCCESS, "moderate": MUTED, "weak": ERROR}.get(rating, MUTED)

    @staticmethod
    def generate_into_form(password, entry, visible):
        """Fill the existing form using the shared generator; remask every result."""
        password.set(generate_password())
        visible.set(False)
        entry.configure(show="•")

    def generator_page(self):
        body = self.shell("Password Generator", "Create a unique password locally. Nothing is copied to your clipboard.")
        if body is None:
            return
        panel = ttk.Frame(body, padding=24, style="Panel.TFrame")
        panel.pack(fill="x", pady=(0, 16))
        ttk.Label(panel, text="Create a unique password", style="Panel.TLabel",
                  font=(FONT, 16, "bold")).pack(anchor="w")
        panel.bind("<Configure>", lambda event: self.wrap_labels(panel, event.width))
        ttk.Label(panel, text="Adjust length below. Generated values remain hidden until you choose to show them.",
                  style="Caption.TLabel", wraplength=580).pack(anchor="w")
        controls = ttk.Frame(body, padding=20, style="Panel.TFrame")
        controls.pack(fill="x")
        ttk.Label(controls, text="Password length (8–128)", style="Panel.TLabel").pack(anchor="w")
        length = tk.StringVar(self.root, value="16")
        ttk.Spinbox(controls, from_=8, to=128, textvariable=length, width=10).pack(anchor="w", pady=8)
        symbols = tk.BooleanVar(self.root, value=True)
        ttk.Checkbutton(controls, text="Include symbols", style="Panel.TCheckbutton", variable=symbols).pack(anchor="w")
        self.generated = self.secret()
        display = ttk.Entry(controls, textvariable=self.generated, show="•", state="readonly")
        display.pack(fill="x", pady=(24, 8))
        visible = tk.BooleanVar(self.root, value=False)
        ttk.Checkbutton(controls, text="Show generated password", style="Panel.TCheckbutton", variable=visible,
                        command=lambda: display.configure(show="" if visible.get() else "•")).pack(anchor="w")
        strength = ttk.Label(controls, text="Generate a password to begin.", style="Caption.TLabel")
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
            strength.configure(text=f"Estimated strength: {estimate_strength(password).title()}",
                               foreground=self.strength_color(estimate_strength(password)))
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
