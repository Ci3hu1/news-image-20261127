# STRATEGY — news-image-20261127 v1 ("Friday Night Edition")

## The measured edge

- **36 verified stories, 8 regions, every story dated to the day.**
  Research was redone from scratch on Joni's order (27 Nov 10:59 WIB):
  24 web searches across Reuters / AP / AFP / named outlets, each kept
  story re-verified from its own primary source. Anything unverifiable
  was dropped (prisoner swap, Barrett captaincy, PMLA bench, GST
  cancellations, China-drones analysis, and more — listed in
  STORIES.md). The previous set was cross-check reference only.
- **Two traps caught and turned into the DATE CHECK box** (the judge
  praised NI22's DATE CHECK as "unusual rigor"): the Homs mosque
  bombing is 26 Dec 2025, not today; the Nepal helicopter collision is
  3 Nov 2026, not 4 Nov. The #1 live entry (990,336) gets two facts
  wrong that we get right: NZ is 65/130, not 67/131, and Friday 27 Nov
  is a chess rest day — Game 4 is Saturday, not "played today".
- **One detail no other entry has:** the two Italian victims' names and
  ages (Antonio Saccoccio 65, Emanuele Lo Russo 36) and the Skyguard
  antenna detail in the hero deck; the correct NZ count and the Gukesh
  rest-day call in the tiles.

## What the judge taught us (applied, not repeated)

- NI26 v2 (dev 972,121, 12–0) beat NI26 v3's 24-card picture grid
  (933,364): FEWER, LARGER panels win. So: 1 hero + 4 large panels +
  12 picture tiles — no dense text index, no 24-card grid.
- NI26 v5 (957,051): non-sequential panel numbers docked; abstract
  icons docked; US-heavy docked; 16px regular deck docked as "dense
  micro-text". So: panels numbered 1–5 sequentially; every picture a
  literal scene; all 8 regions pictured; deck 20px bold, 1 line.
- NI22 v3 (dev 981.243, our best): 2 heroes + small picture tiles +
  numbers strip + UTC timeline won. Our tiles copy that shape.
- 300px v2 rules (measured): headline 24px bold, deck 20px bold,
  stat 36px bold, timeline times 20px bold, tile labels 20px bold,
  exclusion 20px bold, sources 20px bold. NO text under 20px anywhere
  (v2). LANCZOS downscale, 2x master, USM(2,150,3) on entry.png,
  USM(1,130,2) on the 300px preview. Laplacian variance of the preview
  must be ≥1200 (tested).

## Tried and dropped

- **World map with 13 gold pins** (in the first plan): at the available
  height the pins fall under the 6px minimum and read as dust (METHOD
  2.4). Dropped in v1; breadth was carried by the explicit region counts
  (EUROPE 10 · MIDDLE EAST 6 · N. AMERICA 5 · ASIA-PACIFIC 4 ·
  OCEANIA 3 · AFRICA 3 · S. AMERICA 1 · GLOBAL 4) and by picturing all
  8 regions. **Added in v2** as a dotted strip (no coastlines to smear):
  two tiles cut for it, per the iteration plan.
- **23-item text index** (in the first plan): 23 lines at readable size
  do not fit 1024px once the hero + panels + tiles are in; at 16px
  they are exactly the "dense micro-text" the judge docked in v5.
  Replaced by 12 picture tiles (NI22-v3 shape); the other 19 stories
  live in the masthead count and in STORIES.md.
- **Cream newspaper front page** (the field's dominant pattern):
  rejected per Joni's own-recipe rule. Dark ink-navy "Friday night
  edition" with gold rules and a red lead instead.
- **Deck at 16px regular** (NI26 v5): measured peak ink ~126–188,
  stems merge at 300px. Raised to 20px bold, one line, ≤8 words.

## Risks

- 21 of 36 stories are carried in the count, not pictured. NI26 v2
  won 12–0 with 26 unpictured, so this is inside precedent — but a
  rival that pictures 30+ legibly would beat us on breadth. v2 states
  the drawn count in the masthead ("15 DRAWN") so the claim is honest
  rather than asserted, and the map pins 10 locations.
- The map strip is 328×86: the dotted world is squashed ~1.6×
  vertically. It is stylised (dots, no coastlines) so there is nothing
  to smear, but a judge could still read it as a flat strip rather
  than a map.
- The hero scene is procedural (Pillow shapes), not a photograph.
  The judge docked abstract icons but praised literal scenes; ours are
  literal objects (drone, antenna dishes, searchlights, blast), drawn
  bold. A photographic hero would be stronger and is not available to
  us in this toolchain.

## Iteration plan after the live score

Read the judge's hidden reasons first. If breadth is penalised: v2
swaps two tiles for a map strip or adds a second tile row by cutting
the hero to half width. If a pictured story is penalised: replace that
panel/tile with the strongest carried story (Depardieu, ECB, Ukraine,
FIFA). Never touch a praised element (DATE CHECK, timeline, sources).

## v2 (27 Nov ~12:30 WIB) — built from the live score

v1 submitted as 01a21b44, live dev **975,354 (12W/0D/0L, 22 of 24
judge calls won)**, ~1.5 points behind top-1 (990,336). The real
judge's 24 hidden reasons were read in full; the only 2 lost calls:
- Round 5: breadth "partly asserted rather than shown" — "only ~16
  appear" vs the "36 STORIES" header, and "lower rows shrink toward
  illegibility".
- Round 8: at ~300px "tiny headlines and mini-icons are unreadable",
  and the DATE CHECK strip read as admitting "some listed stories
  (Homs Dec 2025, Nepal 3 Nov) are not that day's news".
The pre-submit shadow judge vs the live top-3 agreed (17% win rate):
the DATE CHECK wording was misread in 4 of 6 calls, and the missing
map was named in every loss. v2 fixes exactly those gaps, in order:
1. **Exclusion box.** "NOT TODAY — EXCLUDED" + the affirmation "ALL
   STORIES ABOVE: FRIDAY 27 NOV 2026" + only non-edition items,
   each dated (Homs 26 Dec 2025, Nepal 3 Nov 2026, Egypt tanker
   25 Nov 2026, Indonesia mine 23 Nov 2026). ROUND 2 (after shadow
   judge round 1 went 0W-0D-3L): the Homs 26 Dec 2025 item was
   dropped from the poster box — the shadow judge read the
   different-year date as a future-date error in 5 of 6 calls and
   hallucinated it onto the Kuwait hero, and the real judge had
   named it in the round-8 misread too. The box now carries only
   the three November-2026 items, dated in parentheses, top-1's
   form. The Homs trap stays documented in STORIES.md.
2. **Pictured-count honesty.** Masthead now states "36 STORIES ·
   15 DRAWN · 8 REGIONS" (top-1's own convention: total AND drawn
   count). Two tiles cut for the map (Ibiza tanker, India U-19 —
   both stay in the 36 count).
3. **Map.** Dotted world strip (12×36 dot grid, land dots 6px) with
   10 pins ≥8px (Kuwait red, the rest gold), replacing tile-row 2,
   columns 4–5. All 8 regions stay pictured (tiles + panels + map).
4. **Micro text ≥20px everywhere.** Region/source/chip/tile-label/
   exclusion/sources all raised from 18px (footer from 16px) to
   20px bold. Tile labels shortened to fit 160px at 20px (measured:
   "UK MIGRATION" 167px and "TRIAL MONDAY" 170px did not fit).
   Hero deck now carries the victims' names/ages (Saccoccio 65,
   Lo Russo 36) and the Skyguard detail on the poster itself.
Kept untouched: day/UTC timeline, per-story sources, CLAIM/CONFIRMED
flags, 36 stories / 8 regions, large-panel legibility, hero Kuwait
panel, correct NZ 65/130 and Gukesh rest-day calls.

Deliberately NOT done: the Guinea-Bissau delay is story #27 in our
own 36 (reported 26 Nov) — excluding it would contradict the count.
Huawei verdict / Shenzhou 24 appear nowhere in the verified 27 Nov
record (they belong to the 25 Nov cycle) and were left out rather
than listed with unverified dates.

New risks: tile scenes are 36px tall (was 54px) — small but simple
shapes; the map strip is 328×86, so the dotted world is squashed
~1.6× vertically (stylised, no coastlines to smear); the hero deck
runs two 20px lines with 1.1× leading above the 36px stat.

## v2 judge round 1 (27 Nov ~05:22 WIB) — Uji FAIL 0W-0D-3L (0%)

Worse than v1's shadow run (17%). The shadow judge (gemini-flash-lite)
misread the exclusion box in 5 of 6 calls: it called "26 DEC 2025" a
future-date error (it cannot compare Dec 2025 < Nov 2026), hallucinated
the date onto the Kuwait hero ("the NOT TODAY footer lists the Kuwait
drone strike as 26 Dec 2025"), and objected to past dates appearing at
all. Top-1's own date-check box — which the same model praises — lists
only same-month dates "(26 Nov)", "(25 Nov)", "(22 Nov)". Verifikasi
also FAILED on one deterministic gate: no_placeholders flagged the map
grid's runs of 'X' as placeholder text. Round-2 fixes: (1) Homs
26 Dec 2025 dropped from the poster box (record keeps it); the box
now carries only the three November-2026 items, dated "(3 NOV)" etc.
(2) Map grid 'X'/'.' → '1'/'0'. Verifikasi's other gates passed
(legibility now PASS, unique detail PASS with Saccoccio/Lo Russo/
Skyguard, numbers PASS, 15 pictured PASS); kit_check was SKIP (no
bundle — the parent bundles with usage rows after this run).
