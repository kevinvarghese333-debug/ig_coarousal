# Research Notes — "The company is growing. Its cash is missing."

## Topic selected

Why a company can report profit while its cash position is deteriorating: the gap between accrual profit and actual cash collection, and why growth widens rather than closes that gap.

## Why it was selected — and an important correction mid-run

This session initially selected "Why zero-cost EMI is not always a free decision" (the #1 item in `carousel_topic_bank.md`), since the repo's own `published_log.csv` and `carousel_topic_bank.md` showed no prior published topics.

Before finalising that draft, this session checked the connected Google Drive delivery folder (https://drive.google.com/drive/folders/172n6BtZiBcFQYVn3oyMraQrYH0yKJ4Kl) and found **an extensive history of prior runs that the GitHub repository does not reflect**. The Drive folder contains dated subfolders going back to at least 2026-07-27, and the "no-cost EMI" / "zero-cost EMI" topic (under slightly varied slugs: `no-cost-emi-hidden-cost`, `zero-cost-emi-hidden-cost`, `no-cost-emi-real-cost`, `no-cost-emi-hidden-interest`, `zero-cost-emi-not-free`) had already been produced roughly 25+ times, including **the day before this run (2026-09-27)**, under the title `2026-09-27_zero-cost-emi-hidden-cost`.

This means the account's actual topic-repetition state was completely different from what the repo's tracking files suggested. Producing the same topic again today would have been the ~26th near-duplicate carousel on this exact idea in about nine weeks, a direct violation of the "do not repeat a topic from the prior 30 days" rule, so the original draft, research file and rendered PNGs for that topic were discarded before completing this run, and this topic was substituted instead.

**This is flagged as a priority item for Kevin** — see the note at the bottom of this file and the final response.

Other topics found repeated multiple times in the Drive history: "credit-card-minimum-due-trap" (~7 occurrences) and various loan-app framings (~5 occurrences: harmless, friction-design, cooling-off-window, disclosure-vs-design, engineered-ease). By contrast, no business-case-study, investor-lens, or company-analysis carousel appeared anywhere in the visible Drive history, which is also a real gap in the content mix per the routine's own instructions ("gaps in the existing topic mix").

"Why a company can report profit while cash is disappearing" (item 6 in the topic bank) was chosen because:
- It is not a repeat of anything found in the Drive history (checked directly).
- It fills the business-breakdown / investor-lens gap noted above.
- It is evergreen and explains a real, well-established accounting mechanism rather than depending on a fragile or fast-moving data point, which was a safer choice given this session's limited web-fetch access (see Access Notes).
- It fits the "Investor Lens" carousel type in the mastermind doc (popular belief → mechanism → what it misses → investor takeaway) without giving any stock tip or buy/sell recommendation.

## Access notes (carried over, applies to this run too)

This session's outbound network access goes through a proxy that allowed `WebSearch` calls but blocked `WebFetch` to every URL attempted (rbi.org.in, business-standard.com, moneylife.in, en.wikipedia.org were all tried and blocked earlier in this run on the discarded EMI topic). Research for this topic likewise relies on WebSearch snippets rather than full page reads. This is lower-risk here than for the EMI topic because the core claims are general, uncontested accounting principles rather than a specific regulator circular or company figure.

## Primary sources consulted

Not applicable in the regulator/filing sense — this topic explains a general accounting mechanism rather than a specific regulation, company, or current event, so no RBI/SEBI/NSE/BSE primary source is required. See `output/2026-09-28_profit-cash-gap/sources_and_fact_check.md` for the general finance explainers consulted for terminology and grounding.

## Claims included in the carousel

1. Profit is recognised (booked) at the point of invoicing under accrual accounting, while cash is recognised only when received. (Slide 4)
2. Real-world payment terms commonly create a 60-120 day gap between invoicing and collection. (Slide 4)
3. Faster revenue growth increases the amount of cash tied up in unpaid receivables at any given time. (Slide 6)
4. An illustrative ₹1 crore example showing profit booked on Day 1 versus cash collected on Day 90. Explicitly framed as an example, not a real transaction. (Slide 5)

## Claims removed because they were not adequately verified

- Any specific real Indian company was considered as the illustrative example and deliberately not used, since this session could not independently verify a specific company's receivables, profit, or cash-flow figures from a primary source (annual report, investor presentation, or NSE/BSE filing) within this session's access constraints.
- No industry-specific "typical" receivable-days figure was asserted, since this varies too much by sector to state as one verified number.

## All [VERIFY] items

None for this topic's on-slide claims (see `sources_and_fact_check.md`). The only carried-over [VERIFY] item is the meta-level one below.

## Priority follow-up for Kevin (not a slide claim, but important)

**[VERIFY / ACTION]** The dedup mechanism between this GitHub repository and the actual publishing history is broken. `published_log.csv` and `carousel_topic_bank.md` in this repo were empty/unused before this run, but Google Drive shows dozens of prior runs with real topics and dates. Two possible explanations: (a) prior runs used a different repository or branch that was later disconnected, or (b) prior runs generated content but never successfully committed their `published_log.csv` / `carousel_topic_bank.md` updates back to this repo. Kevin should check which, and consider backfilling this repo's `published_log.csv` from the Drive folder's dated subfolders so future runs (including this one) have an accurate 30-day lookback and stop repeating the same handful of topics.

## Source links and dates

| Source | URL | Date |
|---|---|---|
| Ramp blog | https://ramp.com/blog/are-you-turning-a-profit-but-running-out-of-cash | undated explainer |
| Beancount.io blog | https://beancount.io/blog/2026/04/23/profitable-but-broke-why-businesses-run-out-of-cash | 23 Apr 2026 |
| Varsity Tutors | https://www.varsitytutors.com/practice/subjects/corporate-finance/lessons/working-capital-and-cash-flow | undated |
