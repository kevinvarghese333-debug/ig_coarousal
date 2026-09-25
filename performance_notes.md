# Performance Notes

Add results after each post: reach, saves, shares, comments, profile visits, follows, strongest comment, and what to repeat or avoid.

## Operational flag (2026-09-25)

Not a performance note, but worth reading before the next scheduled run:
this repository's `main` branch cannot currently be trusted as the routine's
history. Every scheduled run pushes to its own uniquely named branch
(`claude/gracious-goodall-*`); `git ls-remote` shows 57 such branches as of
this run, and only one pull request has ever been opened (PR #1, from
2026-07-27, still open and unmerged). `main`, and therefore this file,
`published_log.csv` and `carousel_topic_bank.md`, has never actually
accumulated history from any of those runs.

The connected Google Drive delivery folder is the only reliable record of
what has actually been produced. As of this run it shows roughly 50+ prior
carousels, heavily concentrated on 3 to 4 near-identical topics: "no-cost
EMI hidden cost" alone accounts for well over a dozen runs, several within
days of each other, and "credit card minimum due trap" / "on-time payment"
variants account for most of the rest. This run itself started by drafting
a credit-utilization carousel that turned out to duplicate a 2026-08-18
Drive carousel almost exactly, caught only by manually checking Drive.

Recommend either merging the outstanding branches/PRs so `main` accumulates
real history, reconfiguring the routine so each run branches from and
merges back into a shared branch, or treating Drive as the canonical
topic-dedup source until the branching setup is fixed. Until then, every
run risks silently repeating recent topics.
