"""
video_maker.py — Sports Reel Studio
1080×1920 MP4 reel üretimi.
Mimarisi: sabit header + kayan içerik şeridi + sabit footer (3 katman, ffmpeg overlay)
"""

import os
import json
import subprocess
import urllib.request
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

W, H      = 1080, 1920
HEADER_H  = 340
FOOTER_H  = 220
CONTENT_H = H - HEADER_H - FOOTER_H   # 1360 px görünür alan
MARGIN    = 70
FPS       = 30

# ── Sport kimlik sistemi ──────────────────────────────────────────────────────
SPORT_IDENTITY = {
    "futbol": {
        "name":         "FOOTBALL",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["football","soccer","weekly scores","highlights"],
        "bg":     (13, 15, 26),
        "accent": (79, 150, 255),
        "dim":    (30, 42, 74),
    },
    "basket": {
        "name":         "BASKETBALL",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["basketball","NBA","weekly scores"],
        "bg":     (18, 8, 8),
        "accent": (224, 64, 48),
        "dim":    (50, 20, 18),
    },
    "tenis": {
        "name":         "TENNIS",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["tennis","ATP","WTA","weekly results"],
        "bg":     (8, 16, 8),
        "accent": (88, 192, 48),
        "dim":    (24, 40, 14),
    },
    "motor": {
        "name":         "MOTORSPORT",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["motorsport","F1","MotoGP","race results"],
        "bg":     (18, 9, 0),
        "accent": (240, 120, 32),
        "dim":    (48, 28, 10),
    },
    "dovus": {
        "name":         "COMBAT SPORTS",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["UFC","MMA","combat sports","fight results"],
        "bg":     (14, 8, 20),
        "accent": (144, 80, 208),
        "dim":    (40, 22, 62),
    },
    "amerikan": {
        "name":         "AMERICAN FOOTBALL",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["NFL","american football","weekly scores"],
        "bg":     (6, 12, 22),
        "accent": (56, 112, 224),
        "dim":    (18, 30, 58),
    },
    "voley": {
        "name":         "VOLLEYBALL",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["volleyball","VNL","weekly results"],
        "bg":     (7, 14, 14),
        "accent": (42, 184, 160),
        "dim":    (14, 36, 32),
    },
    "diger": {
        "name":         "OTHER SPORTS",
        "header_title": "WEEKLY SCORES",
        "yt_category":  "17",
        "yt_tags":      ["sports","weekly scores"],
        "bg":     (12, 12, 18),
        "accent": (140, 140, 180),
        "dim":    (30, 30, 48),
    },
    # ── New channel themes ─────────────────────────────────────────────────────
    "fixtures": {
        "name":         "UPCOMING FIXTURES",
        "header_title": "UPCOMING FIXTURES",
        "yt_category":  "17",
        "yt_tags":      ["fixtures","upcoming matches","football schedule"],
        "bg":     (6, 16, 8),
        "accent": (64, 200, 112),
        "dim":    (18, 44, 24),
    },
    "transfer": {
        "name":         "TRANSFERS",
        "header_title": "WEEKLY TRANSFER NEWS",
        "yt_category":  "17",
        "yt_tags":      ["transfer news","football transfers","weekly transfers"],
        "bg":     (18, 8, 0),
        "accent": (255, 140, 0),
        "dim":    (46, 26, 4),
    },
    "finance": {
        "name":         "MARKETS",
        "header_title": "WEEKLY MARKETS",
        "yt_category":  "25",
        "yt_tags":      ["finance","markets","stocks","weekly markets"],
        "bg":     (4, 12, 4),
        "accent": (0, 200, 83),
        "dim":    (10, 38, 16),
    },
    "news": {
        "name":         "WORLD NEWS",
        "header_title": "WEEKLY WORLD NEWS",
        "yt_category":  "25",
        "yt_tags":      ["world news","breaking news","weekly news"],
        "bg":     (6, 6, 14),
        "accent": (129, 140, 248),
        "dim":    (22, 22, 52),
    },
    "games": {
        "name":         "GAMING",
        "header_title": "WEEKLY GAME NEWS",
        "yt_category":  "20",
        "yt_tags":      ["gaming","game news","weekly gaming"],
        "bg":     (8, 4, 20),
        "accent": (168, 85, 247),
        "dim":    (28, 14, 58),
    },
    "music": {
        "name":         "MUSIC CHARTS",
        "header_title": "WEEKLY WORLD TOP 5",
        "yt_category":  "10",
        "yt_tags":      ["music","charts","billboard","top5","weekly"],
        "bg":     (14, 4, 18),
        "accent": (224, 64, 251),
        "dim":    (40, 14, 52),
    },
    "techai": {
        "name":         "AI & TECH",
        "header_title": "AI & TECH WEEKLY",
        "yt_category":  "28",
        "yt_tags":      ["AI","tech","artificial intelligence","weekly tech"],
        "bg":     (4, 8, 20),
        "accent": (96, 165, 250),
        "dim":    (14, 26, 58),
    },
}

# Her kıta için sabit aksent rengi (sport aksentiyle karışmaz)
CONTINENT_COLORS = {
    "EUROPE":       (79, 150, 255),
    "AMERICAS":     (220, 64, 64),
    "ASIA-PACIFIC": (88, 192, 48),
    "ASIA":         (88, 192, 48),
    "MOTORSPORT":   (240, 120, 32),
    "OTHER":        (150, 150, 180),
    "UPCOMING":     (64, 200, 112),   # fixtures green
    "CHARTS":       (224, 64, 251),   # music violet
    "AI & TECH":    (96, 165, 250),   # techai blue
    "GAMING":       (168, 85, 247),   # games purple
    "MARKETS":      (0, 200, 83),     # finance green
    "COMMODITIES":  (218, 165, 32),   # gold
    "CRYPTO":       (247, 147, 26),   # bitcoin orange
    "TRANSFERS":    (255, 140, 0),    # transfer orange
    "NEWS":         (129, 140, 248),  # news indigo
}

LEAGUE_COLORS = {
    "Premier League":                        (111, 45,  189),
    "Trendyol Süper Lig":                    (232, 64,   64),
    "LaLiga":                                (255, 107,  53),
    "Serie A":                               (0,   87,  168),
    "Bundesliga":                            (227,  6,   19),
    "Ligue 1":                               (0,   63,  135),
    "VriendenLoterij Eredivisie":            (255, 102,   0),
    "Liga Portugal Betclic":                 (0,  100,   60),
    "Pro League":                            (60,  60,   60),
    "UEFA Champions League, Knockout stage": (0,   32,   96),
    "Brasileirão Betano":                    (0,  156,   59),
    "Liga Profesional de Fútbol, Apertura":  (116, 172, 223),
    "NBA":                                   (201,  8,   42),
    "NFL":                                   (1,   51,  105),
    "MLS":                                   (18, 134,   68),
    "EuroLeague":                            (0,   61,  165),
    "BSL":                                   (232,  64,  64),
    "Formula 1":                             (232,  0,   45),
    "MotoGP":                                (204,  0,    0),
    "Moto2":                                 (180,  90,   0),
    "Moto3":                                 (140,  60,   0),
    "ATP":                                   (26,  123, 196),
    "WTA":                                   (196,  26,  90),
}

# ── Font yönetimi ─────────────────────────────────────────────────────────────
FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")
FONTS = {
    "regular": os.path.join(FONT_DIR, "Roboto-Regular.ttf"),
    "bold":    os.path.join(FONT_DIR, "Roboto-Bold.ttf"),
    "italic":  os.path.join(FONT_DIR, "Roboto-Italic.ttf"),
}
GOOGLE_FONTS_SOURCES = {
    "regular": [
        "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf",
        "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Regular.ttf",
        "https://cdn.jsdelivr.net/npm/@fontsource/roboto/files/roboto-latin-400-normal.ttf",
    ],
    "bold": [
        "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf",
        "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Bold.ttf",
        "https://cdn.jsdelivr.net/npm/@fontsource/roboto/files/roboto-latin-700-normal.ttf",
    ],
    "italic": [
        "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Italic.ttf",
        "https://github.com/google/fonts/raw/main/apache/roboto/static/Roboto-Italic.ttf",
        "https://cdn.jsdelivr.net/npm/@fontsource/roboto/files/roboto-latin-400-italic.ttf",
    ],
}


def ensure_fonts():
    os.makedirs(FONT_DIR, exist_ok=True)
    for key, path in FONTS.items():
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue
        sources = GOOGLE_FONTS_SOURCES.get(key, [])
        for url in sources:
            try:
                print(f"[fonts] Trying {key} from {url[:60]}...")
                urllib.request.urlretrieve(url, path)
                size = os.path.getsize(path)
                if size > 1000:
                    print(f"[fonts] {key} OK ({size // 1024}KB)")
                    break
                else:
                    os.remove(path)
            except Exception as ex:
                print(f"[fonts] Failed: {ex}")
        else:
            print(f"[fonts] {key}: all sources failed — using system fallback")


def get_font(size: int, bold: bool = False):
    ensure_fonts()
    key  = "bold" if bold else "regular"
    path = FONTS[key]
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    for p in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans" + ("-Bold" if bold else "") + ".ttf",
        "C:/Windows/Fonts/arial" + ("bd" if bold else "") + ".ttf",
    ]:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def get_italic_font(size: int):
    ensure_fonts()
    path = FONTS["italic"]
    if os.path.exists(path):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return get_font(size)


# ── Çizim yardımcıları ────────────────────────────────────────────────────────
def league_color(name: str) -> tuple:
    for k, v in LEAGUE_COLORS.items():
        if k.lower() in (name or "").lower():
            return v
    return (120, 120, 130)


def centered_x(draw: ImageDraw.ImageDraw, text: str, font, width: int = W) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return (width - (bb[2] - bb[0])) // 2


def truncate_text(draw: ImageDraw.ImageDraw, text: str, font, max_w: int) -> str:
    """Truncate text to fit within max_w pixels, appending '...' if needed."""
    bb = draw.textbbox((0, 0), text, font=font)
    if (bb[2] - bb[0]) <= max_w:
        return text
    for i in range(len(text), 0, -1):
        t = text[:i] + "..."
        bb = draw.textbbox((0, 0), t, font=font)
        if (bb[2] - bb[0]) <= max_w:
            return t
    return "..."


def text_height(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def draw_text_shadow(draw, xy, text, font, fill, shadow=(0, 0, 0), offset=2):
    draw.text((xy[0]+offset, xy[1]+offset), text, font=font, fill=shadow + (100,))
    draw.text(xy, text, font=font, fill=fill)


def auto_text_colors(accent: tuple) -> dict:
    """Given accent color, return appropriate text colors based on luminance."""
    r, g, b = accent[:3]
    luminance = 0.299*r + 0.587*g + 0.114*b
    if luminance > 160:  # light accent
        return {
            "title":    (20, 20, 20),
            "subtitle": (60, 60, 60),
            "content":  (40, 40, 40),
        }
    else:  # dark accent (most cases)
        return {
            "title":    (255, 255, 255),
            "subtitle": (195, 195, 210),
            "content":  (160, 160, 180),
        }


def get_week_num(date_str: str) -> int:
    """dd.mm.yyyy → ISO hafta numarası"""
    try:
        d = datetime.strptime(date_str, "%d.%m.%Y")
        return d.isocalendar()[1]
    except Exception:
        return datetime.now().isocalendar()[1]


# ── HEADER (sabit) ────────────────────────────────────────────────────────────
def generate_header(sport_id: str, date_str: str) -> Image.Image:
    """
    Sabit header katmanı.
    İçerik: WEEKLY SCORES (beyaz) + SPOR ADI (aksent rengi) + çubuk + tarih/hafta
    Döner: RGBA Image, W × HEADER_H
    """
    ident  = SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"])
    bg     = ident["bg"]
    accent = ident["accent"]
    dim    = ident["dim"]
    name   = ident["name"]
    week   = get_week_num(date_str)

    img  = Image.new("RGBA", (W, HEADER_H), bg + (255,))
    draw = ImageDraw.Draw(img)

    f_title = get_font(82, bold=True)
    f_date  = get_font(48)

    # Title — centered vertically in upper portion
    title = ident.get("header_title", "WEEKLY SCORES")
    title_h = text_height(draw, title, f_title)
    title_y = 72
    x = centered_x(draw, title, f_title)
    draw.text((x, title_y), title, font=f_title, fill=(255, 255, 255, 255))

    # Aksent çubuğu — anchored well below title
    bar_y = title_y + title_h + 28
    bar_w = 74
    draw.rectangle(
        [(W - bar_w) // 2, bar_y, (W + bar_w) // 2, bar_y + 4],
        fill=accent + (255,)
    )

    # Tarih + Hafta — below bar
    date_y = bar_y + 4 + 24
    date_text = f"{date_str}  \u00b7  Week {week:02d}"
    x = centered_x(draw, date_text, f_date)
    draw.text((x, date_y), date_text, font=f_date, fill=(220, 220, 235, 255))

    # Alt ayırıcı çizgi
    draw.line(
        [(MARGIN, HEADER_H - 1), (W - MARGIN, HEADER_H - 1)],
        fill=accent + (40,), width=1
    )

    return img


# ── FOOTER (sabit) ────────────────────────────────────────────────────────────
def generate_footer(sport_id: str, channel_name: str) -> Image.Image:
    """
    Sabit footer katmanı.
    İçerik: abone çağrısı, @kanal, YOUTUBE — hepsi aksent renginde
    Döner: RGBA Image, W × FOOTER_H
    """
    ident  = SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"])
    bg     = ident["bg"]
    accent = ident["accent"]
    dim    = ident["dim"]

    img  = Image.new("RGBA", (W, FOOTER_H), bg + (255,))
    draw = ImageDraw.Draw(img)

    # Üst ayırıcı
    draw.line([(MARGIN, 1), (W - MARGIN, 1)], fill=accent + (40,), width=1)

    f_sub = get_font(28)
    f_hdl = get_font(44, bold=True)
    f_yt  = get_font(26, bold=True)

    center_y = FOOTER_H // 2 - 8

    # Play üçgeni
    tri_h = 46
    tri_w = int(tri_h * 0.78)
    sub_w = draw.textbbox((0, 0), f"@{channel_name}", font=f_hdl)[2]
    group_total = tri_w + 20 + max(sub_w, 300)
    tri_x = (W - group_total) // 2
    tri_y = center_y - tri_h // 2

    draw.polygon([
        (tri_x,          tri_y),
        (tri_x,          tri_y + tri_h),
        (tri_x + tri_w,  tri_y + tri_h // 2),
    ], fill=accent + (255,))

    # Metin bloğu — no shadows, bright colors
    tx = tri_x + tri_w + 20
    draw.text((tx, tri_y + 2),               "SUBSCRIBE FOR MORE",
              font=f_sub, fill=(210, 210, 225, 255))
    bright_accent = tuple(min(c + 50, 255) for c in accent) + (255,)
    draw.text((tx, tri_y + 2 + 30 + 8),      f"@{channel_name}",
              font=f_hdl, fill=bright_accent)

    # YOUTUBE — ortalı
    yt_y = tri_y + tri_h + 16
    x    = centered_x(draw, "YOUTUBE", f_yt)
    draw.text((x, yt_y), "YOUTUBE", font=f_yt, fill=dim + (175,))

    # Finance disclaimer
    if sport_id == "finance":
        f_disc = get_font(22)
        disc = "NOT FINANCIAL ADVICE \u00b7 Educational only"
        x = centered_x(draw, disc, f_disc)
        draw.text((x, yt_y + 28), disc, font=f_disc,
                  fill=(190, 190, 200, 230))

    return img


# ── CONTENT STRIP (kayan) ─────────────────────────────────────────────────────
def generate_content_strip(config: dict, sport_id: str) -> Image.Image:
    """
    Kayan içerik şeridi — sadece maç sonuçları, header/footer yok.
    Döner: RGBA Image, W × (değişken yükseklik)
    """
    ident      = SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"])
    bg         = ident["bg"]
    continents = config.get("continents", [])

    f_cont   = get_font(34, bold=True)
    f_league = get_font(28, bold=True)
    f_team   = get_font(32)
    f_score  = get_font(38, bold=True)

    ROW_H      = 68
    LEAGUE_H   = 52
    CONT_H     = 56
    LEAGUE_GAP = 22
    CONT_GAP   = 44

    # Yükseklik hesapla
    total_h = 28
    for ci, cont in enumerate(continents):
        if ci > 0:
            total_h += CONT_GAP
        if cont.get("name"):
            total_h += CONT_H
        for g in cont.get("groups", []):
            if not g.get("matches"):
                continue
            total_h += LEAGUE_H
            total_h += len(g["matches"]) * ROW_H
            total_h += LEAGUE_GAP
    total_h += 80
    total_h  = max(total_h, 400)

    img  = Image.new("RGBA", (W, total_h), bg + (255,))
    draw = ImageDraw.Draw(img)
    y    = 28

    for ci, cont in enumerate(continents):
        if ci > 0:
            y += CONT_GAP

        cont_name = cont.get("name", "")
        if cont_name:
            cont_color = CONTINENT_COLORS.get(cont_name, (150, 150, 180))
            line_y     = y + CONT_H // 2

            # Sol + sağ çizgiler
            draw.line([(MARGIN, line_y), (W // 2 - 92, line_y)],
                      fill=cont_color + (50,), width=1)
            draw.line([(W // 2 + 92, line_y), (W - MARGIN, line_y)],
                      fill=cont_color + (50,), width=1)

            # Kıta adı — ortalı
            x = centered_x(draw, cont_name, f_cont)
            draw.text((x, y + 10), cont_name, font=f_cont,
                      fill=cont_color + (200,))
            y += CONT_H

        for g in cont.get("groups", []):
            matches = g.get("matches", [])
            if not matches:
                continue

            # Lig başlığı — sol aksent çubuğu
            league  = g.get("league", "")
            display = g.get("display_name") or league
            col     = league_color(league)

            draw.rectangle(
                [MARGIN, y + 6, MARGIN + 3, y + LEAGUE_H - 8],
                fill=col
            )
            draw.text((MARGIN + 18, y + 12), display, font=f_league,
                      fill=(155, 155, 182, 220))
            y += LEAGUE_H

            # Maç satırları
            for mi, m in enumerate(matches):
                # Alternatif satır arkaplanı
                if mi % 2 == 0:
                    row_bg = Image.new("RGBA", (W - 2*MARGIN, ROW_H - 8),
                                       (255, 255, 255, 18))
                else:
                    row_bg = Image.new("RGBA", (W - 2*MARGIN, ROW_H - 8),
                                       (0, 0, 0, 22))
                img.alpha_composite(row_bg, (MARGIN, y + 4))

                home  = m.get("home",  "")
                score = m.get("score", "–")
                away  = m.get("away",  "")

                # Wide row mode: score is empty → two-line layout
                if not score.strip():
                    f_label = get_font(22)
                    f_line1 = get_font(28, bold=True)
                    f_line2 = get_font(22)

                    label = home
                    line1 = away
                    line2 = m.get("time", "")

                    safe_col = tuple(min(c + 60, 255) for c in col)
                    draw.text((MARGIN + 10, y + 6), label, font=f_label,
                              fill=safe_col + (180,))
                    draw.text((MARGIN + 10, y + 28), line1, font=f_line1,
                              fill=(225, 225, 240, 245))
                    if line2:
                        draw.text((MARGIN + 10, y + 55), line2, font=f_line2,
                                  fill=(130, 130, 155, 170))
                    y += ROW_H
                    continue

                # Skor kutusu — truncate if too wide
                max_score_w = W - 2*MARGIN - 120
                score = truncate_text(draw, score, f_score, max_score_w)
                sb    = draw.textbbox((0, 0), score, font=f_score)
                sw    = sb[2] - sb[0]
                box_w = sw + 28
                box_x = (W - box_w) // 2
                box_y = y + (ROW_H - 50) // 2

                # Kutu arka plan + kenar
                box_bg = Image.new("RGBA", (box_w, 50), col + (38,))
                img.alpha_composite(box_bg, (box_x, box_y))
                draw.rectangle(
                    [box_x, box_y, box_x + box_w - 1, box_y + 49],
                    outline=col + (100,), width=2
                )

                # Skor metni (lig renginin aydınlatılmış hali)
                sc_col = tuple(min(c + 90, 255) for c in col) + (255,)
                draw.text((box_x + 14, box_y + 6), score, font=f_score,
                          fill=sc_col)

                # Ev sahibi (sağa yaslı)
                bb = draw.textbbox((0, 0), home, font=f_team)
                hw = bb[2] - bb[0]
                hx = max(MARGIN, box_x - hw - 16)
                draw.text((hx, y + 18), home, font=f_team,
                          fill=(225, 225, 240, 245))

                # Deplasman (sola yaslı)
                ax = box_x + box_w + 16
                draw.text((ax, y + 18), away, font=f_team,
                          fill=(225, 225, 240, 245))

                y += ROW_H

            y += LEAGUE_GAP

    return img


# ── MAKE REEL (ana fonksiyon) ─────────────────────────────────────────────────
def make_reel(config: dict, output_path: str, bg_path: str = None,
              music_path: str = None, music_volume: float = 0.4,
              sport_id: str = "futbol", custom_theme: dict = None):
    """
    3 katmanlı video üretimi:
      1. Sabit header  (y=0, yükseklik=HEADER_H)
      2. Kayan içerik  (y=HEADER_H, alttan üste kayar)
      3. Sabit footer  (y=H-FOOTER_H, yükseklik=FOOTER_H)

    Kayma: içeriğin tamamı üstten çıkınca video kapanır.
    custom_theme: {"bg": [r,g,b], "accent": [r,g,b], "dim": [r,g,b]}
    """
    # If custom_theme provided, inject temporarily into SPORT_IDENTITY
    _custom_key = None
    if custom_theme:
        _custom_key = f"_custom_{id(config)}"
        SPORT_IDENTITY[_custom_key] = {
            "name":   SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"])["name"],
            "bg":     tuple(custom_theme["bg"]),
            "accent": tuple(custom_theme["accent"]),
            "dim":    tuple(custom_theme["dim"]),
        }
        sport_id = _custom_key

    ident    = SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"])
    bg_rgb   = ident["bg"]
    date_str = config.get("date", datetime.now().strftime("%d.%m.%Y"))
    channel  = config.get("channel_name", "DailyScoreBoard")

    # ── Load per-channel reel_config.json overrides ─────────────────────
    reel_cfg_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "channels", sport_id, "reel_config.json"
    )
    reel_cfg = {}
    if os.path.exists(reel_cfg_path):
        try:
            with open(reel_cfg_path, "r", encoding="utf-8") as f:
                reel_cfg = json.load(f)
        except Exception:
            pass

    # Apply overrides from reel_config
    if reel_cfg.get("header_text"):
        ident = {**ident, "header_title": reel_cfg["header_text"]}
        if _custom_key and _custom_key in SPORT_IDENTITY:
            SPORT_IDENTITY[_custom_key]["header_title"] = reel_cfg["header_text"]
        else:
            SPORT_IDENTITY[sport_id] = {**SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"]), "header_title": reel_cfg["header_text"]}
    if reel_cfg.get("footer_text"):
        channel = reel_cfg["footer_text"]
    if reel_cfg.get("bg_color"):
        try:
            h = reel_cfg["bg_color"].lstrip("#")
            bg_rgb = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except Exception:
            pass
    if reel_cfg.get("accent_color"):
        try:
            h = reel_cfg["accent_color"].lstrip("#")
            new_accent = (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
            ident = {**ident, "accent": new_accent}
        except Exception:
            pass

    # Speed multiplier: 1.0→40, 1.5→60, 2.0→80
    speed_mult = float(reel_cfg.get("reel_speed", 1.5))
    base_scroll_spd = speed_mult * 40.0

    # ── Katmanları oluştur ────────────────────────────────────────────────
    header_img  = generate_header(sport_id, date_str)
    footer_img  = generate_footer(sport_id, channel)
    content_img = generate_content_strip(config, sport_id)

    content_h = content_img.height

    # ── Süre hesapla ──────────────────────────────────────────────────────
    # İçerik tamamen üstten çıkana kadar kaydır
    scroll_dist = content_h
    scroll_spd  = base_scroll_spd
    pause_top   = 3.0    # başlangıç duraklaması (sn)
    PAUSE_BOTTOM = 2.0   # son satır çıktıktan sonra bekleme
    scroll_dur  = scroll_dist / scroll_spd if scroll_dist > 0 else 0
    duration    = pause_top + scroll_dur + PAUSE_BOTTOM
    duration    = max(8.0, duration)   # no upper cap — ends when content exits

    # ── Geçici PNG dosyaları ──────────────────────────────────────────────
    tmp_dir = os.path.dirname(output_path) or "."
    pid     = os.getpid()
    hdr_png = os.path.join(tmp_dir, f"_hdr_{pid}.png")
    ftr_png = os.path.join(tmp_dir, f"_ftr_{pid}.png")
    cnt_png = os.path.join(tmp_dir, f"_cnt_{pid}.png")

    def _save(img_rgba: Image.Image, path: str):
        rgb = Image.new("RGB", img_rgba.size, bg_rgb)
        if img_rgba.mode == "RGBA":
            rgb.paste(img_rgba, mask=img_rgba.split()[3])
        else:
            rgb.paste(img_rgba)
        rgb.save(path, "PNG")

    _save(header_img,  hdr_png)
    _save(footer_img,  ftr_png)
    _save(content_img, cnt_png)

    # ── ffmpeg filter ─────────────────────────────────────────────────────
    # İçerik şeridinin y konumu: HEADER_H'den başlar, scroll_dist kadar yukarı kayar
    spd = scroll_dist / scroll_dur if scroll_dur > 0 else 0
    if scroll_dist > 0:
        ye = (
            f"if(lt(t,{pause_top:.1f}),"
            f"{HEADER_H},"
            f"max({HEADER_H - scroll_dist},"
            f"{HEADER_H}-(t-{pause_top:.1f})*{spd:.2f}))"
        )
    else:
        ye = str(HEADER_H)

    br, bg_, bb_ = bg_rgb

    # Arka plan girişi
    if bg_path and os.path.exists(bg_path):
        ext = os.path.splitext(bg_path)[1].lower()
        if ext in (".mp4", ".mov"):
            bg_inputs = ["-stream_loop", "-1", "-i", bg_path]
        else:
            bg_inputs = ["-loop", "1", "-i", bg_path]
        bg_filter = f"[0:v]scale={W}:{H},setsar=1[bg];"
    else:
        bg_inputs = [
            "-f", "lavfi",
            "-i", f"color=c=0x{br:02x}{bg_:02x}{bb_:02x}:size={W}x{H}:rate={FPS}"
        ]
        bg_filter = "[0:v]setsar=1[bg];"

    has_music = bool(music_path and os.path.exists(music_path))

    input_args = [
        *bg_inputs,
        "-loop", "1", "-i", cnt_png,   # idx 1
        "-loop", "1", "-i", hdr_png,   # idx 2
        "-loop", "1", "-i", ftr_png,   # idx 3
    ]
    if has_music:
        input_args += ["-stream_loop", "-1", "-i", music_path]  # idx 4

    # Filter graph
    fc = (
        f"{bg_filter}"
        f"[1:v]setpts=PTS-STARTPTS[cnt];"
        f"[2:v]setpts=PTS-STARTPTS[hdr];"
        f"[3:v]setpts=PTS-STARTPTS[ftr];"
        f"[bg][cnt]overlay=0:y='{ye}'[v1];"
        f"[v1][hdr]overlay=0:0[v2];"
        f"[v2][ftr]overlay=0:{H - FOOTER_H}[out]"
    )

    if has_music:
        fc += (
            f";[4:a]"
            f"volume={music_volume:.2f},"
            f"afade=t=in:st=0:d=1.5,"
            f"afade=t=out:st={max(0, duration-2):.1f}:d=2.0"
            f"[aout]"
        )
        audio_map = ["-map", "[aout]"]
        audio_enc = ["-c:a", "aac", "-b:a", "192k", "-ar", "44100"]
    else:
        audio_map = []
        audio_enc = ["-an"]

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", fc,
        "-map", "[out]",
        *audio_map,
        "-t", f"{duration:.1f}",
        "-r", str(FPS),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "22",
        "-preset", "fast",
        *audio_enc,
        output_path,
    ]

    print("[ffmpeg]", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Geçici dosyaları temizle
    for p in [hdr_png, ftr_png, cnt_png]:
        try:
            os.remove(p)
        except Exception:
            pass

    # Clean up custom theme from SPORT_IDENTITY
    if _custom_key and _custom_key in SPORT_IDENTITY:
        del SPORT_IDENTITY[_custom_key]

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-2000:]}")

    return output_path
