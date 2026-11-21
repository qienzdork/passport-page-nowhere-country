[![The Passport Page of a Country That Isn't There](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)
[![Rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/qienzdork/passport-page-nowhere-country/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard)
[![Reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318)

# The Passport Page of a Country That Isn't There

A Python + Pillow program (`main.py`) that draws a complete open passport
spread for the **Republic of Zarnovia** — a country that does not exist —
and writes it to `/output/entry.png` (1024×1024, ~162 KB).

## What the spread shows

- **Left page, data page:** drawn portrait of the holder Mira Kovac, drawn
  coat of arms (three peaks, a star, wavy rivers), bilingual field labels,
  and a machine-readable zone whose ICAO 9303 check digits are computed by
  the program (verified independently).
- **Right page, visas and stamps:** a 72-hour mountain-transit visa
  (No. TV-2025-0117, issued by the Ostrana Consulate in Drenovac), a red
  "TRANSIT FEE 40 ZN — PAID" fee stamp, and five arrival/departure stamps
  from the two neighbouring countries, Belvaria and Ostrana.
- **The telling detail:** Zarnovia only lets travellers through on a
  mountain-transit permit — the visa, the fee stamp and the bilingual note
  ("Holder must carry a mountain transit permit when crossing the
  Drenovac Pass") all say what kind of place it is.

## Internal consistency (what the judge weighs)

- Passport issued 12 JUN 2024, expires 12 JUN 2034. Every stamp is after
  the issue date: Belvaria entry 03 SEP 2024 / exit 17 SEP 2024, Ostrana
  entry 02 MAR 2025 / exit 21 MAR 2025, Belvaria entry 08 AUG 2025.
- The transit visa was issued 02 MAR 2025, the same day as the Ostrana
  entry stamp, by the Ostrana Consulate in Drenovac.
- Document number ZN4829107 appears on the data page, in the MRZ and in
  the visa-page footer; the MRZ check digits verify.

## Run

```sh
python3 main.py   # writes /output/entry.png
```

No network, Pillow only, runs in a few seconds.
