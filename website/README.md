# Python Class Pollution Website

Static website for the Python Class Pollution research project, including the landing page and the documentation wiki.

## Structure

```
website/
├── index.html         # Landing page (generated from source-landing/)
├── img/               # Hero icon and demo GIFs
├── source-landing/    # Landing-page source (Hugo, single home page)
│   ├── content/       # _index.md — landing page markdown
│   ├── layouts/       # index.html template with the landing styles
│   └── hugo.toml      # Hugo config
├── source/            # Wiki source (Hugo content + layouts)
│   ├── content/       # Markdown pages
│   ├── layouts/       # Custom Hugo templates
│   ├── static/        # Wiki CSS and assets
│   └── hugo.toml      # Hugo config
└── wiki/              # Built wiki (generated from source/)
```

## Running locally

Serve the directory with any static file server. For example:

```bash
cd website
python3 -m http.server 1313
```

Then open:

- Landing page: <http://localhost:1313/>
- Wiki: <http://localhost:1313/wiki/docs/>

## Rebuilding the wiki

The wiki source is in `source/` and uses [Hugo](https://gohugo.io/) with custom layouts.

```bash
cd source
hugo --baseURL="/wiki/" --destination="../wiki"
```

This generates the static site under `website/wiki/`.

## Rebuilding the landing page

The landing page is generated from `source-landing/content/_index.md` using a single Hugo home template at `source-landing/layouts/index.html` (which contains the page's inline styles). To edit copy, edit the markdown — don't edit `index.html` directly.

```bash
cd source-landing 
hugo --destination=/tmp/landing-build && cp /tmp/landing-build/index.html ../index.html
```

## Deployment

The site is deployed to <https://class-pollution.github.io> via the GitHub Actions workflow at `.github/workflows/deploy-website.yml`. On every push to `main` that touches `website/`, the workflow:

1. Builds the wiki with Hugo into `website/wiki/`
2. Pushes `index.html`, `img/`, and `wiki/` to the `class-pollution/class-pollution.github.io` repo

The workflow uses a `DEPLOY_TOKEN` repository secret (a fine-grained PAT with write access to the target repo).
