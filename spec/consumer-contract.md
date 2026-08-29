# Catalog consumer contract
Mirrors `core/registry.py` in the rndrSBC core package.

- `GET <base>/catalog/_feed.json` → feed object
  - `version: int` = 1
  - `widgets: [{id, name, summary, author, version, license, min_core, sha256, url, entry, config_schema}]`
- Install algorithm (client-side, in `core/registry.py`):
  1. `GET widget.url` → bytes `B`
  2. compute `sha256(B)`; if `!= widget.sha256` → **refuse** (RuntimeError)
  3. unzip into `$RNDRSBC_HOME/plugins/<id>/`
  4. add `$RNDRSBC_HOME` to `sys.path`; `discover_widgets()` imports `plugins.<id>.widget`
- Artifacts are plain zips with a `widget.py` (and optional `assets/`).
- Every widget MUST subclass `BaseWidget` and self-register with `@register_widget`.
