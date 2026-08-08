#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3: Pack .uasset files into a game mod (.utoc/.ucas).

retoc to-zen -> IoStore container (.utoc/.ucas) straight from the uasset folder.

The uasset folder must contain the game-relative structure under <content_prefix>
(e.g. Impact/Content/Assets/...). retoc reads the folder directly, so no legacy
.pak step is needed (UE5 games load IoStore .utoc/.ucas; a legacy .pak would
just be redundant).

Usage:
    python 3_pack.py [config.json]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RETOC = HERE / "tools" / "retoc.exe"


def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run(cmd: list[str]) -> bool:
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"  ERROR: exit {result.returncode}")
        return False
    return True


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "config.json"
    cfg = load_config(config_path)

    uasset_root = HERE / cfg['uasset_output']
    pak_dir = HERE / cfg['pak_output']
    pak_name = cfg['pak_name']
    engine = cfg['engine_version']
    content_prefix = cfg.get('content_prefix', '')

    if not uasset_root.exists():
        print(f"ERROR: uasset folder not found: {uasset_root}")
        print("  Run step 2 first: python 2_json_to_uasset.py")
        sys.exit(1)
    if not RETOC.exists():
        print(f"ERROR: retoc.exe not found: {RETOC}")
        print("  Download it: https://github.com/trumank/retoc/releases")
        print("  Place retoc.exe in the tools/ folder.")
        sys.exit(1)

    pak_dir.mkdir(parents=True, exist_ok=True)
    utoc_path = pak_dir / f"{pak_name}.utoc"

    # Step 0: merge the language fallback (e.g. English subtitles in the L10N/fr
    # slot) into the uasset tree so it ships inside the pak
    l10n = HERE / cfg.get('l10n_fallback', '')
    if l10n.exists():
        dest = uasset_root / content_prefix / "L10N" / "fr"
        shutil.copytree(l10n, dest, dirs_exist_ok=True)
        print(f"Copied language fallback -> {dest}")

    # Step 1: IoStore container straight from the uasset folder (no repak needed)
    print(f"Step 1: retoc to-zen -> {utoc_path}")
    if not run([str(RETOC), "to-zen", "--version", engine, str(uasset_root), str(utoc_path)]):
        sys.exit(1)

    # Step 2: verify
    print(f"Step 2: retoc verify")
    run([str(RETOC), "verify", str(utoc_path)])

    # retoc writes an empty legacy .pak stub alongside the container — it has
    # no data (just a header), the game doesn't need it, drop it
    for stub in pak_dir.glob(f"{pak_name}.pak"):
        if stub.stat().st_size < 1024:
            stub.unlink()
            print(f"Removed empty .pak stub: {stub.name}")

    print("\nDone. Mod files:")
    for f in sorted(pak_dir.glob(f"{pak_name}.utoc")) + sorted(pak_dir.glob(f"{pak_name}.ucas")):
        print(f"  {f} ({f.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
