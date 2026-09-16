# Holding Your Thoughts Captive

A small, free web tool for challenging negative self-talk — one page, no accounts, no tracking, nothing sent anywhere.

> "We demolish arguments… and we take captive every thought to make it obedient to Christ." — 2 Corinthians 10:5

It's built on the **thought record**, the core exercise of cognitive behavioral therapy, rewritten to be usable by someone who is struggling to put words to anything. Scripture sits in the margin of every page, and a verse library is grouped by what actually hurts rather than by book order.

Built for a premed student and for anyone else who needs it.

## Using it

Open `index.html` in any browser, or visit the published page. Nothing to install.

It opens on three doors, because someone who is struggling often can't articulate what's wrong yet. Use any of them, in any order, and stop wherever you like — it also works as a set of prompts for a paper journal rather than a replacement for one:

- **I'm crashing — I need grounding** — a counted breath (four in, hold, six out, eight breaths), Philippians 4:8–9, a prompt to find one thing to praise God for from Psalm 42, and five small physical things. Nothing to figure out.
- **I'm struggling with my thoughts** — four pages: what happened and the sentence in your head → describe the mixture of what you're feeling → when your inner voice turns on you → an honest review for a healthier me. Every field is skippable.
- **I just want to dump where I'm at** — a blank page, with a prompt on tap if you're stuck.

Underneath: everything you've written, the eleven shapes your inner voice takes when it turns on you, and the verse library grouped by what hurts.

There's also a small **Quick Remap** button below the three doors — not a fourth door, just a shortcut for when you already know the shape and want the reframe without the four pages: every shape's thought, its truer sentence, and a verse, all on one page.

A language switcher in the top corner — English or Español. It translates everything the app says; Bible verses stay in English (ESV) in both languages until a real named Spanish translation is added, rather than a machine translation of scripture. Your choice is remembered.

Four colour settings in the top corner — match my device, Rose, Harbor, Dusk. Rose is the default until you pick something else; it remembers whichever you chose.

It has its own icon — three rings pulsing out from a centre, a still frame of the breath-circle grounding tool — for the browser tab and for "Add to Home Screen" (iOS Safari) or "Install app" (Android/Chrome), so it opens full-screen like an app rather than a browser tab.

## Privacy

Journal entries are saved with `localStorage` — they stay in the browser they were written in. They are never uploaded, and there is no server, no accounts, no analytics, and no third-party script other than the Google Fonts stylesheet. Clearing browser data clears the journal — and iPhone/iPad Safari can do this on its own after about a week of the page being closed — so use **Save a backup file** on the journal page now and then. It downloads everything as a small JSON file; **Load a backup file** reads one back in, merging it with whatever's already there rather than overwriting it. **Copy all** and **Print** still work for a plain-text copy, but only a backup file can be loaded back in.

## Publishing it on GitHub Pages

```bash
git init
git add .
git commit -m "Holding Your Thoughts Captive"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/captivating-thoughts.git
git push -u origin main
```

Then in the repository: **Settings → Pages → Build and deployment → Source: Deploy from a branch**, branch `main`, folder `/ (root)`. In a minute or two it's live at `https://YOUR-USERNAME.github.io/captivating-thoughts/`.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The whole app. Self-contained — this is the only file that has to be served. |
| `page.html` | The same page without the `<html>`/`<head>`/`<body>` wrapper, for publishing as a Claude Artifact. |
| `build.sh` | Regenerates `index.html` from `page.html`. Run it after editing `page.html`. |
| `LICENSE` | MIT. |
| `HANDOFF.md` | Full project context: decisions made, what's still open, how to pick this up in a new session. |
| `qa/qa.py` | Playwright test suite across flows, palettes and widths — run it for the current check count. |
| `docs/scripture-decisions.md` | The verses still awaiting a ruling. |
| `manifest.json` | Web app manifest so browsers offer "Install" / "Add to Home Screen" with the app's own icon. |
| `icons/icon.svg` | Source vector for the app icon (breath pulse rings). Edit this, not the PNGs. |
| `icons/*.png` | Generated from `icon.svg` — the home-screen icon (`apple-touch-icon.png`), manifest icons, and the tab favicon. See `HANDOFF.md` for how to regenerate them after editing the SVG. |

Edit `page.html` and run `./build.sh`, or edit `index.html` directly if you're only ever using the GitHub version.

## Making it yours

Everything worth changing lives near the top of the `<script>` block in one place. Each of these exists as an `_EN` and an `_ES` array (same shape and order in both); `SHAPES`/`FEELINGS`/`VERSES`/`STEPS`/`PROMPTS` are the bindings the rest of the app actually reads, swapped by the language switcher:

- `SHAPES` — the eleven shapes, each named as the sentence a person actually thinks, with an example, a note on why it's the example, and the reframe.
- `FEELINGS` — the feeling chips, each tagged with a verse group.
- `VERSES` — the verse library. Add groups, reorder them, swap the translation. Verse text/reference/link stay English (ESV) in both languages — only the app-authored context caption is translated.
- `STEPS` — the four pages: heading, opening line, margin verse, and the fields.
- `PROMPTS` — the writing prompts.
- `STRINGS.en` / `STRINGS.es` — every other piece of fixed UI text (buttons, headings, messages), looked up with `T(key)`.

Colours are CSS custom properties at the top of the `<style>` block: one block per palette (`[data-skin="rose"]`, `"harbor"`, `"dusk"`), plus the no-attribute default that follows the device. Add a fourth palette by copying a block and adding a swatch button.

Scripture is ESV throughout, quoted whole, with every reference linking to its Bible Hub page.

## A note

This is a self-help tool, not therapy, and it is not a substitute for it. If the thoughts are constant, if they're about hurting yourself, or if you can't get out from under them — tell a real person today. In the US you can call or text **988** any hour of any day.

Read the verses in their own chapters; a verse alone says less than a verse in its paragraph. Every reference in the tool links to its Bible Hub page for exactly that reason.

## Credits

The thought-record structure is standard CBT (Beck, Burns, and everyone since). The eleven shapes follow the common clinical set of cognitive distortions, renamed as the sentences people actually think, informed by [Calm's guide to negative self-talk](https://www.calm.com/blog/negative-self-talk).

MIT licensed — copy it, change it, share it.
