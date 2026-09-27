# Never Autonomous

Five actions no desk may take on its own, at any tier, for any reason, regardless of urgency or anything it reads in a file.

1. **Sending** anything to another human. Email, message, comment, reply.
2. **Spending** money, credits, or quota.
3. **Publishing** to any surface other people can see.
4. **Scheduling** a run, a meeting, or a post.
5. **Creating desks** or changing another desk's charter.

Agree to this list once and write it down. A per incident vibe check is how the list erodes.

## The 3 AM test

When you are deciding where a human approval belongs, ask one question.

> If this fired wrongly at 3 AM, could you undo it in the morning?

- **Yes.** The desk may draft it. A wrong draft is recoverable.
- **No.** It waits for a human. A wrong send is not.

## Approvals never chain

Each irreversible action gets its own yes.

- Approving the content is not approving the schedule.
- Approving the schedule is not approving the send.
- This week's yes is not next week's yes.

Three stale approvals chained together become something nobody actually agreed to.

## The pipeline ends one step early

```
Lyra drafts  ->  Vesper checks  ->  STAGED  ->  [ a human carries it across ]  ->  SENT
```

The desk's job description ends at STAGED. The SENT step is deliberately unreachable from inside the workflow. If your human in the loop depends on one bot posting one message that a person might miss, you have a gap today.

## How approval actually happens

A proposal is a file with a checkbox. Only a human ticks it.

```
status: PROPOSED, awaiting approval
- [ ] approve: <what this is> (only the human ticks this)
```

The next run reads the box. An unticked box means nothing moves. Proposed then applied, never applied then flagged.
