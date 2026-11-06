# Source recipes

Loaded by **Step 1**, when the source is one of the kinds below.

## Hosted-document / AI-workspace artifact link

If the URL belongs to a hosted document system that is not an ordinary web page (a notebook, an AI-workspace doc, a canvas), never web-fetch it. Read it through that system's connector: read the project, then the tab or file, then the node you need. Cite it as `artifact:<title>`. A connector that is absent means the link is "Not read" and its requirements are `blocked`.

## Meeting notes / auto-generated meeting summaries

Auto-summaries mislabel decisions and mis-transcribe names and terms.

- Treat the summary's "Decisions" as unconfirmed. Quote the Details/transcript section, not the summary.
- A topic filed under "Needs further discussion" may have been settled in the Details: record the conflict, and let the user decide which stands.
- Note each transcription variant of a name or term (a product, a service, a person) in the spec's Vocabulary.
- Cite it as `meeting:<title, date>`.

## A chat link the user adds mid-run

Read it (chat rules in the Critical block still apply). Then re-open the ledger for every requirement it touches, and say which requirement changed and why, before carrying on. If the spec was already written, this is an amendment: follow `references/amend-mode.md`.
