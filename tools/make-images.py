#!/usr/bin/env python3
"""Génère les images du site (vignettes Open Graph et icône Apple).

Dépendance : Pillow (`python -m pip install pillow`). À lancer uniquement
quand le texte des vignettes change ; les PNG produits sont versionnés.

    python tools/make-images.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

NAVY = (15, 36, 64)
NAVY_DEEP = (10, 22, 40)
TEAL = (99, 183, 214)
WHITE = (255, 255, 255)
MUTED = (173, 189, 208)
GRID = (30, 52, 80)

FONT_DIR = Path(r"C:\Windows\Fonts")
FONT_CANDIDATES = {
    "bold": ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"],
    "regular": ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"],
    "semibold": ["seguisb.ttf", "segoeuib.ttf", "arialbd.ttf"],
}


def font(kind, size):
    for name in FONT_CANDIDATES[kind]:
        for base in (FONT_DIR, Path("/usr/share/fonts/truetype/dejavu")):
            path = base / name
            if path.exists():
                return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def background(width, height):
    img = Image.new("RGB", (width, height), NAVY_DEEP)
    draw = ImageDraw.Draw(img)
    # Dégradé vertical léger.
    for y in range(height):
        t = y / height
        color = tuple(int(NAVY_DEEP[i] + (NAVY[i] - NAVY_DEEP[i]) * t) for i in range(3))
        draw.line([(0, y), (width, y)], fill=color)
    # Grille technique discrète, atténuée vers la gauche.
    grid = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(grid)
    step = 64
    for x in range(0, width, step):
        gdraw.line([(x, 0), (x, height)], fill=GRID + (110,), width=1)
    for y in range(0, height, step):
        gdraw.line([(0, y), (width, y)], fill=GRID + (110,), width=1)
    mask = Image.linear_gradient("L").rotate(90, expand=True).resize((width, height))
    grid.putalpha(Image.eval(mask, lambda v: int(v * 0.85)))
    img.paste(grid, (0, 0), grid)
    return img


def shield(draw, x, y, size, width=3):
    """Bouclier simple, même dessin que le favicon."""
    s = size / 64
    pts = [
        (x + 32 * s, y + 10 * s),
        (x + 50 * s, y + 17.5 * s),
        (x + 50 * s, y + 30.7 * s),
        (x + 41 * s, y + 46 * s),
        (x + 32 * s, y + 54 * s),
        (x + 23 * s, y + 46 * s),
        (x + 14 * s, y + 30.7 * s),
        (x + 14 * s, y + 17.5 * s),
    ]
    draw.polygon(pts, outline=TEAL, width=width)


def og_card(lang, title_role, subtitle, tagline, out_name):
    width, height = 1200, 630
    img = background(width, height)
    draw = ImageDraw.Draw(img)

    left = 84
    # Bandeau accent à gauche.
    draw.rectangle([(0, 0), (10, height)], fill=TEAL)

    # Monogramme + bouclier.
    draw.rounded_rectangle([(left, 76), (left + 84, 160)], radius=18, fill=NAVY, outline=GRID)
    shield(draw, left + 10, 86, 64, width=3)
    mono = font("bold", 26)
    draw.text((left + 42, 121), "LG", font=mono, fill=WHITE, anchor="mm")

    name = font("bold", 66)
    draw.text((left, 200), "Lénusan Gunarajah", font=name, fill=WHITE)

    role = font("semibold", 38)
    draw.text((left, 292), title_role, font=role, fill=TEAL)

    sub = font("regular", 27)
    draw.text((left, 348), subtitle, font=sub, fill=MUTED)

    draw.line([(left, 418), (left + 120, 418)], fill=TEAL, width=3)

    tag = font("regular", 24)
    y = 440
    for line in tagline:
        draw.text((left, y), line, font=tag, fill=WHITE)
        y += 36

    url = font("semibold", 22)
    draw.text((left, 560), "lenu-san.github.io" + ("/en/" if lang == "en" else ""), font=url, fill=MUTED)

    img.save(ASSETS / out_name, optimize=True)
    print("  écrit", out_name)


def apple_icon():
    size = 180
    img = Image.new("RGB", (size, size), NAVY)
    draw = ImageDraw.Draw(img)
    shield(draw, 0, 0, size, width=6)
    draw.text((size / 2, size / 2 + 6), "LG", font=font("bold", 54), fill=WHITE, anchor="mm")
    img.save(ASSETS / "apple-touch-icon.png", optimize=True)
    print("  écrit apple-touch-icon.png")


if __name__ == "__main__":
    print("Génération des images :")
    og_card(
        "fr",
        "Ingénieur cybersécurité junior",
        "Audit de sécurité · Sécurité des infrastructures · Services managés",
        [
            "Audits de pare-feux (Forcepoint, FortiGate) · Filtrage web haute disponibilité",
            "Diagnostic d'incidents · Mobilité Luxembourg / Metz / Thionville",
        ],
        "og.png",
    )
    og_card(
        "en",
        "Junior Cybersecurity Engineer",
        "Security Auditing · Infrastructure Security · Managed Services",
        [
            "Firewall audits (Forcepoint, FortiGate) · High-availability web filtering",
            "Incident troubleshooting · Open to Luxembourg / Metz / Thionville",
        ],
        "og-en.png",
    )
    apple_icon()
