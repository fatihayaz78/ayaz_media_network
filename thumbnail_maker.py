"""
thumbnail_maker.py — YouTube thumbnail generator (1280x720 JPEG)
3-zone layout: top band (accent gradient) + center (title + items) + bottom band (branding)
"""

import os
from PIL import Image, ImageDraw, ImageFont
from video_maker import SPORT_IDENTITY, get_font, get_italic_font, ensure_fonts

TW, TH = 1280, 720
TOP_H = 160
BOT_H = 160
CENTER_H = TH - TOP_H - BOT_H  # 400px

CHANNEL_EMOJI = {
    "futbol":   "\u26BD",    "basket":   "\U0001f3c0",
    "tenis":    "\U0001f3be", "motor":    "\U0001f3ce\ufe0f",
    "dovus":    "\U0001f94a", "amerikan": "\U0001f3c8",
    "voley":    "\U0001f3d0", "finance":  "\U0001f4ca",
    "music":    "\U0001f3b5", "news":     "\U0001f30d",
    "games":    "\U0001f3ae", "techai":   "\U0001f916",
    "transfer": "\U0001f504", "fixtures": "\U0001f4c5",
    "diger":    "\U0001f3c6",
}


def thumbnail_path_for(sport_id: str, date_str: str) -> str:
    """Returns canonical output path for a thumbnail."""
    safe_date = date_str.replace(".", "-").replace("/", "-")
    os.makedirs("output/thumbnails", exist_ok=True)
    return f"output/thumbnails/{sport_id}_{safe_date}.jpg"


def _draw_gradient(draw, x0, y0, x1, y1, color_left, color_right):
    """Horizontal gradient from color_left to color_right."""
    width = x1 - x0
    for i in range(width):
        t = i / max(width - 1, 1)
        r = int(color_left[0] * (1 - t) + color_right[0] * t)
        g = int(color_left[1] * (1 - t) + color_right[1] * t)
        b = int(color_left[2] * (1 - t) + color_right[2] * t)
        draw.line([(x0 + i, y0), (x0 + i, y1)], fill=(r, g, b))


def _find_logo(sport_id: str) -> str:
    """Find logo file: channels/{id}/logo.png > static/logos/{id}.png > None"""
    for path in [
        os.path.join("channels", sport_id, "logo.png"),
        os.path.join("static", "logos", f"{sport_id}.png"),
    ]:
        if os.path.exists(path):
            return path
    return None


def generate_thumbnail(
    sport_id: str,
    date_str: str,
    top_items: list,
    output_path: str = None,
    logo_path: str = None,
) -> str:
    """
    Generates 1280x720 JPEG thumbnail.
    top_items: e.g. ["Man City 3-1 Arsenal", "Real Madrid 2-0 Barca", ...]
    Returns: output_path
    """
    ensure_fonts()
    ident = SPORT_IDENTITY.get(sport_id, SPORT_IDENTITY.get("diger", {}))
    bg     = ident.get("bg", (12, 12, 18))
    accent = ident.get("accent", (140, 140, 180))
    dim    = ident.get("dim", (30, 30, 48))
    header_title = ident.get("header_title", "WEEKLY SCORES")

    if output_path is None:
        output_path = thumbnail_path_for(sport_id, date_str)

    img  = Image.new("RGB", (TW, TH), bg)
    draw = ImageDraw.Draw(img)

    # ── TOP BAND: accent gradient + emoji/logo + date ─────────────────────
    dark_accent = tuple(max(0, c - 40) for c in accent)
    _draw_gradient(draw, 0, 0, TW, TOP_H, accent, dark_accent)

    f_emoji = get_font(80, bold=True)
    f_date  = get_font(36)

    # Logo or emoji
    logo_file = logo_path or _find_logo(sport_id)
    if logo_file and os.path.exists(logo_file):
        try:
            logo = Image.open(logo_file).convert("RGBA")
            logo.thumbnail((100, 100), Image.LANCZOS)
            # Center vertically in top band
            ly = (TOP_H - logo.height) // 2
            img.paste(logo, (30, ly), logo.split()[3] if logo.mode == "RGBA" else None)
        except Exception:
            emoji = CHANNEL_EMOJI.get(sport_id, "\U0001f3c6")
            draw.text((30, 30), emoji, font=f_emoji, fill=(255, 255, 255))
    else:
        emoji = CHANNEL_EMOJI.get(sport_id, "\U0001f3c6")
        draw.text((30, 30), emoji, font=f_emoji, fill=(255, 255, 255))

    # Date — right side
    date_text = date_str
    bb = draw.textbbox((0, 0), date_text, font=f_date)
    dw = bb[2] - bb[0]
    draw.text((TW - dw - 40, (TOP_H - 36) // 2), date_text, font=f_date, fill=(255, 255, 255))

    # ── CENTER: title + top items ─────────────────────────────────────────
    f_title = get_font(86, bold=True)
    f_item  = get_font(36)

    center_y = TOP_H

    # Title — centered
    tb = draw.textbbox((0, 0), header_title, font=f_title)
    tw_text = tb[2] - tb[0]
    th_text = tb[3] - tb[1]
    tx = (TW - tw_text) // 2
    ty = center_y + 40
    draw.text((tx, ty), header_title, font=f_title, fill=(255, 255, 255))

    # Top items — centered, accent color
    item_y = ty + th_text + 30
    for item_text in (top_items or [])[:3]:
        text = (item_text or "")[:48]
        if not text:
            continue
        ib = draw.textbbox((0, 0), text, font=f_item)
        iw = ib[2] - ib[0]
        ix = (TW - iw) // 2
        draw.text((ix, item_y), text, font=f_item, fill=accent)
        item_y += 46

    # ── BOTTOM BAND: branding ─────────────────────────────────────────────
    bot_y = TH - BOT_H
    draw.rectangle([(0, bot_y), (TW, TH)], fill=dim)

    # Thin accent line
    draw.line([(40, bot_y + 8), (TW - 40, bot_y + 8)], fill=accent, width=2)

    f_brand = get_font(32, bold=True)

    # Left: AYAZ MEDIA NETWORK
    draw.text((40, bot_y + 60), "AYAZ MEDIA NETWORK", font=f_brand, fill=(220, 220, 235))

    # Right: @channel handle
    handle = f"@ayaz_{sport_id}"
    hb = draw.textbbox((0, 0), handle, font=f_brand)
    hw = hb[2] - hb[0]
    draw.text((TW - hw - 40, bot_y + 60), handle, font=f_brand, fill=accent)

    # Save
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    img.save(output_path, "JPEG", quality=95)
    return output_path
