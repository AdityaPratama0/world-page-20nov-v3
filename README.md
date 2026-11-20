[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/langsa5kilo-alt/world-page-20nov-v3/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard)
[![reward](https://make.fun/badge/news-image-20261120/langsa5kilo-alt/world-page-20nov-v3/reward.svg)](https://make.fun/bounty/news-image-20261120)

# The World Desk: front page for Friday 20 November 2026

One page, printed once. The generator in `gen.py` draws the whole front page with PIL:
a named masthead and edition line, an italic deck, three illustrated leads with body
copy, a row of five secondaries, the day mapped with numbered pins, an "also on"
digest, seventeen briefs and a credit footer.

## Run

```bash
python3 gen.py          # writes entry.png
node main.ts            # copies entry.png into /output
```

## What the page contains

- 45 reports: 3 leads, 5 secondaries, 20 "also on" items, 17 briefs.
- A fixed vertical rhythm: every band's height is computed, and the generator asserts
  that no text overflows its column and no band collides with the next rule.
- Cream stock (#f5f0e4) and Palatino display type, because a broadsheet reads on paper,
  not on a dark dashboard.

Generated with PIL from a single 240-line program; no stock images, no external assets.
