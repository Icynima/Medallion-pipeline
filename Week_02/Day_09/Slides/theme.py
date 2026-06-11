"""Theme constants and chart helpers for Day 9 slide deck."""
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor

# ----- Colors (light professional theme) -----
BG_DARK = RGBColor(0xFF, 0xFF, 0xFF)        # white canvas
BG_PANEL = RGBColor(0xF3, 0xF5, 0xF8)       # light grey panel
BG_PANEL_2 = RGBColor(0xE6, 0xEA, 0xF0)     # secondary panel
FG_TEXT = RGBColor(0x14, 0x18, 0x20)        # primary text (near-black)
FG_MUTED = RGBColor(0x4A, 0x52, 0x60)       # secondary text
FG_DIM = RGBColor(0x6E, 0x76, 0x81)         # tertiary text
ACCENT_TEAL = RGBColor(0x0E, 0x9F, 0x8F)    # primary accent (darker teal)
ACCENT_YELLOW = RGBColor(0xC9, 0x8A, 0x00)  # warm accent (darker amber)
ACCENT_RED = RGBColor(0xD6, 0x3A, 0x3A)     # alert/error
ACCENT_GREEN = RGBColor(0x2E, 0x8B, 0x3F)   # success
ACCENT_BLUE = RGBColor(0x2E, 0x6C, 0xD6)    # info
ACCENT_PURPLE = RGBColor(0x7A, 0x4C, 0xD6)  # extra

# ----- Slide geometry (16:9 widescreen 13.333 x 7.5 in) -----
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)
MARGIN_X = Inches(0.5)
MARGIN_Y = Inches(0.4)
TITLE_H = Inches(0.9)
FOOTER_H = Inches(0.35)

# ----- Fonts -----
FONT_TITLE = "Segoe UI Semibold"
FONT_BODY = "Segoe UI"
FONT_MONO = "Consolas"

# ----- Matplotlib chart style -----
MPL_BG = "#FFFFFF"
MPL_PANEL = "#F3F5F8"
MPL_TEXT = "#141820"
MPL_GRID = "#D4D9E0"
MPL_ACCENT = "#0E9F8F"
MPL_YELLOW = "#C98A00"
MPL_RED = "#D63A3A"
MPL_GREEN = "#2E8B3F"
MPL_BLUE = "#2E6CD6"
MPL_PURPLE = "#7A4CD6"

MPL_PALETTE = [MPL_ACCENT, MPL_YELLOW, MPL_RED, MPL_GREEN, MPL_BLUE, MPL_PURPLE]


def apply_mpl_style(plt):
    plt.rcParams.update({
        "figure.facecolor": MPL_BG,
        "axes.facecolor": MPL_PANEL,
        "axes.edgecolor": MPL_GRID,
        "axes.labelcolor": MPL_TEXT,
        "axes.titlecolor": MPL_TEXT,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.grid": True,
        "grid.color": MPL_GRID,
        "grid.linestyle": "--",
        "grid.alpha": 0.5,
        "xtick.color": MPL_TEXT,
        "ytick.color": MPL_TEXT,
        "text.color": MPL_TEXT,
        "font.family": "DejaVu Sans",
        "font.size": 11,
        "legend.facecolor": MPL_PANEL,
        "legend.edgecolor": MPL_GRID,
        "legend.labelcolor": MPL_TEXT,
        "savefig.facecolor": MPL_BG,
        "savefig.edgecolor": MPL_BG,
        "savefig.dpi": 150,
    })
