# Holding Your Thoughts Captive

A small, free web tool for challenging negative self-talk — one page, no accounts, no tracking, nothing sent anywhere.

> "We demolish arguments… and we take captive every thought to make it obedient to Christ." — 2 Corinthians 10:5

It's built on the **thought record**, the core exercise of cognitive behavioral therapy, rewritten to be usable by someone who is struggling to put words to anything. Scripture sits in the margin of every page, and a verse library is grouped by what actually hurts rather than by book order.

Built for a premed student and for anyone else who needs it.

## Using it

Open `index.html` in any browser, or visit the published page. Nothing to install.

It opens on three doors, because someone who is struggling often can't articulate what's wrong yet. Use any of them, in any order, and stop wherever you like — it also works as a set of prompts for a paper journal rather than a replacement for one:

- **I'm crashing — I need grounding** — a counted breath (four in, hold, six out, eight breaths), Philippians 4:8–9, a prompt to find one thing to praise God for from Psalm 42, and five small physical things. Nothing to figure out.
- **I'm struggling with my thoughts** — four pages: what happened and the sentence in your head → describe the mixture of what you're feeling → what that thought is doing → an honest review for a healthier me. Every field is skippable.
- **I just want to dump where I'm at** — a blank page, with a prompt on tap if you're stuck.

Underneath: everything you've written, the ten shapes a hard thought takes, and the verse library grouped by what hurts.

Four colour settings in the top corner — match my device, Rose, Harbor, Dusk — and it remembers which you chose.

## Privacy

Journal entries are saved with `localStorage` — they stay in the browser they were written in. They are never uploaded, and there is no server, no analytics, and no third-party script other than the Google Fonts stylesheet. Clearing browser data clears the journal, so use **Copy all** or **Print** to keep a lasting copy.

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
| `qa/qa.py` | Playwright test suite — 111 checks across flows, palettes and widths. |
| `docs/scripture-decisions.md` | The verses still awaiting a ruling. |

Edit `page.html` and run `./build.sh`, or edit `index.html` directly if you're only ever using the GitHub version.

## Making it yours

Everything worth changing lives near the top of the `<script>` block in one place:

- `SHAPES` — the ten shapes, each named as the sentence a person actually thinks, with an example, a note on why it's the example, and the reframe.
- `FEELINGS` — the feeling chips, each tagged with a verse group.
- `VERSES` — the verse library. Add groups, reorder them, swap the translation.
- `STEPS` — the four pages: heading, opening line, margin verse, and the fields.
- `PROMPTS` — the writing prompts.

Colours are CSS custom properties at the top of the `<style>` block: one block per palette (`[data-skin="rose"]`, `"harbor"`, `"dusk"`), plus the no-attribute default that follows the device. Add a fourth palette by copying a block and adding a swatch button.

Scripture is ESV throughout, quoted whole, with every reference linking to its Bible Hub page.

## A note

This is a self-help tool, not therapy, and it is not a substitute for it. If the thoughts are constant, if they're about hurting yourself, or if you can't get out from under them — tell a real person today. In the US you can call or text **988** any hour of any day.

Read the verses in their own chapters; a verse alone says less than a verse in its paragraph. Every reference in the tool links to its Bible Hub page for exactly that reason.

## Credits

The thought-record structure is standard CBT (Beck, Burns, and everyone since). The ten shapes follow the common clinical set of cognitive distortions, renamed as the sentences people actually think, informed by [Calm's guide to negative self-talk](https://www.calm.com/blog/negative-self-talk).

MIT licensed — copy it, change it, share it.
