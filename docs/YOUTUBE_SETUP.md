# YOUTUBE_SETUP.md — YouTube Upload Configuration
> One-time setup. After this, daemon uploads automatically.

---

## Step 1: Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create new project: **Ayaz Media Network**
3. Select the project

## Step 2: Enable YouTube API

1. Go to **APIs & Services** → **Library**
2. Search **YouTube Data API v3**
3. Click **Enable**

## Step 3: Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted, configure consent screen:
   - User Type: **External**
   - App name: **Ayaz Media Network**
   - Add scope: `youtube.upload`
4. Application type: **Desktop app**
5. Name: **ayaz-uploader**
6. Click **Create**
7. Click **Download JSON**
8. Rename to `credentials.json` and place in project root:
   ```
   /Users/fatihayaz/Documents/Projects/ayaz_media_network/credentials.json
   ```

## Step 4: First Authentication

```bash
cd /Users/fatihayaz/Documents/Projects/ayaz_media_network
python youtube.py --auth
```

This opens your browser. Sign in with the YouTube channel account and grant permission.
`token.json` is created automatically — do not delete it.

## Step 5: Test Upload

```bash
python youtube.py --test-upload
```

This uploads a 1-second black frame as a **private** video to verify everything works.
Delete the test video from YouTube Studio afterwards.

## Step 6: Enable in Config

Edit `config.json`:
```json
"youtube_enabled": true
```

Or use the Scheduler UI at http://localhost:5052/scheduler.

## Troubleshooting

- **"credentials.json not found"** → Download from Google Cloud Console (Step 3)
- **"Token expired"** → Delete `token.json` and re-run `python youtube.py --auth`
- **"Quota exceeded"** → YouTube API has a daily quota of ~10,000 units. Each upload = ~1,600 units. Max ~6 uploads/day on free tier.
- **"The user has exceeded the number of videos"** → YouTube limits new channels to ~15 videos/day
