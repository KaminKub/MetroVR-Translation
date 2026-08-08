#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 3: Pack .uasset files into a game mod (.pak/.ucas/.utoc).

1. repak pack  -> legacy .pak from the uasset folder
2. retoc to-zen -> convert to IoStore container (.utoc/.ucas/.pak)

The uasset folder must contain the game-relative structure under <content_prefix>
(e.g. Impact/Content/Assets/...). The pak mounts at <mount_point> (default ../../../).

Usage:
    python 3_pack.py [config.json]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPAK = HERE / "tools" / "repak.exe"
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
    mount_point = cfg.get('mount_point', '../../../')
    content_prefix = cfg.get('content_prefix', '')

    if not uasset_root.exists():
        print(f"ERROR: uasset folder not found: {uasset_root}")
        print("  Run step 2 first: python 2_json_to_uasset.py")
        sys.exit(1)
    if not REPAK.exists():
        print(f"ERROR: repak.exe not found: {REPAK}")
        print("  Download it: https://github.com/trumank/repak/releases")
        print("  Place repak.exe in the tools/ folder.")
        sys.exit(1)
    if not RETOC.exists():
        print(f"ERROR: retoc.exe not found: {RETOC}")
        print("  Download it: https://github.com/trumank/retoc/releases")
        print("  Place retoc.exe in the tools/ folder.")
        sys.exit(1)

    pak_dir.mkdir(parents=True, exist_ok=True)
    pak_path = pak_dir / f"{pak_name}.pak"
    utoc_path = pak_dir / f"{pak_name}.utoc"

    # Step 0: merge the language fallback (e.g. English subtitles in the L10N/fr
    # slot) into the uasset tree so it ships inside the pak
    l10n = HERE / cfg.get('l10n_fallback', '')
    if l10n.exists():
        dest = uasset_root / content_prefix / "L10N" / "fr"
        shutil.copytree(l10n, dest, dirs_exist_ok=True)
        print(f"Copied language fallback -> {dest}")

    # Step 1: legacy .pak
    print(f"Step 1: repak pack -> {pak_path}")
    if not run([str(REPAK), "pack", "--mount-point", mount_point, str(uasset_root), str(pak_path)]):
        sys.exit(1)

    # Step 2: IoStore container
    print(f"Step 2: retoc to-zen -> {utoc_path}")
    if not run([str(RETOC), "to-zen", "--version", engine, str(pak_path), str(utoc_path)]):
        sys.exit(1)

    # Step 3: verify
    print(f"Step 3: retoc verify")
    run([str(RETOC), "verify", str(utoc_path)])

    print("\nDone. Mod files:")
    for f in sorted(pak_dir.glob(f"{pak_name}.*")):
        print(f"  {f} ({f.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
