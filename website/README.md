# Python Class Pollution Website

Static website for the Python Class Pollution research project, including the landing page and the documentation wiki.

## Structure

```
website/
├── index.html       # Landing page
├── img/             # Hero icon and demo GIFs
├── source/          # Wiki source (Hugo content + layouts)
│   ├── content/     # Markdown pages
│   ├── layouts/     # Custom Hugo templates
│   ├── static/      # Wiki CSS and assets
│   └── hugo.toml    # Hugo config
└── wiki/            # Built wiki (generated from source/)
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
