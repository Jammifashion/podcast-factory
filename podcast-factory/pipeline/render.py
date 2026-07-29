"""Phase 4: Audio-Rendering. Laeuft NUR nach dem Production-Lock-Approval.

Schritte:
  1. Jedes Segment ueber die ElevenLabs-v3-Dialogue-API rendern -> seg_XX.mp3
  2. Segmente + optionale Intro/Outro-Musik mit ffmpeg zusammenfuegen
  3. Auphonic-Mastering (Loudness, Leveler, Noise Reduction) -> final.mp3

HINWEIS: v3 ist Alpha. Endpoint-/Feldnamen vor dem ersten Produktivlauf gegen
die aktuelle ElevenLabs-Doku pruefen. Die Struktur unten kapselt den Call, so
dass nur eine Stelle angepasst werden muss.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

import requests

from .common import load_config, out_path, parse_args, read_out

ELEVEN_BASE = "https://api.elevenlabs.io/v1"
AUPHONIC_BASE = "https://auphonic.com/api"


def render_segment(seg: dict, voices: dict, api_key: str, dest: Path) -> None:
    """Ein Segment (mehrere Zeilen) als Dialog rendern."""
    payload = {
        "model_id": "eleven_v3",
        "inputs": [
            {"text": line["text"], "voice_id": voices[line["speaker"]]}
            for line in seg["lines"]
        ],
    }
    resp = requests.post(
        f"{ELEVEN_BASE}/text-to-dialogue",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
        timeout=300,
    )
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"  gerendert: {dest.name} ({len(resp.content)//1024} KB)")


def concat(segment_files: list[Path], intro: str, outro: str, dest: Path) -> None:
    """Segmente (+ optionale Musik) mit ffmpeg aneinanderhaengen."""
    parts = []
    if intro:
        parts.append(Path(intro))
    parts.extend(segment_files)
    if outro:
        parts.append(Path(outro))

    listfile = dest.parent / "concat.txt"
    listfile.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(listfile), "-c", "copy", str(dest)],
        check=True,
    )
    print(f"  zusammengefuegt: {dest.name}")


def auphonic_master(src: Path, dest: Path, api_key: str, lufs: int) -> None:
    """Optionales Mastering. Ohne AUPHONIC_API_KEY wird uebersprungen."""
    if not api_key:
        print("  Auphonic uebersprungen (kein Key) – nutze Rohmix")
        dest.write_bytes(src.read_bytes())
        return

    with open(src, "rb") as f:
        prod = requests.post(
            f"{AUPHONIC_BASE}/simple/productions.json",
            headers={"Authorization": f"Bearer {api_key}"},
            data={
                "title": src.stem,
                "loudnesstarget": lufs,
                "leveler": "true",
                "denoise": "true",
                "action": "start",
            },
            files={"input_file": f},
            timeout=300,
        )
    prod.raise_for_status()
    uuid = prod.json()["data"]["uuid"]
    print(f"  Auphonic-Produktion {uuid} gestartet …")

    # Auf Fertigstellung warten (Status 3 = Done).
    while True:
        time.sleep(15)
        st = requests.get(
            f"{AUPHONIC_BASE}/production/{uuid}.json",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        ).json()["data"]
        if st["status"] == 3:
            url = st["output_files"][0]["download_url"]
            audio = requests.get(url, headers={"Authorization": f"Bearer {api_key}"}, timeout=300)
            dest.write_bytes(audio.content)
            print(f"  gemastert: {dest.name}")
            return
        if st["status"] in (2, 9, 13):  # Error-Zustaende
            raise SystemExit(f"Auphonic-Fehler, Status {st['status']}")


def main() -> None:
    args = parse_args()
    cfg = load_config(args.podcast)
    a = cfg["audio"]

    dialogue = json.loads(read_out(args.podcast, "dialogue.json"))
    voices = dialogue["voices"]
    eleven_key = os.environ["ELEVENLABS_API_KEY"]
    auphonic_key = os.environ.get("AUPHONIC_API_KEY", "")

    seg_files = []
    for seg in dialogue["segments"]:
        dest = out_path(args.podcast, f"{seg['id']}.mp3")
        render_segment(seg, voices, eleven_key, dest)
        seg_files.append(dest)

    rough = out_path(args.podcast, "rough.mp3")
    concat(seg_files, a.get("intro_music", ""), a.get("outro_music", ""), rough)

    final = out_path(args.podcast, "final.mp3")
    auphonic_master(rough, final, auphonic_key, a["loudness_lufs"])
    print("  FERTIG:", final)


if __name__ == "__main__":
    main()
