#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step 1: Inject translations from CSV into UAssetAPI JSON files.

Reads a CSV (File_Path, Original_Text, Target_Translation), copies the source
JSON tree to the output folder, and writes Target_Translation into the
CultureInvariantString fields of each matching JSON file.

Supported asset types:
  - Subtitle assets: Exports[0].Data[SubtitleCues].Value[i].Value[Text].CultureInvariantString
  - Speaker name assets (DV_Speaker_*): Exports[0].Data[Name].CultureInvariantString

Rows with an empty Target_Translation are skipped (original text kept) and counted.

Usage:
    python 1_inject_translations.py [config.json]
"""
import json
import csv
import sys
import shutil
from pathlib import Path
from collections import defaultdict

HERE = Path(__file__).resolve().parent


def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def read_csv(csv_file: Path) -> dict[str, list[dict]]:
    """Group CSV rows by File_Path (keep order)."""
    by_file = defaultdict(list)
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            by_file[row['File_Path']].append(row)
    return dict(by_file)


def map_to_source(csv_path: str, source_root: Path, strip_prefix: str) -> Path:
    """Map a CSV path to the source JSON path (strip the content prefix)."""
    rel = csv_path.replace('\\', '/')
    if strip_prefix and rel.startswith(strip_prefix):
        rel = rel[len(strip_prefix):]
    return source_root / rel


def inject_file(data: dict, rows: list[dict], is_speaker: bool) -> int:
    """Inject translations into one UAssetAPI JSON dict. Returns cues injected."""
    exports = data.get('Exports', [])
    if not exports:
        return 0
    props = exports[0].get('Data', [])

    injected = 0
    if is_speaker:
        # single Name property
        for prop in props:
            if prop.get('Name') == 'Name' and 'CultureInvariantString' in prop:
                prop['CultureInvariantString'] = rows[0]['Target_Translation']
                injected = 1
                break
    else:
        # SubtitleCues array
        cue_idx = 0
        for prop in props:
            if prop.get('Name') != 'SubtitleCues':
                continue
            for cue in prop.get('Value', []):
                if cue_idx >= len(rows):
                    break
                for cue_prop in cue.get('Value', []):
                    if cue_prop.get('Name') == 'Text' and 'CultureInvariantString' in cue_prop:
                        cue_prop['CultureInvariantString'] = rows[cue_idx]['Target_Translation']
                        cue_idx += 1
                        injected += 1
                        break
            break

    return injected


def main():
    config_path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "config.json"
    cfg = load_config(config_path)

    csv_file = HERE / cfg['csv_file']
    source_root = HERE / cfg['source_json']
    out_root = HERE / cfg['translated_json']
    strip_prefix = cfg.get('csv_path_prefix_to_strip', '')

    if not csv_file.exists():
        print(f"ERROR: CSV not found: {csv_file}")
        sys.exit(1)
    if not source_root.exists():
        print(f"ERROR: source JSON folder not found: {source_root}")
        sys.exit(1)

    by_file = read_csv(csv_file)
    total_rows = sum(len(v) for v in by_file.values())
    print(f"CSV rows: {total_rows}, files: {len(by_file)}")

    # 1. copy full source tree -> output (files not in CSV stay as originals)
    if out_root.exists():
        shutil.rmtree(out_root)
    shutil.copytree(source_root, out_root)
    print(f"Copied source tree -> {out_root}")

    # 2. inject translations into output copies
    ok = 0
    missing = 0
    mismatch = 0
    skipped_empty = 0
    for csv_path, rows in by_file.items():
        src = map_to_source(csv_path, source_root, strip_prefix)
        if not src.exists():
            print(f"  [MISS] {csv_path}")
            missing += 1
            continue

        # filter out rows with empty Target_Translation
        filled = [r for r in rows if r.get('Target_Translation', '').strip()]
        skipped_empty += len(rows) - len(filled)
        if not filled:
            continue

        out = out_root / src.relative_to(source_root)
        with open(src, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
        n = inject_file(data, filled, is_speaker='DV_Speaker' in src.name)
        if n == len(filled):
            ok += 1
        else:
            print(f"  [MISMATCH] {src.name}: injected {n}/{len(filled)}")
            mismatch += 1
        with open(out, 'w', encoding='utf-8', newline='') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\nOK: {ok}, MISSING: {missing}, MISMATCH: {mismatch}, SKIPPED_EMPTY_ROWS: {skipped_empty}")
    print(f"Output JSON files: {sum(1 for _ in out_root.rglob('*.json'))}")


if __name__ == "__main__":
    main()
