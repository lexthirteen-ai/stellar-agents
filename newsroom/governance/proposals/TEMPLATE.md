---
id: YYYY-MM-DD-short-slug
status: PROPOSED
proposed_by: <desk id>
score: 0
---

# Proposal, one line title

- [ ] approve (only the owner ticks this)

## What

One paragraph. What changes if this is approved.

## Why

The signal, request, or drift report that prompted it. Link the file.

## Undo

How this gets reversed if it turns out wrong. If there is no undo, say so, and expect a no.

## Score

| Factor | Max | This |
|---|---|---|
| Revenue or mission effect | 25 | |
| Cash cost avoided | 20 | |
| Confidence it works | 20 | |
| Fits the current plan | 15 | |
| Effort (higher is easier) | 15 | |
| Reusable elsewhere | 5 | |
| **Total** | **100** | |

Scores are computed by Carina, the Managing Editor from the factors above. A desk can argue for a score, but it cannot invent one.

## If approved

Registry row or change:

```json
{}
```

Audit line Selene, the Archivist will append:

```
YYYY-MM-DD HH:MM | REGISTERED or MODIFIED | <desk id> | <note>
```

---
provenance: desk=<id> | run=<ISO datetime> | trigger=<what> | inputs=<paths>
