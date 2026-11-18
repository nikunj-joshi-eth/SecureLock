"""CustomTkinter desktop views; all vault operations stay in VaultController."""

from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from .controller import AppError, VaultController
from .components import (BACKGROUND, SIDEBAR, PANEL, ELEVATED, ACCENT, TEXT,
                         MUTED, SUCCESS, WARNING, ERROR, label, button, entry, card, section)
from ..password_tools import estimate_strength, generate_password

DEFAULT_VAULT = Path(__file__).resolve().parents[2] / "data" / "securelock.vault"


class SecureLockApp:
    """One root and a few page builders. Navigation clears secret variables."""

    def __init__(self, root, controller):
        self.root, self.controller = root, controller
        self.secret_variables = []
        self.dialog = None
        root.title("SecureLock • Personal Security")
        root.geometry("1180x700")
        root.minsize(1000, 620)
        root.configure(fg_color=BACKGROUND)
        root.protocol("WM_DELETE_WINDOW", self.close)
        root.report_callback_exception = self.callback_error
        self.show_login()

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
        self.generated = self.revealed = None
        self.selected_id = None
        self.row_buttons = {}

    def button(self, parent, text, command, accent=False, danger=False):
        widget = button(parent, text, command, accent, danger)
        widget.pack(side="left", padx=(0, 8), pady=8)
        return widget

    def show_login(self):
        self.clear_page()
        # A scrolling outer surface also supports small desktop work areas.
        surface = ctk.CTkScrollableFrame(self.root, fg_color=BACKGROUND, corner_radius=0)
        surface.pack(fill="both", expand=True)
        surface.grid_columnconfigure(0, weight=1)
        label(surface, "SECURELOCK  /  PERSONAL SECURITY", size=12, color=MUTED).grid(row=0, column=0, pady=(35, 22))
        panel = card(surface)
        panel.grid(row=1, column=0, pady=(0, 24))
        panel.grid_columnconfigure(0, minsize=440)
        form = ctk.CTkFrame(panel, fg_color="transparent")
        form.grid(row=0, column=0, padx=32, pady=28, sticky="ew")
        label(form, "S", size=26, bold=True, fg_color=ACCENT, corner_radius=12, width=48, height=48).pack(anchor="w")
        try:
            setup = not self.controller.vault_exists()
        except AppError as error:
            label(form, str(error), color=ERROR, wraplength=370).pack(pady=20)
            button(form, "Retry", self.show_login).pack()
            return
        label(form, "Your security starts here." if setup else "Welcome back.", size=28, bold=True).pack(anchor="w", pady=(20, 4))
        label(form, "Create a local encrypted vault." if setup else "Enter your master password to unlock your vault.", color=MUTED, wraplength=370).pack(anchor="w", pady=(0, 20))
        password, confirmation = self.secret(), self.secret()
        label(form, "Master password").pack(anchor="w")
        password_entry = entry(form, textvariable=password, show="•")
        password_entry.pack(fill="x", pady=(4, 12))
        fields = [password_entry]
        if setup:
            label(form, "Confirm master password").pack(anchor="w")
            confirm = entry(form, textvariable=confirmation, show="•")
            confirm.pack(fill="x", pady=(4, 8))
            fields.append(confirm)
            label(form, "Use 8+ characters. A long, unique passphrase is best.", color=MUTED, wraplength=370).pack(anchor="w")
        feedback = label(form, "", color=ERROR, wraplength=370)
        feedback.pack(fill="x", pady=8)

        def submit():
            try:
                if setup:
                    self.controller.setup(password.get(), confirmation.get())
                else:
                    self.controller.login(password.get())
            except AppError as error:
                feedback.configure(text=str(error))
                if self.controller.failed_attempts >= 3:
                    action.configure(state="disabled")
                    password_entry.configure(state="disabled")
            else:
                self.dashboard()
            finally:
                password.set("")
                confirmation.set("")

        action = button(form, "Create vault  →" if setup else "Unlock vault  →", submit, accent=True)
        action.pack(fill="x", pady=(0, 14))
        label(form, "LOCAL STORAGE  •  AES-256-GCM ENCRYPTION", size=11, color=MUTED).pack()
        for field in fields:
            field.bind("<Return>", lambda event: submit())
        password_entry.focus_set()

    def shell(self, title, subtitle):
        if self.controller.session is None:
            self.show_login()
            return None
        self.clear_page()
        sidebar = ctk.CTkFrame(self.root, width=220, corner_radius=0, fg_color=SIDEBAR)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        label(sidebar, "SecureLock", size=24, bold=True).pack(anchor="w", padx=24, pady=(28, 0))
        label(sidebar, "PERSONAL SECURITY", size=10, color=MUTED).pack(anchor="w", padx=24, pady=(2, 34))
        for icon, text, command in (("▦", "Dashboard", self.dashboard), ("▤", "Credential Vault", self.vault_page),
                                    ("◇", "Password Generator", self.generator_page), ("ⓘ", "About & Credits", self.about_page)):
            active = text == title
            nav = button(sidebar, f"{icon}   {text}", command, anchor="w", width=188)
            nav.configure(fg_color=ELEVATED if active else "transparent", text_color=TEXT if active else MUTED)
            nav.pack(padx=16, pady=4)
        button(sidebar, "Lock Vault", self.lock, width=188).pack(side="bottom", padx=16, pady=20)
        label(sidebar, "●  Local encrypted vault", size=11, color=SUCCESS).pack(side="bottom", padx=20)
        content = ctk.CTkFrame(self.root, fg_color=BACKGROUND, corner_radius=0)
        content.pack(side="left", fill="both", expand=True, padx=26, pady=22)
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, 16))
        label(header, title, size=28, bold=True).pack(anchor="w")
        description = label(header, subtitle, color=MUTED, wraplength=650)
        description.pack(anchor="w", pady=(4, 0))
        header.bind("<Configure>", lambda event: description.configure(wraplength=max(200, event.width - 10)))
        body = (ctk.CTkFrame(content, fg_color=BACKGROUND, corner_radius=0) if title == "Credential Vault"
                else ctk.CTkScrollableFrame(content, fg_color=BACKGROUND, corner_radius=0))
        body.pack(fill="both", expand=True)
        return body

    def dashboard(self):
        body = self.shell("Dashboard", "A clearer view of your passwords. A safer place to start.")
        if body is None:
            return
        stats = self.controller.statistics()
        metrics = ctk.CTkFrame(body, fg_color="transparent")
        metrics.pack(fill="x", pady=(0, 16))
        for i, (icon, key, title, color) in enumerate((("▤", "total", "Credentials", ACCENT), ("✓", "strong", "Strong", SUCCESS),
                                                      ("!", "weak", "Weak", WARNING), ("↻", "reused", "Reused", WARNING))):
            metrics.grid_columnconfigure(i, weight=1, uniform="metric")
            panel = card(metrics)
            panel.grid(row=0, column=i, sticky="nsew", padx=(0, 10) if i < 3 else 0)
            label(panel, icon, size=22, color=color).pack(anchor="w", padx=16, pady=(12, 0))
            label(panel, str(stats[key]), size=28, bold=True).pack(anchor="w", padx=16)
            label(panel, title, color=MUTED).pack(anchor="w", padx=16, pady=(0, 12))
        split = ctk.CTkFrame(body, fg_color="transparent")
        split.pack(fill="x", pady=(0, 16))
        split.grid_columnconfigure(0, weight=1, uniform="overview")
        split.grid_columnconfigure(1, weight=1, uniform="overview")
        health, advice = card(split), card(split)
        health.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        advice.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        label(health, "Password health", size=18, bold=True).pack(anchor="w", padx=20, pady=(18, 4))
        total = stats["total"]
        percent = 100 * stats["strong"] / total if total else 0
        label(health, f"{percent:.0f}% strong" if total else "No passwords yet", size=26, bold=True, color=SUCCESS).pack(anchor="w", padx=20)
        label(health, f"{stats['strong']} strong / {total} total credentials", color=MUTED).pack(anchor="w", padx=20, pady=(0, 12))
        for key, color in (("strong", SUCCESS), ("moderate", WARNING), ("weak", ERROR)):
            line = ctk.CTkFrame(health, fg_color="transparent")
            line.pack(fill="x", padx=20, pady=5)
            label(line, f"{key.title()}   {stats[key]}", color=color).pack(anchor="w")
            progress = ctk.CTkProgressBar(line, progress_color=color, fg_color=ELEVATED, height=6)
            progress.pack(fill="x", pady=(3, 5))
            progress.set(stats[key] / total if total else 0)
        label(health, "Rule-based estimates, not a security score.", size=11, color=MUTED, wraplength=280).pack(anchor="w", padx=20, pady=(8, 18))
        label(advice, "Recommended next steps", size=18, bold=True).pack(anchor="w", padx=20, pady=(18, 12))
        for recommendation in self.controller.recommendations():
            item = label(advice, "•  " + recommendation, color=MUTED, wraplength=280)
            item.pack(fill="x", padx=20, pady=(0, 12))
            advice.bind("<Configure>", lambda event, widget=item: widget.configure(wraplength=max(180, event.width - 40)), add="+")
        actions = section(body, "Quick actions")
        self.button(actions, "+ Add credential", self.credential_form, True)
        self.button(actions, "Generate password", self.generator_page)
        self.button(actions, "Open vault", self.vault_page)

    def vault_page(self):
        body = self.shell("Credential Vault", "Manage your logins. Passwords stay hidden until you choose to reveal them.")
        if body is None:
            return
        toolbar = section(body, "Your credentials")
        label(toolbar, "Search website / service", size=11, color=MUTED).pack(anchor="w", pady=(4, 0))
        search = ctk.CTkFrame(toolbar, fg_color="transparent")
        search.pack(fill="x", pady=(0, 8))
        self.query = tk.StringVar(self.root)
        entry(search, textvariable=self.query, placeholder_text="Search by website or service…").pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.button(search, "+ Add credential", self.credential_form, True)
        filters = ctk.CTkFrame(toolbar, fg_color="transparent")
        filters.pack(fill="x")
        self.strength_filter = tk.StringVar(self.root, value="All")
        ctk.CTkSegmentedButton(filters, values=["All", "Weak", "Moderate", "Strong", "Reused"],
                               variable=self.strength_filter, selected_color=ACCENT, unselected_color=ELEVATED,
                               height=32, font=("Segoe UI", 13),
                               command=lambda _: self.refresh_table()).pack(side="left", padx=(0, 16))
        self.alphabetical = tk.BooleanVar(self.root, value=True)
        ctk.CTkSwitch(filters, text="A–Z", variable=self.alphabetical, command=self.refresh_table,
                       progress_color=ACCENT, width=80).pack(side="left", padx=(0, 8))
        self.button(filters, "Reset filters", self.reset_filters)
        self.query.trace_add("write", lambda *_: self.refresh_table())
        self.rows = ctk.CTkScrollableFrame(body, fg_color=BACKGROUND, corner_radius=0, height=100)
        detail = section(body, "Selected credential")
        # Reserve the action panel before giving remaining height to the list.
        detail.master.pack_configure(side="bottom")
        self.revealed = self.secret()
        actions = ctk.CTkFrame(detail, fg_color="transparent")
        actions.pack(fill="x", pady=(6, 0))
        self.reveal_entry = entry(actions, textvariable=self.revealed, show="•", state="readonly", width=140)
        self.reveal_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.button(actions, "Show / Hide", self.toggle_revealed)
        self.button(actions, "Edit", self.edit_selected)
        self.button(actions, "Delete", self.delete_selected, danger=True)
        self.feedback = label(detail, "", color=MUTED, wraplength=600)
        self.feedback.pack(anchor="w")
        self.rows.pack(fill="both", expand=True, pady=(0, 10))
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
        self.selected_id = None
        self.row_buttons = {}
        for child in self.rows.winfo_children():
            child.destroy()
        records = self.controller.filtered_records(self.query.get(), self.strength_filter.get(), self.alphabetical.get())
        if not records:
            empty = section(self.rows, "No credentials found", "Add your first login, or reset your search and filters.")
            button(empty, "+ Add credential", self.credential_form, accent=True).pack(anchor="w")
        for record in records:
            # Only these safe fields enter row widgets. Passwords never do.
            row = card(self.rows)
            row.pack(fill="x", pady=(0, 8))
            row.grid_columnconfigure(0, weight=3)
            row.grid_columnconfigure(1, weight=3)
            website = label(row, record.website, bold=True)
            username = label(row, record.username, color=MUTED)
            rating = estimate_strength(record.password)
            strength = label(row, rating.title(), color=self.strength_color(rating))
            for i, widget in enumerate((website, username, strength)):
                widget.grid(row=0, column=i, sticky="ew", padx=14, pady=16)
                widget.configure(wraplength=200 if i < 2 else 90)
                widget.bind("<Button-1>", lambda event, identifier=record.id: self.select_record(identifier))
            choose = button(row, "Select", lambda identifier=record.id: self.select_record(identifier), width=76)
            choose.grid(row=0, column=3, padx=(0, 12))
            self.row_buttons[record.id] = choose
            row.bind("<Button-1>", lambda event, identifier=record.id: self.select_record(identifier))
        self.feedback.configure(text=f"{len(records)} credentials shown", text_color=MUTED)

    def select_record(self, identifier):
        self.hide_revealed()
        self.selected_id = identifier
        for record_id, widget in self.row_buttons.items():
            widget.configure(text="Selected" if record_id == identifier else "Select", fg_color=ACCENT if record_id == identifier else ELEVATED)

    def selected(self):
        if self.selected_id is None:
            messagebox.showinfo("Select a credential", "Select a row in the vault first.", parent=self.root)
            return None
        return next((record for record in self.controller.records() if record.id == self.selected_id), None)

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
            self.feedback.configure(text="Credential deleted and saved.", text_color=SUCCESS)

    def credential_form(self, record=None, initial_password=""):
        if self.controller.session is None:
            self.show_login()
            return
        if self.dialog is not None:
            self.dialog.lift()
            return
        self.hide_revealed()
        dialog = ctk.CTkToplevel(self.root)
        self.dialog = dialog
        dialog.title("Edit credential" if record else "Add credential")
        dialog.configure(fg_color=BACKGROUND)
        dialog.geometry("560x620")
        dialog.minsize(520, 560)
        dialog.geometry(f"560x620+{self.root.winfo_rootx() + 240}+{self.root.winfo_rooty() + 10}")
        dialog.transient(self.root)
        dialog.grab_set()
        form = ctk.CTkScrollableFrame(dialog, fg_color=PANEL, corner_radius=16)
        form.pack(fill="both", expand=True, padx=20, pady=20)
        label(form, text="Edit credential" if record else "Add credential",
                  size=24, bold=True).pack(anchor="w", pady=(0, 14))
        website = self.secret(record.website if record else "")
        username = self.secret(record.username if record else "")
        password = self.secret(record.password if record else initial_password)
        record_id = record.id if record else None
        variables = (website, username, password)
        entries = []
        for field_name, variable in zip(("Website / Service", "Username", "Password"), variables):
            label(form, text=field_name).pack(anchor="w")
            widget = entry(form, textvariable=variable, show="•" if variable is password else "")
            widget.pack(fill="x", pady=(0, 10))
            entries.append(widget)
        visible = tk.BooleanVar(dialog, value=False)
        ctk.CTkSwitch(form, text="Show password", variable=visible,
                        command=lambda: entries[2].configure(show="" if visible.get() else "•")).pack(anchor="w")
        strength = label(form, color=MUTED)
        strength.pack(anchor="w")
        def update_strength(*_):
            rating = estimate_strength(password.get())
            strength.configure(text=f"Estimated strength: {rating.title()}",
                               text_color=self.strength_color(rating))
        password.trace_add("write", update_strength)
        update_strength()
        button(form, text="Generate Password", command=lambda: self.generate_into_form(
            password, entries[2], visible)).pack(anchor="w", pady=8)
        feedback = label(form, text="", wraplength=420, color=ERROR)
        feedback.pack(fill="x")

        def dismiss():
            for variable in variables:
                variable.set("")
                if variable in self.secret_variables:
                    self.secret_variables.remove(variable)
            dialog.destroy()
            self.dialog = None

        def save():
            for field_name, variable, widget in zip(("Website / Service", "Username", "Password"), variables, entries):
                if not variable.get().strip():
                    feedback.configure(text=f"{field_name} is required. Enter non-space content.")
                    entries[2].configure(show="•")
                    visible.set(False)
                    widget.focus_set()
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
                self.feedback.configure(text="Credential saved successfully.", text_color=SUCCESS)

        actions = ctk.CTkFrame(form, fg_color="transparent")
        actions.pack(anchor="e", pady=8)
        self.button(actions, "Save credential", save, True)
        self.button(actions, "Cancel", dismiss)
        dialog.protocol("WM_DELETE_WINDOW", dismiss)
        dialog.bind("<Escape>", lambda event: dismiss())
        dialog.bind("<Return>", lambda event: save())
        entries[0].focus_set()

    @staticmethod
    def strength_color(rating):
        return {"strong": SUCCESS, "moderate": WARNING, "weak": ERROR}.get(rating, MUTED)

    @staticmethod
    def generate_into_form(password, entry, visible):
        """Fill the existing form using the shared generator; remask every result."""
        password.set(generate_password())
        visible.set(False)
        entry.configure(show="•")


    def generator_page(self):
        body = self.shell("Password Generator", "Long. Random. Unique. Generate a password entirely on your device.")
        if body is None:
            return
        controls = section(body, "Build a better password", "Choose your options, then generate a fresh password.")
        length = tk.IntVar(self.root, value=16)
        length_label = label(controls, "16 characters", size=24, bold=True)
        length_label.pack(anchor="w", pady=(8, 12))
        slider = ctk.CTkSlider(controls, from_=8, to=128, number_of_steps=120, variable=length,
                              progress_color=ACCENT, button_color=ACCENT,
                              command=lambda value: length_label.configure(text=f"{round(value)} characters"))
        slider.pack(fill="x", pady=(0, 4))
        limits = ctk.CTkFrame(controls, fg_color="transparent")
        limits.pack(fill="x")
        label(limits, "8 characters", size=11, color=MUTED).pack(side="left")
        label(limits, "128 characters", size=11, color=MUTED).pack(side="right")
        symbols = tk.BooleanVar(self.root, value=True)
        ctk.CTkSwitch(controls, text="Include symbols", variable=symbols, progress_color=ACCENT).pack(anchor="w", pady=20)
        self.generated = self.secret()
        display = entry(controls, textvariable=self.generated, show="•", state="readonly")
        display.pack(fill="x", pady=(8, 12))
        visible = tk.BooleanVar(self.root, value=False)
        ctk.CTkSwitch(controls, text="Show password", variable=visible, progress_color=ACCENT,
                       command=lambda: display.configure(show="" if visible.get() else "•")).pack(anchor="w")
        strength = label(controls, "Generate a password to see its estimated strength.", color=MUTED)
        strength.pack(anchor="w", pady=16)
        meter = ctk.CTkProgressBar(controls, fg_color=ELEVATED)
        meter.pack(fill="x", pady=(0, 20))
        meter.set(0)

        def generate():
            password = generate_password(length.get(), use_symbols=symbols.get())
            self.generated.set(password)
            visible.set(False)
            display.configure(show="•")
            rating = estimate_strength(password)
            strength.configure(text=f"Estimated strength: {rating.title()}", text_color=self.strength_color(rating))
            meter.configure(progress_color=self.strength_color(rating))
            meter.set({"weak": .25, "moderate": .6, "strong": 1}[rating])
            use.configure(state="normal")

        def use_password():
            password = self.generated.get()
            if password:
                self.vault_page()
                self.credential_form(initial_password=password)

        actions = ctk.CTkFrame(controls, fg_color="transparent")
        actions.pack(fill="x")
        self.button(actions, "Generate password", generate, True)
        use = self.button(actions, "Use in Add Credential", use_password)
        use.configure(state="disabled")
        label(controls, "Nothing is copied to your clipboard. Each new result starts hidden.", color=MUTED, wraplength=560).pack(anchor="w", pady=(10, 0))

    def about_page(self):
        body = self.shell("About & Credits", "SecureLock — Personal Digital Security Management System")
        if body is None:
            return
        intro = section(body, "Built for personal digital security", "Python Programming — Project-Based Learning (PBL)")
        label(intro, "Development Build", color=ACCENT).pack(anchor="w")
        label(intro, "A local encrypted vault with credential management, password generation and explainable password health checks.", color=MUTED, wraplength=580).pack(anchor="w", pady=(8, 0))
        team = section(body, "The project team")
        for name, roll in (("Nikunj Joshi", "25/SET/BCSE/137"), ("Khushi", "25/SET/BCSE/148"),
                           ("Mansi", "25/SET/BCSE/131"), ("Sumit Kumar", "25/SET/BCSE/145")):
            row = ctk.CTkFrame(team, fg_color=ELEVATED, corner_radius=10)
            row.pack(fill="x", pady=(8, 0))
            label(row, name, bold=True).pack(side="left", padx=14, pady=10)
            label(row, roll, color=MUTED).pack(side="right", padx=14)
        academic = section(body, "Academic details")
        label(academic, "Programme: B.Tech Computer Science and Engineering\nSubject: Python Programming\nSubject Code: 5.0CE202E02H", color=MUTED).pack(anchor="w", pady=8)
        label(academic, "Under the Guidance of:\nDr. Rosy Madan (Professor)", size=16, bold=True).pack(anchor="w", pady=(8, 0))
        label(body, "Developed as part of the Python Programming PBL.", color=MUTED).pack(anchor="w")

    def lock(self):
        self.controller.lock()
        self.show_login()

    def close(self):
        self.controller.lock()
        self.clear_page()
        self.root.destroy()


def main() -> None:
    """Launch using the existing project-relative encrypted vault location."""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    SecureLockApp(root, VaultController(DEFAULT_VAULT))
    root.mainloop()
