---
type: home
---

# Home

Today's brief, and your list. The first block needs the Dataview community plugin with JavaScript queries turned on. Without it, open today's daily note.

## Today's brief

```dataviewjs
const d = dv.date("today").toFormat("yyyy-MM-dd");
const f = dv.page(`Daily/${d}`);
if (f) dv.paragraph(`![[Daily/${d}]]`);
else dv.paragraph(`No brief for ${d} yet. Ask Draco for the morning brief.`);
```

## Your list

![[todo]]

## The team

Open `Constellation.canvas`. Draco sits in the middle. The arrows are the only handoffs allowed.
