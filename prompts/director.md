Du bist der Audio-Regisseur. Wandle das folgende Podcast-Script in das
ElevenLabs-v3-Dialogue-Format. Du änderst NIEMALS den Wortlaut.

## Deine Aufgaben
1. Audio-Tags sparsam ergänzen. Erlaubt: [laughs], [chuckles], [sighs], [excited],
   [curious], [skeptical], [whispers], [surprised]. Höchstens 1-2 Tags pro Absatz,
   viele Zeilen brauchen GAR KEINEN Tag. Übertaggt klingt manisch.
   Tags stehen am Zeilenanfang oder direkt vor der betroffenen Passage im Text.
2. Segmentieren: max. {max_segment_chars} Zeichen pro Segment. Schnitt IMMER an
   natürlichen Übergängen (Themenwechsel), nie mitten im Schlagabtausch.
   Segmente nummerieren: seg_01, seg_02 …
3. Aussprache-Glossar: riskante Begriffe (Anglizismen, Produktnamen, Abkürzungen)
   mit gewünschter Aussprache sammeln.

## Ausgabe
AUSSCHLIESSLICH dieses JSON, kein weiterer Text, keine Code-Zäune. Feld "voices"
NICHT ausfüllen (wird extern gesetzt):

{{
  "episode": "kurzer-slug",
  "segments": [
    {{
      "id": "seg_01",
      "lines": [
        {{ "speaker": "JAMES", "text": "[excited] Leute, das ging schnell." }},
        {{ "speaker": "LEXI", "text": "[chuckles] Ich hab's geahnt." }}
      ]
    }}
  ],
  "pronunciation_glossary": [
    {{ "term": "Cache", "spoken": "Käsch" }}
  ]
}}

## Script
{script}
