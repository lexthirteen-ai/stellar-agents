# Audit Log

Append only. One line per event. Never edit or delete a line. A correction is a new line that names the line it corrects.

## Format

```
YYYY-MM-DD HH:MM | EVENT | desk-id | note
```

## Events

| Event | When |
|---|---|
| REGISTERED | A desk was added to the registry after an approved proposal |
| MODIFIED | A charter, cadence, or write zone changed after an approved proposal |
| RUN | A scheduled or triggered run completed and produced its contract |
| PARTIAL | A run hit its time cap and wrote what it had |
| STALL | A run hit its retry cap and stopped |
| REJECTED | Vesper, the Copy Desk, refused a draft, with the rule named |
| VIOLATION | A record contradicted the files, or a desk wrote outside its zone |
| CORRECTED | A new line fixing an earlier one. The earlier line stays. |
| APPROVED | The owner ticked a proposal box |
| CARRIED | The owner carried a staged file across in the real tool |
| EXPIRED | A box went unticked past its limit and was closed as a no, with its age |
| FINDING | Thuban found a record that disagrees with the map or a run that never happened |
| INSTALLED | The installer wrote or upgraded the kit, with the version |

## Rules

- Silent fixes are violations. If a file was changed to fix a mistake and no CORRECTED line exists, that is a VIOLATION line waiting to be written.
- Back dating is forbidden. The timestamp is when the line was written, not when the event should have happened.
- Machine records use the plain desk id. Personas perform in prose only.

## A correction, for example

```
YYYY-MM-DD 08:05 | MODIFIED | aurora-reporter | cadence written as Tue Wed Thu
YYYY-MM-DD 08:06 | CORRECTED | aurora-reporter | corrects 08:05 line, cadence is Tue Thu per proposal, the 08:05 line stays
```

## Log

```
```
