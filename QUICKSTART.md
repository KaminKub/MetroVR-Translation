# One-Click Translation Mod

Translate a UE5 game → get a ready-to-install `.pak` in 3 steps.

## Before you start

Download and place in `tools/`:
- **repak** → <https://github.com/trumank/repak/releases> (Windows zip → `repak.exe`)
- **retoc** → <https://github.com/trumank/retoc/releases> (Windows zip → `retoc.exe`)

## Steps

1. **Fill the CSV** — `translations_TEMPLATE.csv` (3 columns: `File_Path,Original_Text,Target_Translation`). Fill `Target_Translation` with your translation; leave it empty to keep the original text.

2. **Run** — `python run_all.py`

3. **Install** — copy the 3 files from `output/pak/` into the game's `Content/Paks/` folder:
   - `TranslationMod_P.pak`
   - `TranslationMod_P.ucas`
   - `TranslationMod_P.utoc`

Done. Launch the game.

## Notes

- `File_Path` = path to the JSON in `input/source_json/` (the `Impact/Content/` prefix is stripped automatically).
- Source JSON must be in UAssetAPI format (extract with FModel/UAssetGUI).
- Game must have font glyphs for your language, or text won't render.
- Remove older mods before installing a new one.
- **Switch back to English in-game** — the mod ships the original English subtitles in the `L10N/fr` slot. In the game's language settings, pick **French** to see English subtitles again (no uninstall needed). Your translated language stays the default.
- Full guide: `README.md`
