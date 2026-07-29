"""Phase 3: Regie. Wandelt das Script in das ElevenLabs-v3-Dialogue-Format.

Fügt sparsame Audio-Tags hinzu, segmentiert (<= max_segment_chars) und traegt
die Voice-IDs aus der Config ein.

Input:  out/<podcast>/script.md
Output: out/<podcast>/dialogue.json
"""
from __future__ import annotations

import json
import os

import anthropic

from .common import load_config, load_prompt, parse_args, read_out, write_json

MODEL = "claude-haiku-4-5-20251001"


def main() -> None:
    args = parse_args()
    cfg = load_config(args.podcast)
    a = cfg["audio"]

    script = read_out(args.podcast, "script.md")

    prompt = load_prompt("director").format(
        max_segment_chars=a["max_segment_chars"],
        script=script,
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    dialogue = json.loads(text)  # bewusst hart: kaputtes JSON = Lauf stoppt

    # Voice-IDs aus der Config injizieren (nicht das Modell raten lassen).
    dialogue["voices"] = a["voices"]

    n_seg = len(dialogue.get("segments", []))
    n_lines = sum(len(s.get("lines", [])) for s in dialogue.get("segments", []))
    print(f"  Dialogue-JSON: {n_seg} Segmente, {n_lines} Zeilen")

    # Sicherheits-Check: Segmentlängen
    for seg in dialogue.get("segments", []):
        chars = sum(len(l.get("text", "")) for l in seg.get("lines", []))
        if chars > a["max_segment_chars"]:
            print(f"  WARNUNG: {seg.get('id')} hat {chars} Zeichen (> Limit)")

    write_json(args.podcast, "dialogue.json", dialogue)


if __name__ == "__main__":
    main()
