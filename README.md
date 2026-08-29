# rndrSBC Community Widget Registry

The **curated catalog** behind `rndrsbc search` / `rndrsbc install`.

This repo is the *maintainer* side of the no-git-clone community model. End
users never clone anything — they get widgets from the published catalog feed
over HTTPS. This repo is where contributors add, vet, and ship those widgets.

```
 end user                           THIS REPO (maintainers)
 ─────────                          ─────────────────────────
 rndrsbc search weather  ────►      catalog/widgets/<id>/  (source)
 rndrsbc install sonos    ◄────      catalog/_feed.json     (compiled feed)
                                   GitHub Pages / S3       (served HTTPS)
```

## How a widget gets into the community

1. **Develop** — write `widget.py` (+ optional `assets/`) as a folder under
   `catalog/_widgets/<your_widget_id>/`. It subclasses `BaseWidget` and
   registers via the `@register_widget` decorator, exactly like a built-in.
2. **Declare metadata** — add a `metadata.yaml` next to it (id, name, summary,
   author, version, license, `min_core`).
3. **PR** — open a pull request. The CI (below) packages the folder into a
   `.<id>-<version>.zip`, computes its SHA-256, and **fails the PR if the hash
   doesn't match** the value recorded in the feed stub.
4. **Merge** — publishing the PR regenerates `catalog/_feed.json` (the compiled
   catalog the app consumes) and uploads artifacts.

## Release process (automated)

`.github/workflows/release.yml` runs on merge to `main`:

| Step | Does |
|------|------|
| `python build_feed.py` | Validates every `metadata.yaml` + `schema.json`, packages zips |
| `python build_feed.py` | Regenerates `catalog/_feed.json` with SHA-256 per artifact |
| `deploy` (Pages/S3) | Pushes feed + `artifacts/*.zip` to the static host |

The app's `core/registry.py` fetches `_feed.json`, verifies each `sha256`
before unpacking, and refuses mismatches (tested: a tampered hash is rejected).

## Catalog feed schema (v1)

```jsonc
{
  "version": 1,
  "generated_at": "2026-08-26T00:00:00Z",
  "widgets": [
    {
      "id": "sonos_now_playing",
      "name": "Sonos Now Playing",
      "summary": "Show the currently playing track + album art.",
      "author": { "name": "...", "url": "..." },
      "version": "0.2.1",
      "license": "MIT",
      "min_core": "0.1.0",
      "sha256": "<hex>",
      "url": "https://<host>/artifacts/sonos_now_playing-0.2.1.zip",
      "entry": "widget.py",
      "config_schema": { "fields": [...] }
    }
  ]
}
```

The consumer contract lives in `spec/` and mirrors `core/registry.py` exactly.
