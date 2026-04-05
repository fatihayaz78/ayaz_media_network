# Transfer Channel
YouTube: @ayaz_transfer | Theme: transfer | Continent split: NO (global)

## Data Source
4 RSS feeds: Sky Sports, BBC Sport Football, Goal.com, The Athletic
Claude Haiku AI extracts transfer info from headlines.
Fallback: 8 sample transfers when RSS+Claude yields <3 rows.

## Keywords (18)
transfer, sign, join, move, deal, fee, bid, loan, contract, agree, complete, medical, swap, release, free agent, extend

## Row Format
home="Player" | score="Fee" | away="From -> To" | status=stars or fire emoji

## Status
- RSS+Claude: WORKING (needs ANTHROPIC_API_KEY)
- Sample fallback: WORKING (8 rows always)
