# Annotation Task Instructions

Thank you for helping with this annotation project. Your job is to label semantic links between Turkish word senses that span two conceptual domains: **animals** and **humans/people**. The tool shows you words that appear in both domains and asks you to record how the two senses are related.

---

## What you will need

- A modern web browser (Chrome, Firefox, or Safari)
- The session file: **`kenet-animal-human-4a6d881bfc4af405.json`** (attached / provided separately)
- The annotation guidelines: **`GUIDELINES.md`** (in the same folder, or at the link below)

---

## Loading the session

1. Open the annotation tool in your browser. *(Your supervisor will give you the URL, or you can open `docs/index.html` locally — see below.)*
2. Click **Open session** in the top bar.
3. Select the file `kenet-animal-human-4a6d881bfc4af405.json`.
4. The queue on the left will fill with 38 Turkish words to annotate.

**Opening locally (if no URL is provided):**
```
python3 -m http.server 8000 --directory docs
```
Then open <http://127.0.0.1:8000> in your browser.

---

## Enabling English translations

The senses are in Turkish. To see English glosses alongside them:

1. Once a session is loaded, look for the **"Show omw-en:1.4"** toggle next to the "All senses" heading.
2. Check the box to turn translations on.
3. Each sense card will now show an italic English line below the Turkish definition.

Not every sense will have an English translation (some Turkish synsets do not have ILI links in the English WordNet), but most will.

---

## Annotating a word

For each word in the queue:

1. **Read all the sense cards.** The blue `SOURCE ILI` badge marks senses from the animal domain; the red `TARGET ILI` badge marks senses from the human/person domain. Use the Cygnet link (🦢) next to each ILI to look up more information in a browser.

2. **Click the first sense (A), then the second sense (B).**

3. **Check the Direction selector** (first → second, or second → first). For metaphors and metonymy, point from the more concrete/literal sense toward the extended sense — usually animal → human.

4. **Click a link type:**
   - **metaphor** — the two senses resemble each other (shared structure or properties, with something changed or abstracted)
   - **metonymy** — the two senses are associated by proximity or real-world connection, not resemblance
   - **hypernym** — one sense is a kind-of the other
   - **other** — a clear link exists but none of the above fits; please add a comment
   - **none** — removes an existing link if you made a mistake

5. **Add a comment** if you are uncertain, if the case is unusual, or if you used "other".

6. **Mark the status** when done with a word:
   - **Finished** → confident, all links recorded
   - **Incomplete** → come back to this one
   - **Ignore** → no meaningful link (e.g. a coincidental shared word form)

Read the full [annotation guidelines](GUIDELINES.md) before starting, paying particular attention to the **Distinguishing Metaphor and Metonymy** table and the **Special Cases** section.

---

## Saving your work

Your annotations are saved automatically in the browser's local storage as you work. However, you must **export the file when you are done** (or at the end of each session) to avoid losing work if you clear your browser or switch computers.

**To save:**

1. Click **Save session** in the top bar.
2. Your browser will download a file named `kenet-animal-human.json` (or similar).
3. Send this file to your supervisor when you have finished.

**To resume later:**

1. Click **Open session** and reload your saved `kenet-animal-human.json` file.
   - Use this file (not the original) once you have started annotating, so your work is preserved.
2. Alternatively, if you are on the same browser/computer, your last session is remembered automatically — just open the tool and it should restore your previous state.

---

## Questions and problems

- If a sense card looks wrong (bad ILI, wrong definition), tick the **bad-sense** checkbox on that card and add a note. Do not skip the word entirely.
- If you are unsure about a link type, record your best guess and add a comment explaining the difficulty.
- For anything else, contact your supervisor.
