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
  stat 36px bold, timeline times 20px bold, tile labels 18px bold,
  DATE CHECK 18px bold, footer 16px bold 1 line. LANCZOS downscale,
  2x master, USM(2,150,3) on entry.png, USM(1,130,2) on the 300px
  preview. Laplacian variance of the preview must be ≥1200 (tested).

## Tried and dropped

- **World map with 13 gold pins** (in the first plan): at the available
  height the pins fall under the 6px minimum and read as dust (METHOD
  2.4). Dropped; breadth is carried by the explicit region counts
  (EUROPE 10 · MIDDLE EAST 6 · N. AMERICA 5 · ASIA-PACIFIC 4 ·
  OCEANIA 3 · AFRICA 3 · S. AMERICA 1 · GLOBAL 4) and by picturing all
  8 regions. If the live judge names the map, v2 adds it by cutting
  two tiles.
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

- 19 of 36 stories are carried in the count, not pictured. NI26 v2
  won 12–0 with 26 unpictured, so this is inside precedent — but a
  rival that pictures 30+ legibly would beat us on breadth.
- No map. The recipe lists a map among winner elements; NI26 v5
  dropped it and still scored 957k, but the drop is unproven either way.
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
