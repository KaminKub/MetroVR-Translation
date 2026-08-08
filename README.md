# UAsset Translation Toolkit

A toolkit for translating Unreal Engine 5 (UE5) games — inject translations from a CSV into subtitle assets, then pack them into a game-loadable mod (.utoc/.ucas).

> Built from the Metro Awakening (UE5.2) translation project — made generic so it works with any UE5 game.
> Core idea: edit `CultureInvariantString` in subtitle assets (same as UAssetGUI).

---

## Pipeline Overview

```
CSV (translations) ──► 1_inject_translations.py ──► translated JSON
                                                        │
source JSON ────────────────────────────────────────────┘
                                                        │
                                                        ▼
                                          2_json_to_uasset.py ──► .uasset/.uexp
                                                        │
                                                        ▼
                                          3_pack.py ──► .utoc/.ucas (mod)
```

| Step | Script | Input | Output |
|------|--------|-------|--------|
| 1 | `1_inject_translations.py` | CSV + source JSON | `output/translated_json/` |
| 2 | `2_json_to_uasset.py` | `output/translated_json/` | `output/uasset/` |
| 3 | `3_pack.py` | `output/uasset/` | `output/pak/` (.utoc/.ucas) |

Run everything at once: `python run_all.py`

---

## Folder Structure

```
Metro_translation/
├── README.md                    # this guide
├── config.json                  # settings (engine, paths, mod name)
├── run_all.py                   # run all 3 steps
├── 1_inject_translations.py     # step 1: CSV → JSON
├── 2_json_to_uasset.py          # step 2: JSON → uasset
├── 3_pack.py                    # step 3: uasset → mod (.utoc/.ucas)
├── translations_TEMPLATE.csv    # ⬅️ translation template (fill Target_Translation)
├── input/
│   ├── source_json/             # ⬅️ source JSON (extracted from game)
│   └── L10N/fr/                 # ⬅️ original English subtitles (French slot) — lets players switch back to English in-game
├── output/                      # results (auto-created)
│   ├── translated_json/         #   JSON with translations injected
│   ├── uasset/                  #   .uasset/.uexp
│   └── pak/                     #   mod .utoc/.ucas
├── json_to_uasset/              # C# converter (UAssetAPI)
├── lib/UAssetAPI.dll            # UAssetAPI v1.1.0
└── tools/                       # ⬅️ download retoc.exe here (see Requirements)
    └── retoc.exe                # create IoStore (.utoc/.ucas) (download)
```

---

## Requirements

- **Python 3.10+** (tested with 3.14)
- **.NET 8 runtime** — to run the prebuilt converter (`json_to_uasset/bin/` is included). To rebuild from source: `cd json_to_uasset && dotnet build -c Release` (requires the SDK)
- **retoc** — download and place in `tools/`:
  - **retoc** (create IoStore .utoc/.ucas): <https://github.com/trumank/retoc/releases> — Windows zip → `retoc.exe`
- Source JSON must be in **UAssetAPI format** (export with UAssetGUI or the `UAssetJsonExporter` project)

---

## Usage

### 1. Prepare input

**CSV** (`translations_TEMPLATE.csv`) — 3 columns:

```csv
File_Path,Original_Text,Target_Translation
Impact\Content\Maps\...\xxx_Sub.json,<source text>,<translation>
```

- `File_Path` — path to the JSON file (relative to `source_json/` — the `Impact/Content/` prefix is stripped automatically, configurable in config.json)
- `Target_Translation` — **fill in your translation here** (rows left empty are skipped, original text kept)

**Source JSON** (`input/source_json/`) — place the JSON extracted from the game (UAssetAPI format)

### 2. Run the pipeline

```bash
# run step by step
python 1_inject_translations.py
python 2_json_to_uasset.py
python 3_pack.py

# or run everything
python run_all.py
```

### 3. Get the mod

Mod files are in `output/pak/`:
- `TranslationMod_P.utoc`
- `TranslationMod_P.ucas`

Copy both files to `<GameDir>/<Content>/Paks/` and launch the game.

---

## config.json

| Field | Default | Description |
|-------|---------|-------------|
| `engine_version` | `UE5_2` | Unreal Engine version of the game (UE4_25..UE5_7) |
| `csv_file` | `translations_TEMPLATE.csv` | translation CSV file (fill `Target_Translation`, leave empty = keep original) |
| `source_json` | `input/source_json` | source JSON folder |
| `translated_json` | `output/translated_json` | translated JSON folder |
| `uasset_output` | `output/uasset` | uasset folder |
| `pak_output` | `output/pak` | mod folder |
| `pak_name` | `TranslationMod_P` | mod name (change to avoid conflicts) |
| `csv_path_prefix_to_strip` | `Impact/Content/` | prefix stripped from CSV paths when mapping to source_json |
| `content_prefix` | `Impact/Content` | in-game path structure (used to place uassets at the correct pak path) |
| `l10n_fallback` | `input/L10N/fr` | folder merged into the pak as `L10N/fr` — original-language subtitles so players can switch back in-game |

---

## Notes / Caveats

- **Rows with empty `Target_Translation`** → skipped, original text kept — ideal for partially-translated templates
- **Files not in the CSV** → copied as-is (not modified)
- **`DV_Speaker_*`** — injects into `Name.CultureInvariantString` (character names)
- **Other files** — injects into `SubtitleCues[].Text.CultureInvariantString`
- **Output filenames** — `<name>.uasset` (not `<name>.json.uasset`) — this bug is fixed in `json_to_uasset/JsonToUAsset.cs`
- **Fonts** — the game must have glyphs for your target language, otherwise text won't render (requires a separate font mod)
- **Mod conflicts** — remove/rename older mods before installing a new one
- **Switch back to the original language in-game** — the mod ships the original English subtitles in the `L10N/fr` slot (`input/L10N/fr`). In the game's language settings, pick **French** to see English subtitles again — no need to uninstall the mod. (The translated language stays the default.)

## License

- This toolkit (scripts, C# source, docs) is released under the **MIT License** — see `LICENSE`.
- Third-party components retain their own licenses:
  - **retoc** — [retoc](https://github.com/trumank/retoc) (MIT) — downloaded separately, see Requirements
  - `lib/UAssetAPI.dll` — [UAssetAPI](https://github.com/atenfyr/UAssetAPI) (MIT)
- **Game assets are NOT covered by this license.** `input/source_json/` and `input/L10N/fr/` are extracted from the game and remain the game's copyrighted content — do not redistribute them. Extract your own from a game you own (see below).

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ERROR: CSV not found` | check that `translations_TEMPLATE.csv` exists |
| `ERROR: converter not found` | rebuild: `cd json_to_uasset && dotnet build -c Release` |
| `ERROR: retoc.exe not found` | download from the links in Requirements, place in `tools/` |
| `[MISS]` in step 1 | CSV path doesn't match a file in `source_json/` — check the prefix |
| `[MISMATCH]` in step 1 | cue count in JSON doesn't match row count in CSV |
| `retoc verify` fails | check `engine_version` in config matches the game |
| game doesn't load the mod | check `content_prefix` structure matches the game |

---

## How to Extract Source JSON from a Game

1. Open the game pak with **FModel** or **UAssetGUI** → export `.uasset`
2. Convert `.uasset` → JSON with **UAssetAPI** (the `UAssetJsonExporter` project or UAssetGUI)
3. Place the JSON into `input/source_json/` (keep the folder structure)
