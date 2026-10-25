# Audit — Commercial Rating Study Guide

Checked 25 October 2026, 30 days before the checkride. Everything below was
counted from the data, not estimated.

---

## 1. Where every question came from

**2,025 questions** across 20 sections. Each carries one or more source tags, shown
as a chip on the question and usable as a filter. Tags overlap — a question held by
two guides carries both — so the column sums to more than 2,025.

| Chip in the guide | Questions | What it actually is |
|---|---|---|
| **CHS** | 793 | *Commercial Rating Study Guide*, CHS Flight School. The original deck. |
| **Gold Seal** | 531 | *Commercial Certificate — Everything You Need To Know*, GroundSchool.com / Atlanta Flight Inc, v1.1.1, 2024. 32 pages, the guide the COM3 instructor recommended. |
| **Flight Insight** | 367 | *CPL At A Glance*. Shown as "Flight Insight" after the publisher. |
| **Warrior POH** | 297 | Piper PA-28-161 *Pilot's Operating Handbook*, Report VB-1180; FAA Type Certificate Data Sheet 2A13; FAA aircraft registry. |
| **Gouge** | 227 | Written to close gaps a first-hand account of a prior ride with this examiner exposed. |
| **Maneuver** | 168 | The aerodynamics behind each commercial maneuver. Written after the instructor flagged "lots of systems and aerodynamics related to maneuvers." |
| **Added** | 168 | Written to close a gap none of the above covered. |

1,624 questions carry a single source; 281 carry two; 115 carry three; 5 carry four.

### Two further markers, independent of source

| Badge | Count | Meaning |
|---|---|---|
| **CHECKRIDE** | 1,016 | The account of the prior ride shows this topic was actually asked. |
| **SYSTEMS** | 166 | Oil, fuel, electrical, powerplant — the four the examiner concentrates on. |
| **MANEUVER** | 168 | Maneuver aerodynamics. |
| **FIGURE** | 30 | Carries a chart or diagram. |

### Reference material, outside the question count

- **217 acronyms and terms** in 15 groups, each ranked in four tiers by how likely
  it is with this examiner. Built from Gold Seal pages 31–32 plus a sweep of the
  mnemonics used elsewhere in that guide.
- **388 sourced data points** on N84054 in the airplane tab, each carrying its POH
  section, page, confidence, and whether it applies to this serial number.
- **10 worked weight and balance cases** plus a live calculator.
- **63-item run-through** of the prior ride in its own order.

---

## 2. Figures

**32 figures, all of them rendering.** 24 scanned and 8 drawn.

| Source | Count | What |
|---|---|---|
| Gold Seal pages | 17 | Full-page renders at 170 dpi: alternate minimums, ASI markings, oxygen, icing, light gun signals, four forces, turns, airspace, night, the "Am I legal?" flowchart, METAR, TAF, thunderstorms, and the four maneuvers. |
| CHS / Flight Insight scans | 7 | Clouds, air masses, METAR weather codes, PIREP encoding, VOR service volumes, sectional legend, 91.213 decision path. |
| Drawn diagrams | 8 | Avionics, cabin heat, electrical bus, and the five maneuvers. |

All are embedded as base64 in the file — nothing is fetched at runtime. Each renders
at the full width of its answer panel; tapping opens it wider for fine print.

Three questions carry **two** figures — the Gold Seal page scan and the drawn diagram
for the same maneuver. (Until this audit the scan was silently overwriting the
drawing on chandelle, lazy eight and steep spiral, so those three never appeared.
Fixed.)

---

## 3. Source coverage — is anything missing?

**Gold Seal, pages 1–32: complete.** Every page 1–30 was inventoried concept by
concept and produced authored entries — 806 in total, no page skipped. Pages 31–32
are a flat abbreviation glossary and became the ranked acronym reference instead of
Q&A.

**The prior-ride account: 63 items, all mapped.** 55 were already well covered, 7
were thin and have been filled, 1 (NTSB Part 830) had nothing at all in the deck and
was written from scratch.

**The POH:** 388 data points extracted. 380 high confidence, 8 medium. 322 apply to
this serial number, 37 do not and are flagged as such, 29 depend on what is actually
fitted to the airframe.

**CHS and Flight Insight** were the original deck and were merged before this phase.

---

## 4. How long it takes

Measured from the real text: 22,683 words of questions and 139,375 words of answers,
162,058 words in all.

| Pass | Basis | Time |
|---|---|---|
| **Everything, once** | 180 wpm for dense technical prose, plus 8 s per card to recall and decide | **19.5 h** — about 40 min a day over the 30 days left |
| Review pass, skimming | 4 s per card | 2.2 h |
| **Checkride-confirmed subset only** (1,016 cards) | as above | **9.8 h** |
| Systems focus only (166 cards) | as above | 1.6 h |

If time gets short, the order to cut in is: **Checkride** filter first, then
**Systems**, then **Maneuver**. That is roughly 13 hours and covers everything the
account shows was actually asked plus the examiner's two stated emphases.

---

## 5. What this guide cannot tell you

These are real gaps, not oversights. Nothing was invented to paper over them, and
each one is marked in the guide where it arises.

### Settle these by opening the airplane or reading its records

1. **The weight and balance record.** The empty weight (1,463.99 lb) and empty CG
   (87.39 in) in the calculator belong to a *different* Warrior II of the same era
   and the same 2,325 lb gross. Every total in the W&B tab is provisional on them.
   Type in N84054's real two numbers and it all recomputes.
2. **A gross-weight-increase STC.** One exists for the PA-28-161 and adds 115 lb. If
   N84054 carries it, the 2,325 lb gross used throughout is wrong. Check the logs.
3. **The engine dash number.** TCDS 2A13 approves either the O-320-D3G or the
   O-320-D2A; the registry records only "O-320 series." Both are 160 hp at 2,700 rpm,
   so nothing else moves — but the data plate is the only place the answer exists.
4. **Battery location.** VB-1180 says the forward right face of the firewall;
   VB-880, which covers this serial, says aft of the main spar. They disagree, and
   the common online POH will give the wrong answer. Look.
5. **What optional equipment is fitted:** vacuum system and gyros, alternate static
   source, pitot heat, the carburetor ice detector, rear-seat shoulder harnesses,
   which ELT model, and whether the oil system has a full-flow filter or a screen
   (that one decides a 25- or 50-hour oil change interval).

### Get the right handbook

6. **VB-880 is this airplane's POH; VB-1180 was used.** Systems descriptions carry
   across unchanged and can be quoted with confidence. Weights and performance do
   not. Specifically unresolved until VB-880 is in hand: maximum ramp weight (not
   published anywhere available), maximum landing weight, Va at 2,325 lb (≈108 KIAS
   by interpolation, not a published figure), the stall speeds and therefore the
   airspeed-indicator arc endpoints, the forward CG limit at maximum weight, and all
   of Section 5 performance.
7. **TCDS 2A13 Note 27** is appended to the CG range for this serial block and its
   text was never retrieved. It may qualify the envelope.

### Things the handbook simply does not say

The guide answers these by naming the gap rather than guessing, which is the right
answer in an oral: the magneto drive arrangement, whether there is an impulse
coupling, the spark plug count and which magneto fires which plugs, the carburetor
make and model, the expected RPM drop on the carb heat check, the thermostatic
bypass or vernatherm, the crankcase breather, the battery amp-hour rating, the bus
arrangement in detail, the stall warning trigger mechanism, published glide ratio,
and separate flaps-up / flaps-down load factors. Ask the instructor for the ones
that matter to him.

### Confirm against the current ACS

8. The 3,000 ft AGL recovery floor for accelerated stalls, and the slow-flight
   tolerances used (±50 ft, ±10° heading, ±5° bank, +5/−0 kt).
9. The **three stages of a stall** are not a verbatim numbered list in any FAA
   document. They are written here as approaching/imminent, full, and recovery, from
   the Airplane Flying Handbook and AC 61-67C. If the instructor has a preferred
   phrasing, use his.

---

## 6. Errors found and corrected

Worth knowing, because two of them came from material that was handed over as
authoritative.

- **The prior candidate's crosswind reasoning is backwards.** He said he chose the
  runway with wind from the left so as to need *less* right rudder. An airplane
  weathervanes into the wind, so a left crosswind pushes the nose left and *adds* to
  the left-turning tendencies. His conclusion is defensible on component size and
  emergency-return grounds; the rudder argument is not. Flagged in the run-through.
- **That airplane had no KOEL; this one does** — Section 2.19, twelve day-VFR items.
  The ATOMATOFLAMES-only route he took is the fallback for an airplane without one.
- **A draft claimed the climbing half of a lazy eight and a chandelle underbank.**
  The FAA says the opposite: the chandelle's overbanking tendency *increases* as
  airspeed decays, and the lazy eight needs opposite aileron at the 90°. Four
  answers were rewritten before shipping.
- **Gold Seal cites BasicMed to § 91.113** (right-of-way rules). It is Part 68 and
  § 61.113(i).
- **Gold Seal's ARROW citation** omits § 91.9 and includes § 91.103, which is
  preflight action and unrelated to onboard documents.
- **Gold Seal's § 91.209** is described as sunset-to-sunrise for anticollision
  lights; they are required for all operations.
- **Gold Seal's steep spiral ACS block** prints the airspeed tolerance as "±10°". It
  is ±10 knots.
- **The deck had the white arc backwards** on multi-position flap limits, and a
  cloud figure disagreeing with its own answer on height bands. Both corrected
  earlier.

---

## 7. Integrity checks

All run against the shipped build.

| Check | Result |
|---|---|
| Duplicate question texts | 0 |
| Progress-key collisions | 0 of 2,025 |
| Empty questions or answers | 0 |
| Answers outside the 120–700 character range | 3 slightly long |
| Unknown source tags | 0 |
| Markdown artifacts in answers | 0 |
| HTML in answers | `<b>` only, 4,798 instances |
| British spellings | 0 |
| Figure references that resolve | 32 of 32 |
| Run-through references pointing at a missing question | 0 |
| External network references in the built file | 0 |
| JavaScript errors on load, all five tabs | 0 |
| Horizontal overflow at 390 px, light and dark | none |
