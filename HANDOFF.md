# Handoff — Captivating Thoughts

Everything a new session (or a new person) needs to pick this up. Read this first.

---

## What this is

A single self-contained HTML page: a free, gentle tool for challenging negative self-talk, built on the CBT **thought record** with scripture alongside. Written for **Michelle Klaer** and for her daughter, who is going through a premed program — so the language is aimed at a struggling nineteen-year-old, not at a clinician.

The app's on-screen title is **Holding Your Thoughts Captive** (from 2 Corinthians 10:5). The repository is named `captivating-thoughts`. If those should match, change the `<title>` in `page.html` and the `<h1>` in the home section, then rerun `./build.sh`.

**No accounts, no server, no analytics, no tracking.** Journal entries live in `localStorage` on the reader's own device. The only external request is the Google Fonts stylesheet. A login with server-side storage was proposed and deliberately turned down — see the "no login" decision below. Durability across devices/data loss is handled instead by a manual backup-file export/import (journal view: **Save a backup file** / **Load a backup file**), which keeps the same zero-server promise.

---

## Current state

Finished and QA'd, and live on GitHub Pages at `https://mklaer86-create.github.io/CaptivatingThoughts/`. Automated checks pass with no failures and no console errors (run `qa/qa.py` for the current count — it grows as features are added).

### Structure

Three doors on the home screen, because someone at their lowest often cannot articulate what is wrong:

| Door | What it does |
| --- | --- |
| **I'm crashing — I need grounding** | A counted breath (4 in / 2 hold / 6 out, eight breaths, with a visible count so it is finite), Philippians 4:8–9, a praise prompt built on Psalm 42:5–6, five small physical things. No inputs — nothing to figure out. |
| **I'm struggling with my thoughts** | Four pages. 1) What happened + the sentence in your head, with a worked example. 2) Describe the mixture of what you're feeling, plus why that matters. 3) What is that thought doing (the eleven shapes) — page three now recaps what you wrote on page one so you don't have to tab back. 4) An honest review for a healthier me — provable facts, what the feeling left out, what someone who loves you would say, the truer sentence, what to tell yourself next time, one small next step, a verse, and the after reading. |
| **I just want to dump where I'm at** | A blank page with a prompt on tap. |

Underneath: the journal, the eleven shapes as a reference, and the verse library.

Also on the home screen, but deliberately not a fourth door — a small dashed pill button below the three, labeled **Quick Remap**: "Skip straight to the reframes." It's for someone who already knows which shape they're in and just wants the payoff without the four-page walk-through — one static page listing all eleven shapes' thought → reframe → verse, no inputs, no interaction. Content is generated from the same `SHAPES` array (`renderRemap()`/`remapHTML()` in `page.html`), so editing a shape's `truer` or `v` updates both places automatically. Michelle's own framing when she asked for it: "a map to a better reframe... when I'm stuck in this place."

### Decisions already locked in — do not undo these without asking

- **Scripture is ESV**, quoted **whole** (no ellipses), with every reference linking to its Bible Hub page (`https://biblehub.com/esv/<book>/<chapter>-<verse>.htm`). Every verse in the app was pulled verse-by-verse from Bible Hub rather than from memory. **Do the same for anything you add.**
- **The eleven shapes are named as the sentence the person is actually thinking** ("This is going to ruin everything", "It's my fault"), not as clinical categories ("catastrophizing", "personalizing"). This was a deliberate, tested change — the category names were unpickable for someone mid-spiral. Each shape shows: the assumption → an example → why that example gives it away → the reframe. The eleventh, "I feel completely worthless" (`labeling`), was added at Michelle's request to cover relationship-shaped hurt rather than only school — its verse reuses Psalm 139:14, already vetted elsewhere in the app, rather than sourcing a fresh Bible Hub pairing.
- **Nothing is called an "error."** Telling someone in despair that their thinking is in error lands as one more failure.
- **Every field is skippable** and the flow can be abandoned at any point.
- **Four colour palettes**: Rose, Harbor, Dusk, match-my-device. **Rose is the default** for a first-time visitor (Michelle's request); match-my-device is still there but no longer the fallback. Remembered in `localStorage` once someone picks one. Explicit choice always beats the host's `data-theme` stamp and `prefers-color-scheme`.
- **The tool pairs with a paper journal** rather than replacing one — said on the home screen and on the writing pages.
- **The 988 line stays in the footer**, and the tool never claims to be therapy.
- **No login, no account, no server-side storage.** Proposed (a way to keep entries past 90 days / across devices) and turned down: a server means someone — host, breach, subpoena — could read a struggling teenager's worst thoughts, which is a real cost even with good intentions, and it turns a free static site into something with ongoing hosting and auth to maintain. The durability problem is solved instead with a manual, local backup file (see below) — same zero-server guarantee, no new attack surface.
- **The app icon is a breath pulse, not a feather.** A feather/quill/cupped-hands round was shown first and rejected outright as the wrong motif — not a color or boldness problem, the symbol itself. Breath (the counted-breath grounding circle, already the app's first door) was Michelle's redirect, tested as three options — pulse rings, a wave curve, and the same rings in Harbor blue — and she picked the Rose pulse rings. **If you're asked to touch the icon again, don't default back to a feather.**

### Backup files

Journal view has **Save a backup file** (downloads `captivating-thoughts-backup-YYYY-MM-DD.json`) and **Load a backup file** (file picker, reads one back in). Format: `{app:"captivating-thoughts", version:1, exportedAt:<ISO date>, entries:[...]}` — `entries` is the same array shape stored under the `tet.entries.v2` localStorage key. Loading a file **merges** by entry `id` rather than replacing — anything already present is left alone, so loading an old backup can't erase newer entries written since.

Downloads can be inert inside an embedding iframe (see the Claude-artifact note under Publishing) — there's no reliable way to detect that from script, so Save a backup file always also drops the same JSON into a read-only textarea underneath as a copy-and-paste fallback, every time, whether or not the download itself worked.

---

## Still open — two builds waiting on scripture text, one deferred decision

### 1. The verse docket — mostly worked through

See `docs/scripture-decisions.md` for the full record. As of 2026-09-15, Michelle has ruled on fourteen items: the title verse kept; Jeremiah 29:11 → Psalm 31:15 and Galatians 1:10 → Proverbs 29:25 both swapped; Romans 8:1 cut from both its spots; 1 Samuel 16:7 and Micah 7:8 cut outright; Joshua 1:9 kept despite overlap; Isaiah 1:18 restored; 2 Corinthians 10:12 left out; Philippians 4:6–7 added to "worn out"; Galatians 6:8–9 shown as the fuller pair; Romans 12:1–2 expanded in step four; and two brand-new additions from Michelle's own devotional reading — Romans 5:3–5 (in both "after you've failed" and "need courage") and Matthew 5:3 (in "not enough"). Every verse in the app now also carries a one-line context caption.

The live review sheet is a Claude artifact called **The Verse Docket** at
`https://claude.ai/artifact/GFV9R7Fwn8gsfAd6hs6V21`
Its decisions are stored in that artifact's database at collection `review`, document `decisions` — readable with the Artifact tool's `read_db`, writable with `write_db`. **Note the docket's own "spine" section describes a six-step flow; the app has had four steps for a while now, so that section is stale relative to the live app — read it for the verse-level notes, not the step structure.**

### 2. Two builds are scoped but blocked on exact scripture text

Both were pulled from Michelle's own comments in the docket, and both got a scope decision from her, but neither is built yet because the current session's environment can't reach Bible Hub directly — ask Michelle to paste the exact ESV text (she's done this before, e.g. for Psalm 31:15) rather than writing it from memory:

- **Ephesians 6:16 → the fuller armor passage.** Decided range: **6:11–16**. Currently only v.16 is in the app (in "afraid"). Need vv. 11–15's exact text to expand it.
- **A new fourth home-screen door for 1 Kings 19 (Elijah at Horeb).** Decided: a separate door from the existing "I'm crashing" grounding door (that one is untouched), breathing exercise plays *before* the story starts, and the story runs through God's full response and instructions (**vv. 15–18**), not stopping at the whisper (v.12–13). Need the exact text for the full passage (roughly vv. 3–18) and door copy (title/subtitle, matching the voice of the other three: "I'm crashing," "I'm struggling with my thoughts," "I just want to dump where I'm at").

### 3. The framing question — deferred by Michelle

Michelle wrote: *"the attack of our minds is the enemy trying to confuse and discourage us,"* and asked for Ephesians 6:16 (the shield of faith, now in the "when you're afraid" group, soon to be part of the fuller armor passage above). Whether the tool should **say** that — name a negative thought as spiritual attack — is undecided. When asked directly, Michelle said: *"Let's wait and log this and come back later."* **Do not decide this or bring it up unprompted — she'll raise it again when ready.**

The tension, in her words and mine, preserved for whenever she picks this back up: naming it as attack has real force and is where Ephesians 6 leads. It also has a cost — if a thought is an attack, a bad day can start to feel like a spiritual failure, and for a student already prone to self-blame that adds a second layer. Exhaustion, a chemical imbalance and a brutal semester are not the enemy, and a tool that implies otherwise can talk someone out of getting help. The standing recommendation is to name it plainly **once**, in an opening note, and let the four steps stay practical. **Her call, not yours.**

---

## Files

| File | What it is |
| --- | --- |
| `START-HERE.md` | How to get this onto GitHub from a Claude Code session, with a paste-in prompt. |
| `index.html` | The whole app, standalone. The only file that has to be served. |
| `page.html` | The same page without the `<html>/<head>/<body>` wrapper — this is the source of truth, and what gets published as a Claude artifact. |
| `build.sh` | Regenerates `index.html` from `page.html`. **Run it after every edit to `page.html`.** |
| `qa/qa.py` | The Playwright test suite. |
| `docs/scripture-decisions.md` | The open verse questions. |
| `.nojekyll` | Stops GitHub Pages running the files through Jekyll. |
| `manifest.json` | Web app manifest — name, theme colour, and the two PNG icons — so Chrome/Android offer "Install app" / "Add to Home Screen" with the app's own icon rather than a screenshot of the page. |
| `icons/icon.svg` | Source vector for the app icon — three concentric rings around a solid centre, a still frame of the in-app breath circle mid-expand (the counted-breath grounding tool, not a borrowed metaphor). Went through two review rounds with Michelle first — a feather/quill/cupped-hands round was rejected outright as the wrong motif; breath was her direction, and this ring pairing ("Pulse, Rose") was her pick over a wave-curve and a Harbor-blue recolour. Edit this, then regenerate the PNGs (see below). |
| `icons/icon-512.png`, `icons/icon-192.png` | Rasters of `icon.svg` for `manifest.json`. |
| `icons/apple-touch-icon.png` | 180×180 raster for iOS "Add to Home Screen" — Safari looks for this via the `<link rel="apple-touch-icon">` in `page.html`, not the manifest. |
| `icons/favicon-32.png` | Browser-tab favicon. |

**Edit `page.html`, never `index.html`.** `index.html` is generated.

### Regenerating the icon PNGs after editing `icons/icon.svg`

There's no build script for this (it's a one-off, unlike `build.sh`) — render the SVG in a real browser at each exact target size, since resizing a raster afterward softens it:

```python
from playwright.sync_api import sync_playwright
html = '<!doctype html><html><head><style>html,body{margin:0;padding:0;width:100%;height:100%}svg{display:block;width:100vw;height:100vh}</style></head><body>' + open("icons/icon.svg").read() + '</body></html>'
open("/tmp/icon_render.html","w").write(html)
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for size, out in [(512,"icons/icon-512.png"),(192,"icons/icon-192.png"),(180,"icons/apple-touch-icon.png"),(32,"icons/favicon-32.png")]:
        p = b.new_page(viewport={"width":size,"height":size})
        p.goto("file:///tmp/icon_render.html")
        p.screenshot(path=out, clip={"x":0,"y":0,"width":size,"height":size})
    b.close()
```

The SVG must not have fixed `width`/`height` attributes on the root `<svg>` (only `viewBox`) — Chromium won't scale a fixed-size SVG down to a small viewport, it just crops the top-left corner, which is a silent, easy-to-miss failure mode (ask if you don't believe it — it happened once already).

---

## Publishing

### GitHub Pages

```bash
git init
git add .
git commit -m "Captivating Thoughts"
git branch -M main
git remote add origin https://github.com/mklaer86-create/captivating-thoughts.git
git push -u origin main
```

Then **Settings → Pages → Deploy from a branch**, `main`, `/ (root)`. Live at
`https://mklaer86-create.github.io/captivating-thoughts/`

**Note for an agent session:** creating the repo requires GitHub access that a default Cowork session does not have — the token is bound to pre-approved repositories, and `POST /user/repos` is refused. Either the repo is created by hand in the browser first and the session granted access to it, or the whole thing is uploaded through GitHub's web "upload an existing file" flow.

### As a Claude artifact

Publish `page.html` with the Artifact tool. The current one is at
`https://claude.ai/artifact/6z347Bes8dNy2JBRMEgf6R` — pass that as `url` to update it rather than creating a duplicate. Favicon 🪶, and it should stay that emoji.

Two things behave differently inside the artifact frame than in a plain browser: the clipboard may be blocked (the Copy button falls back to a select-and-copy box), and viewer-initiated downloads are inert — which is why export is copy-and-print rather than a download link.

---

## Running the tests

```bash
pip install playwright --break-system-packages   # if needed
python3 qa/qa.py
```

The script expects the built standalone page at `/tmp/qa.html`. Generate it with:

```bash
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'; cat page.html; printf '\n</body>\n</html>\n'; } \
  | awk 'BEGIN{d=0} /^<\/style>$/ && !d {print; print "</head>"; print "<body>"; d=1; next} {print}' > /tmp/qa.html
```

It covers: every button and link in all seven views; the four-page flow forwards, backwards and via Skip, checking that text, chips, sliders and shape selections survive navigation both ways; the save guards; the free-write flow; delete; persistence across reload; all four palettes applying, persisting and re-applying after reload; **WCAG AA contrast on every visible text element across three palettes × six views plus system dark**; no horizontal scroll at 320 / 390 / 1280; keyboard focus rings; `aria-pressed` on every toggle; reduced-motion; a double-click on Next not skipping a page; long input not breaking layout; and every Bible Hub link matching the correct URL shape.

**Two bugs it has already caught, so keep it in the loop:**
1. A dark-mode rule repainted the outlined buttons the same colour as the background — every secondary button was invisible in Dusk. Fixed with an `--on-accent` token rather than a per-theme override; don't reintroduce `.btn { color: ... }` overrides inside a theme block.
2. `--ink-3` failed AA in all three palettes, including the footer that carries the 988 line.

Google Fonts is blocked inside the Anthropic sandbox, so local test runs render with fallback faces. The layout holds either way, but webfont rendering has never been verified in an automated run — check it by eye on the live URL.

---

## Voice

If you write copy for this, match what's there. Warm, plain, short sentences. Never chirpy, never clinical, never a lecture. It assumes the reader is intelligent and having a terrible night. It says things like *"You are allowed to be at the sleep-and-food stage"* and *"It does not have to have moved. If it hasn't, that's information, not failure — and it's worth telling someone."*

Do not add emoji. Do not add exclamation marks. Do not tell the reader how to feel.
