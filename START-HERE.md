# Start here — getting this onto GitHub from Claude Code

This project was built in a Cowork session that had no ability to create a
GitHub repository. A **Claude Code** session on your own machine can, because
it uses your own `gh` login.

## Before you start

1. Unzip this folder somewhere you'll find it again — `~/Projects/captivating-thoughts` is fine.
2. Open a terminal in that folder and run `claude`.
3. Check GitHub is connected: `gh auth status`. If it isn't, run `gh auth login` and pick GitHub.com → HTTPS → login with a browser.

## Paste this into Claude Code

> Read HANDOFF.md in this folder before doing anything, then publish this
> project to GitHub for me.
>
> Create a new **public** repo `captivating-thoughts` under my account
> `mklaer86-create`, commit everything here, push to `main`, and turn on
> GitHub Pages from the `main` branch at the root. Then fetch the live Pages
> URL once it's up and confirm the page actually renders — the title, the
> three doors on the home screen, and that the Google Fonts stylesheet loads.
> Tell me the URL when it's live.
>
> Do not change any of the scripture pairings, and do not answer the two open
> questions in HANDOFF.md — those are mine to decide. If you touch
> `page.html` for any reason, run `./build.sh` afterwards so `index.html`
> matches, and run `qa/qa.py` to confirm nothing broke.

## Or do it yourself

```bash
git init
git add .
git commit -m "Captivating Thoughts"
git branch -M main
gh repo create mklaer86-create/captivating-thoughts --public --source=. --remote=origin --push
gh api -X POST repos/mklaer86-create/captivating-thoughts/pages \
  -f "source[branch]=main" -f "source[path]=/"
```

Live a minute or two later at
`https://mklaer86-create.github.io/captivating-thoughts/`

## After it's live

Open the URL on a phone as well as a laptop. Check the three colour swatches in
the top corner, walk one thought through all four pages, and make sure the
journal still holds an entry after a refresh. Then send the link on.

The page is public to anyone with the URL. `LICENSE` carries a copyright line
with a name in it — change or remove that first if you'd rather stay anonymous.
