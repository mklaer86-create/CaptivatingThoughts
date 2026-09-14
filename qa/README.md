# QA suite

111 automated checks: every button and link in all seven views, the four-page
flow forwards and backwards, save guards, persistence, all four colour
palettes, WCAG AA contrast across three palettes and system dark, no
horizontal scroll at 320 / 390 / 1280, focus rings, aria state,
reduced-motion, and the shape of every Bible Hub link.

## Run it

```bash
pip install playwright --break-system-packages     # once
python3 -m playwright install chromium             # once, unless a browser is preinstalled

# build the standalone page the tests load
cd ..
{ printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'; cat page.html; printf '\n</body>\n</html>\n'; } \
  | awk 'BEGIN{d=0} /^<\/style>$/ && !d {print; print "</head>"; print "<body>"; d=1; next} {print}' > /tmp/qa.html

python3 qa/qa.py
```

Expected: `PASS 111   WARN 0   FAIL 0`.

Google Fonts is blocked inside the Anthropic sandbox, so runs there render with
fallback faces and log `ERR_TUNNEL_CONNECTION_FAILED`. That is the sandbox, not
the page. Check webfont rendering by eye on the live URL.
