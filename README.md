# Saddle Up Arcade (installable web app)

Static site, no build step. `index.html` is the whole arcade (generated from the GHL embed by `make_app.py`);
`manifest.webmanifest` + `sw.js` + `icons/` make it installable ("Add to Home Screen").
Deployed on Vercel; every push to `main` goes live.
