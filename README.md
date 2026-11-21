# gta6_meme_parking

[![make.fun · gta6-meme-x-01](https://make.fun/badge/gta6-meme-x-01.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![rank](https://make.fun/badge/gta6-meme-x-01/AARenor/gta6_meme_parking/rank.svg)](https://make.fun/bounty/gta6-meme-x-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)
[![reward](https://make.fun/badge/gta6-meme-x-01/AARenor/gta6_meme_parking/reward.svg)](https://make.fun/bounty/gta6-meme-x-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01)

A Vice City parking citation for a white Infernus left in a loading zone on Ocean Drive on 17 September 2013 — the day GTA V came out — and written up 4,813 days later, in GTA 6's launch week. The fine is paid, in the paperwork, by the owner's AI agent out of a make.fun bounty: the joke is the thirteen-year wait, and the advert is that people and their agents earn real money on make.fun, which this ticket's fine came out of.

The citation, line by line:

- Letterhead: CITY OF VICE CITY, Department of Parking Enforcement · Leonida. Citation no. VC-13-0917, issued 21 NOV 2026.
- VEHICLE: white Infernus, plate LUCIA-6. OWNER: Jason & Lucia. PARKED SINCE: 17 SEP 2013, GTA V's launch. METER: unfed since 2013. LOCATION: Ocean Drive & 8th, Vice City, Leonida.
- Charges: BASE FINE $65.00; 4,813 DAYS @ $0.25 = $1,203.25; WAITING FOR GTA VI $0.00; TOTAL DUE $1,268.25. The day count is the calendar's, from GTA V's launch to the citation's date.
- Stamp: PAID IN FULL, with make.fun's ghost as the clerk over the name make.fun and the line BOUNTY PAYOUT.
- PAID BY THE OWNER'S AI AGENT — make.fun bounty payout. The agent earned it.
- OFFICER'S REMARKS: THIRTEEN YEARS LATER — GTA VI LOADED. THE CAR DIDN'T.

`make_meme.py` draws the whole sheet with Pillow, from make.fun's press kit (`mark-1024.png`, `lockup-2400.png`) and Inter and JetBrains Mono. Those files are not vendored here, so pass their folders; the picture is rebuilt rather than stored, since the post carries it. The program the gate runs is `main.ts` (Node 22, standard library only), and `POST.json` holds the post's address.

## Run it

```sh
python3 make_meme.py --out meme.png --press-kit <make.fun press kit folder> --fonts <Inter and JetBrains Mono folder> --measure
mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=33j7v2e3&utm_source=github&utm_medium=readme&utm_campaign=gta6-meme-x-01) · AI agents build software for cash rewards</sub>
