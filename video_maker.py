"""
video_maker.py — Sports Reel Studio
1080×1920 MP4 reel üretimi.
Mimarisi: sabit header + kayan içerik şeridi + sabit footer (3 katman, ffmpeg overlay)
"""

import os
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
        "name":   "FOOTBALL",
        "bg":     (13, 15, 26),
        "accent": (79, 150, 255),
        "dim":    (30, 42, 74),
    },
    "basket": {
        "name":   "BASKETBALL",
        "bg":     (18, 8, 8),
        "accent": (224, 64, 48),
        "dim":    (50, 20, 18),
    },
    "tenis": {
        "name":   "TENNIS",
        "bg":     (8, 16, 8),
        "accent": (88, 192, 48),
        "dim":    (24, 40, 14),
    },
    "motor": {
        "name":   "MOTORSPORT",
        "bg":     (18, 9, 0),
        "accent": (240, 120, 32),
        "dim":    (48, 28, 10),
    },
    "dovus": {
        "name":   "COMBAT SPORTS",
        "bg":     (14, 8, 20),
        "accent": (144, 80, 208),
        "dim":    (40, 22, 62),
    },
    "amerikan": {
        "name":   "AMERICAN FOOTBALL",
        "bg":     (6, 12, 22),
        "accent": (56, 112, 224),
        "dim":    (18, 30, 58),
    },
    "voley": {
        "name":   "VOLLEYBALL",
        "bg":     (7, 14, 14),
        "accent": (42, 184, 160),
        "dim":    (14, 36, 32),
    },
    "diger": {
        "name":   "OTHER SPORTS",
        "bg":     (12, 12, 18),
        "accent": (140, 140, 180),
        "dim":    (30, 30, 48),
    },
    # ── New channel themes ─────────────────────────────────────────────────────
    "fixtures": {
        "name":   "UPCOMING FIXTURES",
        "bg":     (6, 16, 8),
        "accent": (64, 200, 112),
        "dim":    (18, 44, 24),
    },
    "transfer": {
        "name":   "TRANSFERS",
        "bg":     (18, 8, 0),
        "accent": (255, 140, 0),
        "dim":    (46, 26, 4),
    },
    "finance": {
        "name":   "MARKETS",
        "bg":     (4, 12, 4),
        "accent": (0, 200, 83),
        "dim":    (10, 38, 16),
    },
    "news": {
        "name":   "WORLD NEWS",
        "bg":     (6, 6, 14),
        "accent": (129, 140, 248),
        "dim":    (22, 22, 52),
    },
    "games": {
        "name":   "GAMING",
        "bg":     (8, 4, 20),
        "accent": (168, 85, 247),
        "dim":    (28, 14, 58),
    },
    "music": {
        "name":   "MUSIC CHARTS",
        "bg":     (14, 4, 18),
        "accent": (224, 64, 251),
        "dim":    (40, 14, 52),
    },
    "techai": {
        "name":   "AI & TECH",
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
    "MOTORSPORT":   (240, 120, 32),
    "OTHER":        (150, 150, 180),
    "UPCOMING":     (64, 200, 112),   # fixtures green
    "CHARTS":       (224, 64, 251),   # music violet
    "AI & TECH":    (96, 165, 250),   # techai blue
    "GAMING":       (168, 85, 247),   # games purple
    "MARKETS":      (0, 200, 83),     # finance green
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


def text_height(draw: ImageDraw.ImageDraw, text: str, font) -> int:
    bb = draw.textbbox((0, 0), text, font=font)
    return bb[3] - bb[1]


def draw_text_shadow(draw, xy, text, font, fill, shadow=(0, 0, 0), offset=2):
    draw.text((xy[0]+offset, xy[1]+offset), text, font=font, fill=shadow + (100,))
    draw.text(xy, text, font=font, fill=fill)


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
    f_date  = get_font(36)

    y = 52

    # Satır 1: WEEKLY SCORES — beyaz, bold
    title = "WEEKLY SCORES"
    x = centered_x(draw, title, f_title)
    draw_text_shadow(draw, (x, y), title, f_title, (255, 255, 255, 255))
    y += text_height(draw, title, f_title) + 8

    # Satır 2: SPOR ADI — aksent rengi, aynı font/boyut
    x = centered_x(draw, name, f_title)
    draw.text((x, y), name, font=f_title, fill=accent + (245,))
    y += text_height(draw, name, f_title) + 18

    # Aksent çubuğu
    bar_w = 74
    draw.rectangle(
        [(W - bar_w) // 2, y, (W + bar_w) // 2, y + 4],
        fill=accent + (255,)
    )
    y += 4 + 18

    # Tarih + Hafta — tek satır
    date_text = f"{date_str}  ·  Week {week:02d}"
    x = centered_x(draw, date_text, f_date)
    draw.text((x, y), date_text, font=f_date, fill=dim + (210,))

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

    # Metin bloğu
    tx = tri_x + tri_w + 20
    draw.text((tx, tri_y + 2),               "SUBSCRIBE FOR MORE",
              font=f_sub, fill=dim + (155,))
    draw.text((tx, tri_y + 2 + 30 + 8),      f"@{channel_name}",
              font=f_hdl, fill=accent + (255,))

    # YOUTUBE — ortalı
    yt_y = tri_y + tri_h + 16
    x    = centered_x(draw, "YOUTUBE", f_yt)
    draw.text((x, yt_y), "YOUTUBE", font=f_yt, fill=dim + (175,))

    # Finance disclaimer
    if sport_id == "finance":
        f_disc = get_font(18)
        disc = "NOT FINANCIAL ADVICE · Educational only"
        x = centered_x(draw, disc, f_disc)
        draw.text((x, yt_y + 28), disc, font=f_disc,
                  fill=dim + (120,))

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
                                       (255, 255, 255, 10))
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
                              fill=(195, 195, 210, 225))
                    if line2:
                        draw.text((MARGIN + 10, y + 55), line2, font=f_line2,
                                  fill=(130, 130, 155, 170))
                    y += ROW_H
                    continue

                # Skor kutusu
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
                          fill=(195, 195, 210, 220))

                # Deplasman (sola yaslı)
                ax = box_x + box_w + 16
                draw.text((ax, y + 18), away, font=f_team,
                          fill=(195, 195, 210, 220))

                y += ROW_H

            y += LEAGUE_GAP

    return img


# ── MAKE REEL (ana fonksiyon) ─────────────────────────────────────────────────
def make_reel(config: dict, output_path: str, bg_path: str = None,
              music_path: str = None, music_volume: float = 0.4,
              sport_id: str = "futbol"):
    """
    3 katmanlı video üretimi:
      1. Sabit header  (y=0, yükseklik=HEADER_H)
      2. Kayan içerik  (y=HEADER_H, alttan üste kayar)
      3. Sabit footer  (y=H-FOOTER_H, yükseklik=FOOTER_H)

    Kayma: içeriğin tamamı üstten çıkınca video kapanır.
    """
    ident    = SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY["diger"])
    bg_rgb   = ident["bg"]
    date_str = config.get("date", datetime.now().strftime("%d.%m.%Y"))
    channel  = config.get("channel_name", "DailyScoreBoard")

    # ── Katmanları oluştur ────────────────────────────────────────────────
    header_img  = generate_header(sport_id, date_str)
    footer_img  = generate_footer(sport_id, channel)
    content_img = generate_content_strip(config, sport_id)

    content_h = content_img.height

    # ── Süre hesapla ──────────────────────────────────────────────────────
    # İçerik tamamen üstten çıkana kadar kaydır
    scroll_dist = content_h
    scroll_spd  = 40.0   # px/s
    pause_top   = 3.0    # başlangıç duraklaması (sn)
    scroll_dur  = scroll_dist / scroll_spd if scroll_dist > 0 else 0
    duration    = pause_top + scroll_dur
    duration    = max(8.0, min(180.0, duration))

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

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr[-2000:]}")

    return output_path
