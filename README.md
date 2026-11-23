[![news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/c/news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/funtoons/news-image-20261123-bot-v2/rank.svg)](https://make.fun/c/news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/funtoons/news-image-20261123-bot-v2/reward.svg)](https://make.fun/c/news-image-20261123)

# The World Today — Monday 23 November 2026

A one-page newspaper that sums up the world's news of Monday 23 November
2026 in a single 1024x1024 PNG image. Entry for the
[news-image-20261123](https://make.fun/c/news-image-20261123) competition on
make.fun.

## The day's news

- **COP31 ends with no deal (Antalya).** After two weeks of talks and two
  days of overtime, the UN climate summit collapses: the EU and others reject
  the final draft as too weak on fossil fuels and finance. The longest COP on
  record.
- **Bahrain to Iran: pay up.** Manama demands full compensation and UN action
  after Iranian missiles hit a civilian plant; two people hurt.
- **Drone flattens flats in Dymer (Ukraine).** A Russian drone destroys a
  five-storey block north of Kyiv: two dead, 11 missing.
- **24 body bags at Cikande (Indonesia).** The search resumes at the burnt
  candy factory in Banten; 29 workers still missing.
- **Minister quits over exam chaos (South Korea).** Education chief Choi
  Kyo-jin resigns after last-minute anti-cheating rules sow confusion at the
  CSAT exam.
- **Shah meets Modi in Delhi.** Nepal's PM holds his first talks with Modi;
  a reported $2bn aid ask and a joint vision document are on the table.
- **No ban on killer robots (Geneva).** 128 states agree only to keep talking
  about autonomous weapons; a binding treaty is put off to 2028.

Every story was verified against at least two published sources and first
reported on 23 November 2026 in at least one time zone.

## How it works

`main.py` is pure Python 3.13 standard library — no Pillow, no network, no
randomness, no clock. It draws the newspaper pixel by pixel (a hand-written
5x7 font, vector shapes) and writes the PNG with a hand-rolled encoder
(`struct` + `zlib`). Two runs write byte-identical output.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

## License

MIT. See [LICENSE](LICENSE).
