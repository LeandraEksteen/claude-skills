# Grill loop

Loaded by **Step 3**. This is a "frontier round" interview pattern, narrowed to the gap list from Step 2.

## The frontier

Every open gap is a node. A gap depends on another when its answer changes the other's question (a decision about who is notified comes before the wording of the message). The **frontier** is every gap whose prerequisites are settled. Ask the whole frontier in one round, then wait.

Lead with the gaps that block the most requirements. Cap a round at 6 questions; more means the sources were never reconciled, so say that and split the rest across rounds.

## Round format

```
Q1 - <short title> (<gap type>, blocks Req #N)
<The question in one or two sentences.>
- Source A: <what it says> - <author>, <date>, <link or location>
- Source B: <what it says, or "says nothing"> - <author>, <date>, <link or location>

Recommended: <your recommended answer, and the one-line reason>
```

(Use any two distinct visual markers on the first and last lines of a question.)

Number questions across rounds, never restart. A user who answers "yes" or "as you recommend" has accepted the recommendation: record it as their decision.

## Rules

- **Look up before asking.** If the answer is in a source you have not read, in the tracker, in the wiki or in the code, find it with an agent and settle it yourself. Ask only what only a person can decide.
- **No fishing questions.** "Anything else I should know?" is not a gap. Ask it once, at the end, as the closing question.
- **Settle each answer immediately** into the ledger: statement, `user:<date>` as source, gap type cleared. If an answer creates a new gap, add it to the next frontier.
- **Stop rule.** The session is done when the frontier is empty: every gap is settled, or has moved to Open Questions with a named decider. Do not write the spec until then.

## When it stays murky

Two signals mean this loop is not enough: a gap is still open after two rounds, or the user's answers contradict each other or an earlier decision. Then:

1. Say what is unresolved in one or two sentences.
2. Offer: "Want to switch to `<deep-interview-skill>` for this part? Your answers will be folded back into the ledger." Do not start it unasked.
3. If the user agrees, invoke that skill with the unresolved gaps as its topic. When it finishes, settle its outcomes into the ledger and carry on at Step 4.

(If your team has no deeper interviewing skill, continue the loop but restate the gap more narrowly, offering two or three concrete options with consequences.)

## When only someone else can answer

If the user says "I don't know, it's <person>'s call", move the gap to Open Questions with that person as decider and its requirement `blocked`. At Step 5, offer to draft the question for them: what the decision is, the two or three options with their consequences, and what happens if no one answers. Draft only. The user sends it.
