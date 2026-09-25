# Research Notes: The Business Behind 10-Minute Delivery

## Topic Selected

Why Blinkit's first-ever profitable quarter at real scale still ran on a razor-thin
margin, and what that says about the quick-commerce business model generally.

## Why This Topic Was Selected

- Timely: Eternal Limited (formerly Zomato, Blinkit's listed parent) reported Q4
  FY26 results showing Blinkit's first adjusted-EBITDA-positive quarter, which is
  a genuine, current business development, not an evergreen filler topic.
- Verifiable: figures trace to Eternal's quarterly results, a listed company's
  public disclosure, corroborated across multiple independent financial-press
  reports.
- Fills a real gap in this page's actual output. A full audit of the connected
  Google Drive delivery folder (see process note below) shows that, across
  roughly two months of daily runs, this page has produced dozens of carousels
  but almost all of them cluster around 3 to 4 topics: "no-cost EMI hidden
  cost" (13+ occurrences), "credit card minimum due trap" (8+ occurrences),
  and assorted "on-time payment / credit score timing" variants (at least 3
  occurrences, including one from 2026-08-18 that is nearly identical to the
  topic this run originally drafted before the duplication was caught). No
  prior carousel in the Drive history covers a company/business-model
  breakdown. This is the first.
- Matches "The Business Breakdown" / "Investor Lens" structure in the design
  mastermind doc: popular belief (quick commerce looks like an obvious
  success story) -> number/mechanism (a 0.26 percent margin) -> what it
  misses -> investor takeaway. No stock tips or buy/sell calls are made,
  consistent with brand rules.

## IMPORTANT Process Note: Why the Topic Changed Mid-Run

This run originally researched and fully rendered a different carousel:
"Why people who pay their credit-card bill in full and on time can still get
into money trouble" (utilization ratio vs. statement date). Before finalizing,
this run checked the connected Google Drive delivery folder
(https://drive.google.com/drive/folders/172n6BtZiBcFQYVn3oyMraQrYH0yKJ4Kl)
for prior history, since this repository's own `published_log.csv` and
`carousel_topic_bank.md` showed no prior published topics (both were
effectively empty at the start of this run).

That Drive folder shows the routine has actually run roughly 50+ times since
2026-07-27, but `git ls-remote` on this repository shows 57 branches, one per
past run, and only a single pull request has ever been opened (PR #1, from
2026-07-27, still open and unmerged as of this run). Because nothing merges
back into `main`, every new scheduled run branches from an effectively blank
`main` and has no way to see prior work through the repository alone.

Checking Drive directly surfaced a 2026-08-18 carousel titled "The Credit
Score Timing Trap" with a central idea, mechanism, and even caption phrasing
nearly identical to the one this run had just built (banks reporting the
statement-date balance to the bureau regardless of later payment; the fix
being "check your statement date, not your due date"). Publishing that would
have violated the brand's own one-idea/no-repeat rule in substance, even
though the repo's own tracking files could not have caught it. The original
draft, research file and rendered PNGs for that topic were discarded before
being committed anywhere, and this "10-minute delivery" topic was produced
instead.

This is flagged prominently in this run's final report and in
`carousel_topic_bank.md`, since it is a real, ongoing content-strategy risk
for the page, not a one-off issue.

## Primary and Secondary Sources Consulted

Direct fetches of several financial news sites (Business Standard, Upstox,
Entrackr, The Arc, Outlook Business) were blocked by this session's network
egress policy, so this research relies on search-engine result summaries of
those and other outlets, cross-checked across multiple independent queries
for consistency. Figures below were corroborated across at least two to
three independently returned sources each. Kevin should re-verify against
Eternal Limited's official investor-relations filing or press release before
publishing, since this run could not read the underlying primary documents
directly.

1. Search results summarizing Eternal Limited's Q4 FY26 (quarter ended March
   2026) results, including coverage from thearcweb.com, upstox.com,
   entrackr.com, sahi.com, ziromarket.com and growthvista.in (all accessed
   2026-09-25 via search, direct fetch blocked by network policy). Consistent
   figures across sources:
   - Blinkit's adjusted EBITDA turned positive for the first time, at
     approximately Rs 37 crore, on Net Order Value (NOV) of approximately
     Rs 14,386 crore for the quarter, implying a margin of roughly 0.26
     percent of NOV.
   - Eternal Limited's consolidated net profit for Q4 FY26 was reported at
     approximately Rs 174 crore, up roughly 346 percent year-on-year from
     approximately Rs 39 crore in Q4 FY25.
   - Blinkit's dark store count was reported at 2,200+ as of this period,
     against a reported 1,100+ for Zepto.
2. Search results summarizing Zepto's FY26 IPO/DRHP-linked disclosures,
   including coverage from Outlook Business and Ascendants (accessed
   2026-09-25 via search, direct fetch blocked). Consistent figures:
   - Zepto's operating revenue for FY26 was reported at approximately
     Rs 22,623 crore, roughly double FY25's approximately Rs 11,110 crore.
   - Zepto's net loss for FY26 was reported at approximately Rs 5,905 crore,
     up from approximately Rs 4,695 crore in FY25.
   - Zepto's adjusted EBITDA loss per order was reported to have improved
     to approximately Rs 78.75 in FY26 from approximately Rs 136.15 in
     FY25, with further improvement to roughly Rs 59.40 per order reported
     in Q4 FY26 specifically.

## Claims Included on Slides (and hedging used)

| On-slide claim | Basis | Hedge used |
|---|---|---|
| Blinkit posted its first adjusted-EBITDA-positive quarter | Multiple corroborating press summaries of Eternal's Q4 FY26 results | Stated as fact, attributed to the quarter, sourced note on slide |
| That profit was about Rs 37 crore on about Rs 14,386 crore of order value, roughly 0.26 percent | Same, cross-checked across 3+ sources | Stated as fact with "about" / "roughly" |
| A rival quick-commerce company (Zepto) posted a large loss for the same year despite revenue nearly doubling | Corroborated FY26 figures from IPO-linked press coverage | Stated as fact, company named, no specific claim about its investment merits |
| Running dark stores and fast delivery fleets close to customers creates largely fixed costs that do not fall just because a slow week happens | General, well-established logistics/retail economics reasoning, not tied to one filing | Framed as mechanism/reasoning, not a quoted figure |

## Claims Removed or Not Used

- No claim is made about whether Blinkit or Zepto will become durably
  profitable, whether either company is a good investment, or any
  forward-looking financial projection. This avoids the brand's rule against
  investment calls and unverifiable predictions.
- No per-order profit/loss figure is presented as exact to the rupee; all
  figures use "about" or "roughly" given they are drawn from press summaries
  of results rather than a directly read primary filing.
- Store counts, order volumes and market-share figures beyond what is needed
  for the core idea were left out to keep the carousel to one idea.

## [VERIFY] Items (flag before publishing)

1. [VERIFY] Confirm the exact Q4 FY26 Blinkit adjusted EBITDA (~Rs 37 crore)
   and Net Order Value (~Rs 14,386 crore) figures directly against Eternal
   Limited's official investor presentation or exchange filing for that
   quarter, since this run could not fetch primary sources directly (network
   egress to major financial news domains was blocked).
2. [VERIFY] Confirm Zepto's FY26 net loss (~Rs 5,905 crore) and revenue
   (~Rs 22,623 crore) figures against its IPO prospectus (DRHP/RHP) directly,
   since this run relied on press summaries of the filing rather than the
   filing itself.
3. [VERIFY] Confirm dark store counts (Blinkit 2,200+, Zepto 1,100+) are
   current as of publish date, since these numbers change quickly in this
   sector.

## Source Links (as returned by search, access dates 2026-09-25)

- https://www.sahi.com/blogs/eternal-limited-zomato-parent-q4-fy26-results-analysis
- https://upstox.com/news/market-news/stocks/eternal-share-price-here-is-how-blinkit-fares-against-its-rivals-after-q4-fy-26/article-192919/
- https://entrackr.com/analysis/eternals-reality-check-blinkits-thin-margins-and-districts-losses-11777148
- https://www.thearcweb.com/article/blinkit-zomato-eternal-quick-commerce-Q4-results-food-delivery-IGbWzh0VOAzqIhIC
- https://www.ziromarket.com/blog/eternal-zomato-blinkit-q4-fy26-results
- https://www.growthvista.in/blog-detail/eternal-q4-results-fy26-profit-jumps-346-to-rs-174-crore-blinkit-powers-massive-growth/406
- https://www.outlookbusiness.com/markets/ipo-bound-zepto-doubles-revenue-in-fy26-but-losses-reach-5905-cr
- https://ascendants.in/business-stories/zepto-fy26-revenue-losses-quick-commerce/
- https://www.forbesindia.com/article/news/deep-dive/how-zeptos-burning-cash-chasing-growth/2994869/1

## Google Drive History Audit (for future runs, see process note above)

Dated subfolders observed under the connected Drive delivery root as of
2026-09-25 (titles only, not exhaustive, most recent first): 2026-09-24
no-cost-emi-hidden-cost, 2026-09-23 minimum-due-credit-card-trap, 2026-09-22
zero-cost-emi-not-free, 2026-09-21 no-cost-emi-hidden-cost, 2026-09-20
no-cost-emi-hidden-cost, 2026-09-19 credit-card-minimum-due-trap, 2026-09-18
no-cost-emi-hidden-cost, 2026-09-17 no-cost-emi-hidden-cost, 2026-09-16
why-loan-apps-feel-harmless, 2026-09-15 no-cost-emi-hidden-cost, 2026-09-14
zero-cost-emi-hidden-cost, 2026-09-13 no-cost-emi-hidden-interest, 2026-09-12
on-time-not-in-full, 2026-09-11 no-cost-emi-hidden-cost, 2026-09-10
no-cost-emi-hidden-cost, 2026-09-09 zero-cost-emi-hidden-cost, 2026-09-08
loan-app-hidden-cost, 2026-09-07 no-cost-emi-hidden-cost, and similar
patterns continuing back through July 2026, including 2026-08-18
credit-score-timing-trap (the near-duplicate of this run's discarded draft)
and 2026-07-30 on-time-credit-card-trap. Recommend Kevin either merges the
outstanding branches/PRs so `main` accumulates real history, or treats Drive
as the canonical topic-dedup source until that is fixed.
