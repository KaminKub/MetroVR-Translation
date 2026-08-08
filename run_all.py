#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the full pipeline: inject -> uasset -> pack.

Usage:
    python run_all.py [config.json]
"""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STEPS = ["1_inject_translations.py", "2_json_to_uasset.py", "3_pack.py"]


def main():
    config_arg = sys.argv[1] if len(sys.argv) > 1 else None
    for step in STEPS:
        print("=" * 70)
        print(f"STEP: {step}")
        print("=" * 70)
        cmd = [sys.executable, str(HERE / step)]
        if config_arg:
            cmd.append(config_arg)
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            print(f"\nFAILED at {step} (exit {result.returncode})")
            sys.exit(1)
    print("\nAll steps completed successfully.")


if __name__ == "__main__":
    main()
