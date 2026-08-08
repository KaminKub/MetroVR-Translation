#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 2: Convert translated JSON files back to .uasset binary.

Runs the bundled C# converter (json_to_uasset) which uses UAssetAPI to
deserialize each JSON and write the .uasset (auto-creating .uexp/.ubulk).

The output is written under <uasset_output>/<content_prefix>/ so the final
pak has the correct game-relative paths (e.g. Impact/Content/Assets/...).

Usage:
    python 2_json_to_uasset.py [config.json]
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONVERTER_EXE = HERE / "json_to_uasset" / "bin" / "Release" / "net8.0" / "json_to_uasset.exe"


def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "config.json"
    cfg = load_config(config_path)

    json_folder = HERE / cfg['translated_json']
    content_prefix = cfg.get('content_prefix', '')
    uasset_out = HERE / cfg['uasset_output'] / content_prefix
    engine = cfg['engine_version']

    if not json_folder.exists():
        print(f"ERROR: translated JSON folder not found: {json_folder}")
        print("  Run step 1 first: python 1_inject_translations.py")
        sys.exit(1)
    if not CONVERTER_EXE.exists():
        print(f"ERROR: converter not found: {CONVERTER_EXE}")
        print("  Build it: cd json_to_uasset && dotnet build -c Release")
        sys.exit(1)

    print(f"JSON folder: {json_folder}")
    print(f"UAsset output: {uasset_out}")
    print(f"Engine: {engine}")
    print()

    cmd = [str(CONVERTER_EXE), str(json_folder), str(uasset_out), engine]
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"ERROR: converter failed (exit {result.returncode})")
        sys.exit(1)

    uasset_count = sum(1 for _ in (HERE / cfg['uasset_output']).rglob('*.uasset'))
    print(f"\nUAsset files produced: {uasset_count}")


if __name__ == "__main__":
    main()
