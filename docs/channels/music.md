# Music Channel
YouTube: @ayaz_musics | Theme: music | Continent split: YES (3 continents)

## Data Source
Apple Music RSS: https://rss.applemarketingtools.com/api/v2/{cc}/music/most-played/10/songs.json
Top 5 songs per country, weekly cache.

## Countries (18)
- EUROPE (8): UK, Germany, France, Spain, Turkey, Italy, Netherlands, Sweden
- AMERICAS (5): USA, Brazil, Mexico, Argentina, Chile
- ASIA (5): Japan, South Korea, India, Philippines, Indonesia

## Row Format
home="1 star" | score="Song Title" | away="Artist" | status="3w"
Trend: star=new, up=improved, down=dropped, dot=same

## Output
~55 rows total. Splits: AMERICAS(20), EUROPE(20), ASIA(15), AFRICA(0)

## Status
- Fetch: WORKING (fetch_all returns all continents)
- Split: WORKING
- AFRICA: NO SOURCE (no African countries configured)
