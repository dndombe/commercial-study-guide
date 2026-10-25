# Commercial Rating Study Guide

A single self-contained HTML study guide for the FAA Commercial Pilot certificate —
Single-Engine Land, Part 61, flown in a Piper PA-28-161 Warrior II.

Open `commercial-study-guide.html` in any browser. No server, no network, no
dependencies. Tap a question to reveal the answer, tick it when you own it.
Progress is kept in `localStorage` on that device.

## What's in it

**2,025 questions** across 20 sections, each tagged with where it came from:

| Source | Questions | What it is |
|---|---|---|
| CHS | 793 | CHS Flight School commercial rating study guide |
| Gold Seal | 531 | Commercial Certificate — Everything You Need To Know |
| Flight Insight | 367 | CPL At A Glance |
| Warrior POH | 297 | PA-28-161 handbook, FAA TCDS 2A13, aircraft registry |
| Gouge | 227 | Written to close gaps a real ride with this examiner exposed |
| Maneuver | 168 | The aerodynamics behind each commercial maneuver |
| Added | 168 | Written in to close a gap in all of the above |

Counts overlap: a question carried by two guides is tagged with both and shows
while either source chip is on. 1,016 are additionally marked **CHECKRIDE**,
meaning a first-hand account of a prior ride with this examiner shows the topic
was actually asked.

See **AUDIT.md** for the full source audit, the time it takes to work through,
and the list of things that can only be settled by opening the airplane.

Five tabs:

- **Study** — the question deck, searchable, filterable by source, by what's
  still to do, and by the four systems areas the examiner concentrates on.
- **Acronyms** — 217 terms and mnemonics in 15 groups, ranked in four tiers by
  how likely each is to come up on this particular ride.
- **The airplane** — a systems reference mined from the POH page by page, every
  figure carrying its source, its confidence, and whether it applies to this
  serial number.
- **Run the ride** — the prior checkride in its own order: 63 items across 11
  stages, from logbooks through to the debrief. Ticks are shared with Study.
- **Weight & balance** — a live calculator plus ten worked cases.

Twenty-four scanned figures and eight drawn diagrams are embedded as base64 and
hydrated on first open, so nothing is fetched at runtime. Each renders at the
full width of its answer panel.

## The serial number problem

This matters more than anything else in the repository.

The handbook used is Piper Report **VB-1180**, which covers PA-28-161 serials
**28-8316001 and up**. The airplane this guide was built for is serial
**28-8116257**, a 1981 airframe covered by the earlier **VB-880**.

Section 7 systems descriptions are the same airframe and carry across. The
weights do not. Maximum gross is **2,325 lb** per FAA TCDS 2A13 item XVI-A, not
the 2,440 lb printed in VB-1180, and everything that scales with gross weight —
Va, the stall speeds and therefore the airspeed indicator arc endpoints, the
whole of Section 5 performance, and the top of the CG envelope — is flagged
rather than asserted.

Every leaf in `data/pa28-systems.json` carries `carries_to_1981`, set to
`true`, `false` or `"unknown"`. Nothing marked `false` is presented as this
airplane's number anywhere in the guide.

The battery location differs between revisions: VB-1180 puts it on the
firewall, VB-880 aft of the main spar. The common online POH gives the wrong
answer for this airframe.

## Layout

```
commercial-study-guide.html   the built artifact — this is the thing you open
build/
  buildpage.py                assembles the HTML from data/ and figures/
  app.js                      the page's behaviour, injected at build time
  rec_style.css               the stylesheet
  merge_gs.py                 folds the Gold Seal pass into all.json
  merge_poh.py                folds the POH systems pass into all.json
data/
  all.json                    the question database, 2,025 items in 20 sections
  rideplan.json               the run-through: 63 ride items in order
  gouge/                      the prior-ride account, its mapping and new questions
  acronyms.json               217 ranked terms and mnemonics
  pa28-systems.json           POH systems data, sourced leaf by leaf
  wb-data.json                weight and balance limits, arms and envelope
  wb-worked.json              ten worked loading cases and 40 questions
  warrior-wb.json             FAA registry and TCDS findings
  goldseal/out*.json          per-page authoring output, with dup links
figures/                      24 WebP scans and 8 SVG diagrams
```

Rebuild with `python3 build/buildpage.py` from the repository root.

## Question identity

Progress is keyed by `md5(question_text)[:10]`. **Rewording a question orphans
its tick.** Edit an answer freely; leave the question string alone unless you
mean to reset it.

## Sources are not committed

The four source PDFs — the CHS guide, CPL At A Glance, the Gold Seal guide and
the Piper POH — are copyrighted third-party material and are excluded by
`.gitignore`. The extracted figures in `figures/` are reproductions of
copyrighted diagrams, kept here for personal study use only. **This repository
should stay private.**

## Accuracy

Nothing in here was invented. Where a figure could not be verified against a
source, the guide says so rather than guessing — see the "Still unverified"
section of the airplane tab, and the `unverified` list in
`data/pa28-systems.json`.

Two things remain genuinely open and can only be settled by opening the
airplane: the engine dash number (TCDS 2A13 approves either the O-320-D3G or
the O-320-D2A, and the registry records only "O-320 series"), and the battery
location noted above.

The empty weight and empty CG in the weight and balance tab are a **stand-in**
from a comparable Warrior II, clearly labelled as such. Replace both from
N84054's own signed weighing record before the numbers mean anything.
