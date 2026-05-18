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
- **Animal for product:** *mink* (small furry mammal) → *mink* (a fur coat or garment made from its pelt); similarly *fox* (animal) → *fox* (the fur) — the product is named for the animal it comes from, with no structural resemblance between the two senses.
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

After annotating a word, set its status in the footer (← and → navigate the queue):

| Button | Status shown | Meaning |
|--------|-------------|---------|
| **Done** | `DONE` | All meaningful links recorded; confident. |
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

---

## Special Cases

This section covers recurring edge cases. It is adapted from §2.3.2 and §3 of the ChainNet guidelines.

### The threshold for metaphoricity

When it is unclear whether two senses are sufficiently different to count as a metaphor, **err on the side of labelling it as a metaphor** and use a comment to note the subtlety. This applies even when the difference seems small. For example, *flesh* as animal tissue and *flesh* as the soft interior of a fruit are technically distinct senses even though they share most features — the changed feature (part of an animal vs. part of a fruit) is enough to make the link metaphorical.

### Generalisations

Sometimes one sense is a loose generalisation of another: it covers the literal cases and also cases that are clearly metaphorical. Treat such a sense as a **metaphor** of the more specific one, not as an association. For example, if one sense means *the mother of your parent* and another means *any old woman*, the second is a metaphorical extension of the first.

### Abstractions

A sense that describes a property of an object is often a metaphorical extension of the sense describing the object itself. Colour names are the classic case: *ivory* (the material) → *ivory* (the off-white colour) is a metaphor because the colour sense can be predicated of things that are not made of ivory (e.g. "her ivory skin"). The test is whether the abstract sense can describe things that lack the defining features of the concrete sense.

Note: if the abstract property sense is the *core* sense (the one you think of first), then the object sense is a **metonymy**, not a metaphor. Direction matters here.

### International and regional equivalents

When a word has two senses that refer to different regional or cultural versions of the same thing (e.g. a British and an American unit of measurement, or two regional species referred to by the same name), treat these as **metaphorically** related: they are similar in structure but differ in a specific measurable or definitional way. The more internationally unmarked or historically prior sense is A; the regional variant is B.

### Choosing which sense a metaphor connects to

When multiple senses are candidates for the source of a metaphor, connect to the one whose **semantic type** best matches. An event-like sense should connect to another event-like sense; an object should connect to an object. For example, if a word has both an action sense and a result-state sense, a metaphorical extension that describes an event should link to the action sense rather than the result-state sense.

### Chained links

Occasionally sense A is linked to sense B, and B is itself a metaphor or metonymy of sense C. In ChainNet this is handled with "conduit" labels; this tool does not support that structure. Instead:

- Record the most direct link you can find between each pair of senses.
- If a chain seems important, note it in the item comment (e.g. "sense 2 is a metonymy of sense 1, and sense 3 is a metaphor of sense 2, not directly of sense 1").

### Senses that conflate literal and metaphorical meanings

WordNet definitions sometimes bundle a literal and a metaphorical reading into a single sense (e.g. *birth*: "the time when something begins", covering both the birth of a child and the birth of an era). You cannot split senses in this tool. Instead:

- Annotate the link as **metaphor** if the dominant reading in the cross-domain context is metaphorical.
- Add a sense comment noting that the definition conflates literal and metaphorical readings.

### Missing senses (gaps in the WordNet)

If the semantic link you want to record is clear but the sense needed to express it is absent from the WordNet, and there is an EXTENDED sense (projected from the reference WordNet) that fills this gap, annotate using the EXTENDED sense and note in a sense comment that it is not a verified entry.

If no suitable sense exists at all, mark the item as **Incomplete** and explain in the item comment what link you believe exists and what sense is missing.

---

## Reference

These guidelines are based on and adapted from:

> Haber, R. & Poesio, M. (2023). *Word Sense Distance in Human Judgements*. In *Proceedings of the 17th Linguistic Annotation Workshop (LAW-XVII)*. Association for Computational Linguistics.
> [ChainNet Annotation Guidelines PDF](https://github.com/rowanhm/ChainNet/blob/main/documentation/ChainNet_Annotation_Guidelines.pdf)
