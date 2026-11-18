"""Small shared CustomTkinter components and the SecureLock visual palette."""

import customtkinter as ctk

BACKGROUND = "#0B1120"
SIDEBAR = "#111C2E"
PANEL = "#18263B"
ELEVATED = "#21334B"
ACCENT = "#4F8FF7"
TEXT = "#F1F5F9"
MUTED = "#94A3B8"
SUCCESS = "#34D399"
WARNING = "#FBBF24"
ERROR = "#F87171"
FONT = "Segoe UI"


def label(parent, text="", size=13, bold=False, color=TEXT, **kwargs):
    return ctk.CTkLabel(parent, text=text, font=(FONT, size, "bold" if bold else "normal"),
                        text_color=color, anchor="w", justify="left", **kwargs)


def button(parent, text, command, accent=False, danger=False, **kwargs):
    return ctk.CTkButton(
        parent, text=text, command=command, height=38, corner_radius=9,
        font=(FONT, 13, "bold"), fg_color=ACCENT if accent else ELEVATED,
        hover_color="#3975D1" if accent else "#2D4564",
        text_color=ERROR if danger else TEXT, **kwargs)


def entry(parent, **kwargs):
    return ctk.CTkEntry(parent, height=42, corner_radius=9, fg_color=BACKGROUND,
                        border_color=ELEVATED, text_color=TEXT, font=(FONT, 14), **kwargs)


def card(parent):
    return ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=16)


def section(parent, title, subtitle=""):
    """A padded card body, keeping page layout code readable for the PBL."""
    outer = card(parent)
    outer.pack(fill="x", pady=(0, 16))
    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=22, pady=18)
    label(inner, title, size=18, bold=True).pack(anchor="w")
    if subtitle:
        label(inner, subtitle, color=MUTED, wraplength=540).pack(anchor="w", pady=(3, 14))
    return inner
