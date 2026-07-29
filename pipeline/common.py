"""Gemeinsame Helfer: Config laden, Ausgabepfade, Argumente."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
PROMPT_DIR = ROOT / "prompts"
OUT_DIR = ROOT / "out"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--podcast", required=True, help="Config-Name ohne .yaml")
    return p.parse_args()


def load_config(podcast: str) -> dict:
    path = CONFIG_DIR / f"{podcast}.yaml"
    if not path.exists():
        raise SystemExit(f"Config nicht gefunden: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompt(name: str) -> str:
    return (PROMPT_DIR / f"{name}.md").read_text(encoding="utf-8")


def out_path(podcast: str, filename: str) -> Path:
    d = OUT_DIR / podcast
    d.mkdir(parents=True, exist_ok=True)
    return d / filename


def read_out(podcast: str, filename: str) -> str:
    return out_path(podcast, filename).read_text(encoding="utf-8")


def write_out(podcast: str, filename: str, content: str) -> Path:
    path = out_path(podcast, filename)
    path.write_text(content, encoding="utf-8")
    print(f"  geschrieben: {path.relative_to(ROOT)}")
    return path


def write_json(podcast: str, filename: str, data) -> Path:
    return write_out(podcast, filename, json.dumps(data, ensure_ascii=False, indent=2))
