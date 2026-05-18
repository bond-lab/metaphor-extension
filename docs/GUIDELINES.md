# Annotation Guidelines

These guidelines explain how to annotate semantic links between word senses using the Metaphor Extension tool. The task is adapted from the [ChainNet annotation scheme](https://github.com/rowanhm/ChainNet/blob/main/documentation/ChainNet_Annotation_Guidelines.pdf) (Haber & Poesio 2023).

---

## Overview

Many words have senses that span two distinct conceptual domains. For example, the English word *wolf* has a sense under the ANIMAL domain (a predatory canine) and a sense under the HUMAN domain (an aggressive or voracious person). The tool presents words like this — ones whose senses appear in **both** a source and a target concept hierarchy — and asks you to record the semantic relationship between those senses.

Your job is to:

1. Read the sense cards for the current word.
2. Select two senses — one from each conceptual domain (or both from the same domain if they differ in relevant ways).
3. Choose a link direction.
4. Click a link type: **metaphor**, **metonymy**, **hypernym**, or **other**.
5. Mark the item as Done, Incomplete, or Ignore.

A word may have more than one meaningful link — for example, two different senses of *crane* might each connect to a human-domain sense in different ways. Record all links you find.

---

## Reading Senses

Each sense card shows:

- **Synset lemmas** — the synonyms grouped in this synset.
- **ILI** — the interlingual index identifier; click the 🦢 link to open [Cygnet](https://cygnet.maudslay.eu) for more context and cross-lingual information.
- **Definition** — the WordNet gloss.
- **Badges** — `SOURCE ILI` (this sense falls under the source hierarchy), `TARGET ILI` (target hierarchy), or both. A sense with both badges links to ILIs in both domains.

**If you are working with a non-English WordNet**, enable the *Show translations* toggle (next to "All senses") to display English glosses alongside the native-language definitions. This can help orient you without replacing the primary annotation object, which is always the target-language sense.

**EXTENDED senses** (shown with an orange `EXTENDED` badge) are projected from a reference WordNet because the target WordNet has no native sense for that ILI. Treat them as annotation candidates: if a meaningful link exists, record it, but note in the sense comment that this is an extended sense, not a verified entry in the target WordNet.

---

## Link Types

### Metaphor

A **metaphor** link connects two senses that *resemble* each other — they share some structural or property-based features — but differ in important ways, typically because one is abstract and the other is concrete, or one applies to a different domain.

**Test:** Can you describe features that are preserved from one sense and features that are transformed or lost? If yes, the link is a metaphor.

**Examples:**

| Word | Animal sense | Human/other sense | Shared feature | Changed feature |
|------|-------------|-------------------|----------------|-----------------|
| *wolf* | predatory canine mammal | aggressive, greedy person | predatory behaviour | biological species |
| *crane* | large wading bird with a long neck | tall machine for lifting loads | tall, long neck/arm, used to reach high | living vs. mechanical |
| *fox* | small cunning wild canid | attractive or sly person | cunning behaviour / appealing appearance | animal vs. human |
| *snake* | reptile that moves by slithering | treacherous or deceitful person | moves silently, untrustworthy | animal vs. human |

The direction A → B should point **from the more concrete / primary sense (A) toward the metaphorical extension (B)**. For animal-to-human mappings, A is typically the animal sense.

**Note on subtlety:** When in doubt, be generous about labelling a link as metaphor and capture the distinction in a comment. A link that you can express as a feature transformation (shared and changed properties) is a metaphor.

---

### Metonymy

A **metonymy** link connects two senses that are related through real-world association rather than resemblance. One concept is used to stand for another because of their close connection — not because they look or behave alike.

**Test:** Are the two senses related by proximity, part–whole, cause–effect, or material–object connections, without any structural similarity? If yes, the link is a metonymy.

**Common patterns:**

- **Part for whole:** *hand* (body part) → *hand* (worker, labourer) — a person named by a relevant body part.
- **Animal for behaviour/product:** *leech* (parasitic worm) → *leech* (person who exploits others) — this looks like a metaphor, but the connection is one of association by behaviour rather than structural resemblance. When in doubt, see "Distinguishing metaphor and metonymy" below.
- **Place for institution:** *crown* (ornamental headgear) → *crown* (the monarchy) — the object stands for the institution.

**Direction:** The more literal or physically grounded sense is usually A; the associated sense is B.

---

### Hypernym

A **hypernym** link records a direct or near-direct taxonomic relationship: one sense is a kind of the other, or one is a more general category that includes the other.

**Test:** Is one sense a sub-type or instance of the other, connected by *is-a* rather than by resemblance or association?

The WordNet hierarchy already encodes many such relationships, and the tool displays them in the *Existing WordNet relations* section of each item. You should only use the `hypernym` link type when the taxonomic relation spans the two ILI domains and is not already captured in the Wordnet, or when recording it is analytically important for the session.

**Direction:** A → B, where A is the **hypernym** (more general sense) and B is the hyponym (more specific sense).

**Example:** A word with a sense meaning *creature* or *living being* (under the ANIMAL hierarchy) and a sense meaning *person* (under the HUMAN hierarchy) — the animal sense is the hypernym.

---

### Other

Use **other** when there is a clear, documentable semantic link between the two senses that does not fit metaphor, metonymy, or hypernym. Write a comment explaining the relationship.

Do **not** use `other` as a catch-all for uncertain cases. If you are unsure whether a link is metaphor or metonymy, record it as one of those and add a comment. Reserve `other` for genuinely distinct relationship types.

---

### None

Clicking **none** **removes** an existing link between the selected sense pair. It is not a label applied to a new item — it is only useful for correcting an earlier annotation.

---

## Selecting Senses and Setting Direction

1. **Click the first sense card** (A). It will be highlighted in blue.
2. **Click the second sense card** (B).
3. Check the **Direction** selector:
   - `first → second` means A → B (the default).
   - `second → first` means B → A.
4. Hover over a link type button to preview the full label before clicking.
5. Click the link type to save.

You can select the same sense twice only by clicking elsewhere first to deselect. Clicking an already-selected sense deselects it.

A word may have **multiple links**. For example, *mouse* might have one sense linked by shape metaphor (computer mouse ← rodent) and a second sense linked differently. Record each pair separately.

---

## Distinguishing Metaphor and Metonymy

This is the most common source of difficulty. Use the following tests:

| Question | If yes → | If no → |
|----------|----------|---------|
| Do the two senses *resemble* each other (share structural or perceptual features)? | Metaphor | Metonymy candidate |
| Can you state a feature that is **kept** and a feature that is **changed**? | Metaphor | Metonymy or Other |
| Is the link based on spatial, causal, or part–whole *proximity* in the real world? | Metonymy | Metaphor candidate |

When the boundary is genuinely unclear, prefer **metaphor** and note the difficulty in the item comment. Metonymy should be reserved for cases where you cannot identify a structural resemblance at all.

---

## Item Status

After annotating a word, set its status in the footer:

| Button | Status shown | Meaning |
|--------|-------------|---------|
| **Finished** | `DONE` | All meaningful links recorded; confident. |
| **Incomplete** | `PART` | Started but not finished; return later. |
| **Ignore** | `IGNORE` | No annotatable cross-domain link exists. |
| *(none set)* | `--` | Not yet reviewed. |

Use **Ignore** when:
- The two senses share a lexical form coincidentally (e.g. a proper noun borrowed into the common lexicon with no remaining semantic connection).
- The word appears in both hierarchies only because of an error in the WordNet.

---

## Comments

**Item comment** (bottom of the workspace): Use for overall notes about the word — ambiguity, disagreement, uncertainty about which link type applies, or context that would help a reviewer.

**Sense comment** (below each sense card): Use for notes specific to a sense — for example, "definition seems too broad" or "this sense may not exist in the target language; EXTENDED from English".

**Bad sense** (checkbox on each sense card): Mark this if the ILI assignment looks incorrect — for example, if a sense is listed under the ANIMAL hierarchy but its definition is clearly about something else. This flags the sense for later review without preventing you from annotating other senses on the same item.

---

## Quick Decision Guide

```
Is there a semantic link between the two senses?
│
├─ No clear link → IGNORE (or leave as -- if uncertain)
│
└─ Yes
   │
   ├─ One sense is a kind-of the other (is-a relation)?
   │   └─ hypernym  (A = more general, B = more specific)
   │
   ├─ The senses RESEMBLE each other — shared structure or properties
   │   with something changed or abstracted?
   │   └─ metaphor  (A = concrete/source domain, B = extended/abstract)
   │
   ├─ The senses are linked by real-world association (part, product,
   │   material, behaviour) but do NOT resemble each other?
   │   └─ metonymy  (A = more literal, B = associated use)
   │
   └─ A clear link exists but none of the above fits?
       └─ other  (add a comment explaining the relationship)
```

---

## Reference

These guidelines are based on and adapted from:

> Haber, R. & Poesio, M. (2023). *Word Sense Distance in Human Judgements*. In *Proceedings of the 17th Linguistic Annotation Workshop (LAW-XVII)*. Association for Computational Linguistics.
> [ChainNet Annotation Guidelines PDF](https://github.com/rowanhm/ChainNet/blob/main/documentation/ChainNet_Annotation_Guidelines.pdf)
