"""Phase 2: Dialog-Script mit Claude (natürliches gesprochenes Deutsch).

Input:  out/<podcast>/topics.json
Output: out/<podcast>/script.md
"""
from __future__ import annotations

import os

import anthropic

from .common import load_config, load_prompt, parse_args, read_out, write_out

MODEL = "claude-sonnet-4-6"


def main() -> None:
    args = parse_args()
    cfg = load_config(args.podcast)
    s = cfg["script"]
    test_mode = cfg.get("test_mode", False)

    # Im Testmodus ~3 Minuten = ~450 Wörter
    target_words = 450 if test_mode else s["target_words"]

    topics = read_out(args.podcast, "topics.json")
    hosts = "\n".join(f"- {name}: {desc}" for name, desc in s["hosts"].items())

    prompt = load_prompt("script").format(
        podcast_name=cfg["name"],
        target_words=target_words,
        hosts=hosts,
        ai_disclosure=cfg["ai_disclosure"],
        topics=topics,
    )

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    resp = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        temperature=0.8,
        messages=[{"role": "user", "content": prompt}],
    )

    script = "".join(b.text for b in resp.content if b.type == "text").strip()
    words = len(script.split())
    print(f"  Script erstellt: ~{words} Wörter (~{words/150:.1f} Min)")
    write_out(args.podcast, "script.md", script)


if __name__ == "__main__":
    main()
