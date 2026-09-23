# freshconcept.co

Static site for [www.freshconcept.co](https://www.freshconcept.co), served by GitHub Pages. It was mirrored from Webflow in September 2026.

## Layout

- `index.html`, `pricing.html`, `startups.html`, `contact-us.html`: the pages mirrored from Webflow. GitHub Pages serves `/pricing` from `pricing.html`.
- `assets/`: CSS, JS, fonts and images that were on Webflow's CDN (`cdn.prod.website-files.com`). jQuery is in `assets/vendor/`.
- `404.html`: the not-found page.
- `utah-cancer/`: the Creative Department retainer options for Utah Cancer Specialists (noindex). The source is `creative-department-embed/` in the `utah-cancer` repo.

## Scripts

- `tools/mirror.py` re-downloads the pages and assets from the live Webflow site. It only works while Webflow still serves the site.
- `tools/build_pages.py` builds `404.html` and `utah-cancer/index.html` from the mirrored nav and footer. Re-run it after you edit the embed or its images. It also regenerates the 800px gallery thumbnails in the embed's `images/thumbs/` and copies the embed's `images/` into `utah-cancer/images/`. It needs Pillow.

## Known gaps

- The contact form on `/contact-us` still posts to Webflow's form API, which stops working once the Webflow site is unpublished. It needs a replacement form backend.
