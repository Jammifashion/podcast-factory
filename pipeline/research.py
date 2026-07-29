"""Phase 1: Themenrecherche mit Gemini (inkl. Google-Search-Grounding).

Output: out/<podcast>/topics.json  (Liste priorisierter Themen mit Quellen)
        out/<podcast>/used_topics.json (kumulatives Archiv bereits verwendeter Themen)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from google import genai
from google.genai import types

from .common import load_config, load_prompt, parse_args, out_path, write_json

MODEL = "gemini-2.5-flash"


def load_used_topics(podcast: str) -> list[str]:
    """Lädt die Liste bereits verwendeter Themen (Duplikat-Schutz)."""
    path = out_path(podcast, "used_topics.json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return []


def save_used_topics(podcast: str, topics: list, used: list[str]) -> None:
    """Fügt die neuen Themen zum Archiv hinzu."""
    new_titles = [t.get("thema", "") for t in topics]
    updated = list(set(used + new_titles))
    out_path(podcast, "used_topics.json").write_text(
        json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Themen-Archiv: {len(updated)} Einträge gesamt")


def main() -> None:
    args = parse_args()
    cfg = load_config(args.podcast)
    r = cfg["research"]
    test_mode = cfg.get("test_mode", False)

    # Im Testmodus nur 1 Thema recherchieren
    num_topics = 1 if test_mode else r["num_topics"]
    if test_mode:
        print("  TESTMODUS: 1 Thema, ~3 Minuten")

    used_topics = load_used_topics(args.podcast)
    used_hint = ""
    if used_topics:
        used_hint = (
            f"\n\nBereits behandelte Themen (NICHT nochmal verwenden):\n"
            + "\n".join(f"- {t}" for t in used_topics[-30:])  # max. letzte 30
        )

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = load_prompt("research").format(
        lookback_days=r["lookback_days"],
        num_topics=num_topics,
        focus=r["focus"],
        language=cfg["language"],
        used_hint=used_hint,
    )

    resp = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.4,
        ),
    )

    text = resp.text.strip()
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        topics = json.loads(text)
    except json.JSONDecodeError:
        write_json(args.podcast, "topics.json", {"raw": text, "parse_error": True})
        raise SystemExit("Gemini-Antwort war kein valides JSON – siehe topics.json")

    print(f"  {len(topics)} Themen recherchiert")
    write_json(args.podcast, "topics.json", topics)
    save_used_topics(args.podcast, topics, used_topics)


if __name__ == "__main__":
    main()
