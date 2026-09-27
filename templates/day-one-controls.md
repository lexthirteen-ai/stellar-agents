# Day One Controls

Six rules you can set up in an afternoon. Everything else in the kit is something you add later, when one of these visibly fails.

| # | Control | What it means | Why it exists |
|---|---|---|---|
| 1 | One job per desk | Each desk does one thing. A second duty becomes a second desk. | A desk with two jobs has two failure modes and one log line, so you never learn which half broke. |
| 2 | Chain, don't bundle | Explicit handoffs between steps, never one giant prompt. | A chain can be inspected at each link. A bundle can only be rerun. |
| 3 | Output contract, checked by code | Every desk declares the exact shape of its output, and a script checks it. | A human reviewer gets tired. A script does not, and it rejects the same way every time. |
| 4 | Retry cap | Three failed attempts, then log the stall and stop. | Loop retries hide the real error under a pile of identical ones. |
| 5 | Time cap | About ten minutes without progress means stuck, not thorough. | Long runs feel productive. They are usually a desk arguing with itself. |
| 6 | Delegation off | Only named routers route, and only inside their own scope. | An unplanned handoff is how work quietly leaves the map. |

## How to apply them

Open each Desk Charter and check the six rows against it.

- Control 1 lives in the Goal. If the Goal has an "and" in it, split the desk.
- Control 2 lives in Handoffs. Every arrow should point at a named desk.
- Control 3 lives in the Output contract. If a script could not check it, rewrite it until one could.
- Controls 4 and 5 live in the Failure rule. Copy the numbers in.
- Control 6 lives in Hard boundaries. Add "never hand work to a desk not listed under Handoffs."

## The rule behind the rules

Consistency is a byproduct of structure, not of intent, memory, or discipline. A team saying "we should be consistent about AI" is asking for architecture, so give it architecture.
