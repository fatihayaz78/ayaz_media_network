"""
youtube.py — YouTube Data API v3 upload modülü
OAuth2 credentials: credentials.json (Google Cloud Console'dan indirilir)
Token cache:        token.json (ilk auth sonrası otomatik oluşur)
"""

import os
import json
import time
import pickle
import logging
from datetime import datetime

logger = logging.getLogger("youtube")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
TOKEN_FILE       = os.path.join(os.path.dirname(__file__), "token.json")

CATEGORY_SPORTS = "17"
PRIVACY_PUBLIC  = "public"


def _get_authenticated_service():
    """
    OAuth2 flow:
    1. credentials.json varsa token.json'dan cache okur
    2. Token süresi dolmuşsa refresh eder
    3. Token yoksa browser'da auth URL açar (ilk kez)
    """
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError:
        raise RuntimeError(
            "Google kütüphaneleri eksik.\n"
            "Kur: pip install google-auth google-auth-oauthlib google-api-python-client"
        )

    if not os.path.exists(CREDENTIALS_FILE):
        raise FileNotFoundError(
            f"credentials.json bulunamadı: {CREDENTIALS_FILE}\n"
            "Google Cloud Console'dan indirip proje klasörüne koy."
        )

    creds = None

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("Token süresi dolmuş, yenileniyor...")
            creds.refresh(Request())
        else:
            logger.info("İlk kez auth — browser açılıyor...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        logger.info(f"Token kaydedildi: {TOKEN_FILE}")

    service = build("youtube", "v3", credentials=creds)
    return service


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list,
    privacy: str = PRIVACY_PUBLIC,
    made_for_kids: bool = False,
    retry_count: int = 3,
) -> dict:
    """
    MP4 dosyasını YouTube'a yükler.
    Returns: {"ok": True, "video_id": "...", "url": "..."}
             {"ok": False, "error": "..."}
    """
    if not os.path.exists(video_path):
        return {"ok": False, "error": f"Video dosyası bulunamadı: {video_path}"}

    try:
        from googleapiclient.http import MediaFileUpload
        from googleapiclient.errors import HttpError
    except ImportError:
        return {"ok": False, "error": "google-api-python-client kurulu değil"}

    try:
        service = _get_authenticated_service()
    except Exception as e:
        return {"ok": False, "error": f"Auth hatası: {e}"}

    body = {
        "snippet": {
            "title":       title[:100],
            "description": description[:5000],
            "tags":        tags[:500],
            "categoryId":  CATEGORY_SPORTS,
        },
        "status": {
            "privacyStatus":           privacy,
            "selfDeclaredMadeForKids": made_for_kids,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5,  # 5 MB chunk
    )

    for attempt in range(1, retry_count + 1):
        try:
            logger.info(f"YouTube upload başlıyor (deneme {attempt}/{retry_count}): {title}")
            request = service.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pct = int(status.progress() * 100)
                    logger.info(f"  Upload: %{pct}")

            video_id  = response["id"]
            video_url = f"https://www.youtube.com/shorts/{video_id}"
            logger.info(f"Upload tamamlandı: {video_url}")
            return {"ok": True, "video_id": video_id, "url": video_url}

        except Exception as e:
            logger.warning(f"Upload hatası (deneme {attempt}): {e}")
            if attempt < retry_count:
                time.sleep(5 * attempt)

    return {"ok": False, "error": f"Upload {retry_count} denemede başarısız"}


def build_title(template: str, sport_name: str, channel: str) -> str:
    date_str = datetime.utcnow().strftime("%d %b %Y")
    return (
        template
        .replace("{sport}",   sport_name)
        .replace("{date}",    date_str)
        .replace("{channel}", channel)
    )


def build_description(template: str, sport_name: str, channel: str) -> str:
    return (
        template
        .replace("{sport}",   sport_name)
        .replace("{channel}", channel)
    )


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="YouTube upload module")
    parser.add_argument("--auth", action="store_true",
                        help="Run OAuth2 flow and save token.json")
    parser.add_argument("--test-upload", action="store_true",
                        help="Upload a 1s test video as private")
    args = parser.parse_args()

    if args.auth:
        if not os.path.exists(CREDENTIALS_FILE):
            print(f"Place credentials.json in project root first.")
            print(f"Expected: {CREDENTIALS_FILE}")
            print(f"See docs/YOUTUBE_SETUP.md for instructions.")
        else:
            try:
                svc = _get_authenticated_service()
                print("Authentication successful! token.json saved.")
            except Exception as e:
                print(f"Auth failed: {e}")

    elif args.test_upload:
        import subprocess, tempfile
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            test_path = tmp.name
        try:
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                "color=c=black:size=1080x1920:rate=30:d=1",
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-an",
                test_path,
            ], capture_output=True, check=True)
            result = upload_video(
                test_path,
                title="[TEST] Ayaz Media Network — delete me",
                description="Automated test upload. Safe to delete.",
                tags=["test"],
                privacy="private",
            )
            if result["ok"]:
                print(f"Test upload OK: {result['url']}")
            else:
                print(f"Test upload failed: {result['error']}")
        finally:
            os.unlink(test_path)

    else:
        parser.print_help()
