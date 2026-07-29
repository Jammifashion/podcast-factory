"""Phase 1: Themenrecherche mit Gemini (inkl. Google-Search-Grounding).

Output: out/<podcast>/topics.json  (Liste priorisierter Themen mit Quellen)
"""
from __future__ import annotations

import json
import os

from google import genai
from google.genai import types

from .common import load_config, load_prompt, parse_args, write_json

MODEL = "gemini-2.5-flash"  # günstig + Search-Grounding; bei Bedarf auf Pro wechseln


def main() -> None:
    args = parse_args()
    cfg = load_config(args.podcast)
    r = cfg["research"]

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = load_prompt("research").format(
        lookback_days=r["lookback_days"],
        num_topics=r["num_topics"],
        focus=r["focus"],
        language=cfg["language"],
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
    # Modell soll reines JSON liefern; defensiv ```-Zäune entfernen.
    text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        topics = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: Rohtext sichern, damit der Lauf nachvollziehbar bleibt.
        write_json(args.podcast, "topics.json", {"raw": text, "parse_error": True})
        raise SystemExit("Gemini-Antwort war kein valides JSON – siehe topics.json")

    print(f"  {len(topics)} Themen recherchiert")
    write_json(args.podcast, "topics.json", topics)


if __name__ == "__main__":
    main()
