# Techai Channel
YouTube: @ayaz_techai | Theme: techai | Continent split: NO (global)

## Data Source
Primary: Manual editor at /techai-editor → channels/techai/items.json (max 20)
Fallback: TechAIFetcher RSS (TechCrunch, The Verge, VentureBeat, arXiv) + Claude Haiku

## Item Fields
title (80 chars), summary (300 chars), source, category (LLM/Hardware/Policy/Robotics/Other), date, featured (bool)

## Row Format
Wide row mode: home="emoji CATEGORY" | score="" | away="Title" | time="Summary"
Featured items: star prefix, sorted to top

## Status
- Manual editor: WORKING (/techai-editor)
- items.json: 8 seeded sample items
- If items.json has data, RSS fetch is skipped
