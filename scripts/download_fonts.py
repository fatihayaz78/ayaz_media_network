#!/usr/bin/env python3
"""Download Roboto fonts for video_maker.py. Run: python scripts/download_fonts.py"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from video_maker import ensure_fonts, FONTS

# Clear existing (possibly corrupt) fonts to force re-download
for key, path in FONTS.items():
    if os.path.exists(path) and os.path.getsize(path) < 1000:
        os.remove(path)

ensure_fonts()

print("\n=== Font Status ===")
all_ok = True
for key, path in FONTS.items():
    exists = os.path.exists(path) and os.path.getsize(path) > 1000
    size = os.path.getsize(path) // 1024 if exists else 0
    status = f"✅ {size}KB" if exists else "❌ MISSING (system fallback)"
    print(f"  {key:8s} {status}")
    if not exists:
        all_ok = False

sys.exit(0 if all_ok else 1)
