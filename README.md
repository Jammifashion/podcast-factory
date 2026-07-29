# Podcast Factory

Serverlose, zeitgesteuerte Podcast-Pipeline auf GitHub Actions.
Kein Dauer-PC, kein eigener Server. Läuft alle 3 Tage von allein:

**Recherche (Gemini) → Script (Claude) → Regie/v3-JSON (Claude) → 🔒 deine Freigabe → Audio (ElevenLabs + Auphonic) → MP3**

Ein Podcast = eine Datei in `config/`. Mehrere Podcasts = mehrere Configs, gleiche Pipeline.

---

## Was du einmalig einrichtest

### 1. Repo anlegen
Diesen Ordner in ein **privates** GitHub-Repo pushen:
```bash
git init && git add . && git commit -m "init podcast factory"
git branch -M main
git remote add origin git@github.com:DEINNAME/podcast-factory.git
git push -u origin main
```

### 2. Secrets hinterlegen
Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Diese anlegen:

| Secret | Wofür | Pflicht |
|---|---|---|
| `ANTHROPIC_API_KEY` | Script + Regie | ja |
| `GEMINI_API_KEY` | Recherche | ja |
| `ELEVENLABS_API_KEY` | Audio | ja |
| `AUPHONIC_API_KEY` | Mastering | optional (ohne = Rohmix) |
| `TELEGRAM_BOT_TOKEN` | Benachrichtigung | optional |
| `TELEGRAM_CHAT_ID` | Benachrichtigung | optional |

### 3. Production-Lock-Gate einrichten (das Herzstück)
Repo → **Settings → Environments → New environment** → Name exakt **`production-lock`**.
Darin **Required reviewers** aktivieren und **dich selbst** eintragen.

→ Ab jetzt pausiert der Workflow vor dem teuren Audio-Rendering und wartet auf
deine Freigabe. Du bekommst eine Mail/Push und kannst **vom Handy** freigeben
oder ablehnen.

> Hinweis: Required Reviewers sind bei **öffentlichen** Repos kostenlos, bei
> **privaten** Repos brauchst du GitHub Pro/Team (~4 $/Monat). Alternative ohne
> Kosten: Repo öffentlich stellen (dann aber keine Secrets im Code – die liegen
> ohnehin verschlüsselt in den Actions-Secrets, das ist ok).

### 4. Voice-IDs eintragen
In `config/beats-and-bytes.yaml` die beiden `PLATZHALTER_VOICE_ID_*` durch deine
ElevenLabs-Voice-IDs für JAMES und LEXI ersetzen.

---

## So läuft ein Sprint

1. **Automatisch** alle 3 Tage (Cron) **oder** manuell: Repo → **Actions → Podcast Factory → Run workflow** (dort Podcast wählen).
2. Pipeline recherchiert, schreibt Script, baut das Dialogue-JSON.
3. **Stopp am Production Lock.** Du bekommst eine Nachricht. Im Actions-Lauf kannst
   du das `draft-…`-Artefakt runterladen (topics.json, script.md, dialogue.json)
   und prüfen.
4. Passt es → **Approve**. Passt es nicht → **Reject** (nichts wird gerendert,
   keine Audio-Kosten). Script anpassen oder Lauf neu starten.
5. Nach Freigabe rendert die Pipeline das Audio → `episode-…`-Artefakt (final.mp3).
6. Du hörst final ab und veröffentlichst manuell bei deinem Hoster.

Veröffentlichung bleibt bewusst manuell – EU AI Act Art. 50 verlangt den Hinweis
"KI-generierte Stimmen"; der steckt bereits im Script-Intro und gehört auch in
die Shownotes.

---

## Neuen Podcast hinzufügen
```bash
cp config/beats-and-bytes.yaml config/mein-zweiter-podcast.yaml
# Werte anpassen (Name, Fokus, Hosts, Voices)
```
Dann beim manuellen Start `mein-zweiter-podcast` als Podcast wählen. Für einen
eigenen Automatik-Zeitplan pro Podcast eine zweite `schedule`-Zeile im Workflow
ergänzen oder den Workflow duplizieren.

---

## Kosten pro Folge (grobe Hausnummer)
- Recherche + Script + Regie (LLM): unter 1 €
- ElevenLabs v3: je nach Abo (22–99 $/Monat), ~10.000 Zeichen pro Folge
- Auphonic: ab ~11 €/Monat (oder kostenlos für wenige Stunden/Monat)
- GitHub Actions: im Free-Tier für diese Last kostenlos

## Wichtiger Technik-Hinweis
ElevenLabs **v3 ist Alpha** – die Endpoint-/Feldnamen für `text-to-dialogue`
können sich ändern. Vor dem ersten Produktivlauf `pipeline/render.py` gegen die
aktuelle ElevenLabs-Doku prüfen; der API-Call ist bewusst in `render_segment()`
gekapselt, du musst also nur eine Stelle anfassen.
