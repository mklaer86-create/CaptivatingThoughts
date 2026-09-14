#!/bin/sh
# Wraps page.html (the Claude Artifact source) into a standalone index.html for GitHub Pages.
{
  printf '<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
  printf '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
  printf '<meta name="description" content="A guided tool for challenging negative self-talk, naming thinking errors, and journaling toward a truer sentence, with scripture alongside each step.">\n'
  printf '<meta name="color-scheme" content="light dark">\n'
  cat page.html
  printf '\n</body>\n</html>\n'
} > index.html.tmp
# move the <body> open tag into place, right after the closing </style>
awk 'BEGIN{done=0} /^<\/style>$/ && !done {print; print "</head>"; print "<body>"; done=1; next} {print}' index.html.tmp > index.html
rm index.html.tmp
echo "built index.html"
