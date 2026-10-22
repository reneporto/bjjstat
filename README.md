# bjjstat.com

Jiu-Jitsu by the numbers. Static site for [bjj.stat](https://www.instagram.com/bjj.stat/).

- `build.py` — all pages and posts (content lives in the `post(...)` calls). Run `python3 build.py` to regenerate `docs/`.
- `assets/` — CSS, fonts (Space Grotesk, JetBrains Mono), images and post media.
- `static/` — files copied to the site root (favicon, CNAME, .nojekyll).
- `docs/` — the built site, published by GitHub Pages (Settings → Pages → Deploy from branch `main`, folder `/docs`).
