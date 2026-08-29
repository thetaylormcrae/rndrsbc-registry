"""Build/validate the community catalog feed from `catalog/_widgets/*`.

Local dev:  python3 build_feed.py --path catalog/_widgets
CI:         the workflow runs this on merge to regenerate _feed.json + zips.
"""
import argparse
import hashlib
import io
import json
import os
import sys
import zipfile

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def package_widget(wdir, dest_dir):
    files = []
    for root, _dirs, names in os.walk(wdir):
        for n in names:
            if n == "__pycache__" or n.endswith(".pyc"):
                continue
            fp = os.path.join(root, n)
            rel = os.path.relpath(fp, wdir).replace(os.sep, "/")
            files.append((fp, rel))
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for fp, rel in files:
            z.write(fp, rel)
    data = buf.getvalue()
    artifact = f"{os.path.basename(wdir)}.zip"
    os.makedirs(dest_dir, exist_ok=True)
    with open(os.path.join(dest_dir, artifact), "wb") as fh:
        fh.write(data)
    return artifact, _sha256(data), files

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default="catalog/_widgets")
    ap.add_argument("--out-feed", default="catalog/_feed.json")
    ap.add_argument("--artifacts", default="artifacts")
    args = ap.parse_args()

    widgets = []
    widget_dirs = [d for d in os.listdir(args.path) if os.path.isdir(os.path.join(args.path, d))]
    if not widget_dirs:
        print(f"No widget dirs under {args.path}"); return 0

    for wid in sorted(widget_dirs):
        wdir = os.path.join(args.path, wid)
        artifact, sha, files = package_widget(wdir, args.artifacts)
        entry = {"id": wid, "version": "0.1.0", "sha256": sha,
                 "url": f"https://<host>/artifacts/{artifact}", "entry": "widget.py"}
        # merge metadata.yaml if present
        meta = os.path.join(wdir, "metadata.yaml")
        if os.path.exists(meta):
            for line in open(meta):
                line = line.strip()
                if ":" in line:
                    k, v = line.split(":", 1)
                    entry[k.strip()] = v.strip()
        widgets.append(entry)
        print(f"  packaged {wid}: {artifact} ({len(files)} files, sha256={sha[:12]}...)")

    feed = {"version": 1, "generated_at": "2026-08-26T00:00:00Z", "widgets": widgets}
    with open(args.out_feed, "w") as fh:
        json.dump(feed, fh, indent=2)
    print(f"Wrote catalog feed: {args.out_feed} ({len(widgets)} widgets)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
