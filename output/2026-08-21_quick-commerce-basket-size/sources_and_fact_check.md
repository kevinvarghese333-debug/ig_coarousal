# Sources and Fact Check: The 10 Minutes Was Never the Business Model

## Claims used on the slides

| Slide | Claim | Source | Date | Status |
|---|---|---|---|---|
| 4 | A dark store's fixed costs (rent, staff, inventory holding) do not meaningfully shrink for a smaller individual order | General quick-commerce industry/dark-store economics analysis (multiple secondary sources) | 2026 | Structural claim, not a single citable statistic |
| 5 | Average order value: Blinkit ≈ ₹547, Zepto ≈ ₹390, Flipkart Minutes ≈ ₹750–800 | Industry/market analysis reporting (multiple secondary sources) | Reported early 2026 | [VERIFY] — corroborated across one search pass citing several outlets; not independently confirmed against primary investor disclosures |
| 5 | The platform with the highest average order value (Flipkart Minutes) is described as closest to profitability among the three named | Same as above | Reported early 2026 | [VERIFY] — same as above |
| 6 | Quick commerce platforms use fee prompts and minimum-order nudges to encourage larger baskets | Multiple 2025–2026 reports on platform fee changes | 2025–2026 | Verified concept; no specific frozen fee figure used on-slide since amounts vary by platform and have changed repeatedly |

## Why the AOV figures are marked [VERIFY]

This session's sandbox could not fetch company investor-relations pages or primary filings directly. The AOV and dark-store-count figures come from a web search that returned a synthesized summary citing multiple industry/market-analysis outlets, which is a reasonable basis to publish with a citation but not the same as reading a primary filing. Kevin should confirm the specific ₹547 / ₹390 / ₹750–800 figures against the latest investor disclosures (Eternal Ltd. for Blinkit) or credible, recently dated reporting before publishing, since quick-commerce operating metrics move quickly quarter to quarter.

## Full source list consulted

- iThink Logistics — "Top 7 Quick Commerce Companies In India: Meaning, Apps 2026": https://www.ithinklogistics.com/blog/quick-commerce-companies-in-india/
- Unicommerce — "Quick Commerce in India: Scope, Business Models, Challenges & Strategies": https://unicommerce.com/blog/what-is-q-commerce-india-trends-models-challenges/
- Marketbites (Substack) — "Why are quick-commerce apps ditching 10-minute delivery?": https://marketbites.substack.com/p/why-are-quick-commerce-apps-ditching
- Startupfeed — "Quick Commerce War 2026: Blinkit Tops Brutal 6-Way Fight": https://startupfeed.in/quick-commerce-war-2026-blinkit-zepto-instamart-amazon-flipkart/
- RevQ — "Dark Stores Explained: The Infrastructure Behind Quick Commerce in India (2026)": https://www.revq.in/dark-stores-explained-the-infrastructure-behind-quick-commerce-in-india-2026
- Digital in Asia — "India Quick Commerce 2026: Blinkit, Zepto, Instamart": https://digitalinasia.com/india-quick-commerce-blinkit-zepto-instamart/
- AIIQA — "Quick Commerce in India: Is the 10-Minute Delivery Model Profitable or Just a Bubble?": https://www.aiiqa.com/blogs/quick-commerce-in-india-is-the-10-minute-delivery-model-profitable-or-just-a-bubble/
- Cityscope — "Analyzing India's Quick Commerce War, 2026": https://www.cityscope.media/article/analyzing-indias-quick-commerce-war-2026
- Legal Parivar News — "The Dark Store Decade: How Hyperlocal Commerce Is Rewriting India's E-commerce Playbook": https://news.legalparivar.com/the-dark-store-decade-how-hyperlocal-commerce-is-rewriting-indias-e-commerce-playbook/
- Berkeley CMR — "The Dark Store Revolution: How India's 10-Minute Economy Is Redefining Retail Infrastructure": https://cmr.berkeley.edu/2026/01/the-dark-store-revolution-how-indias-10-minute-economy-is-redefining-retail-infrastructure/
- Storyboard18 — "Blinkit, Zepto, Instamart raise consumer fees as ultra-fast delivery becomes lifestyle": https://www.storyboard18.com/brand-marketing/blinkit-zepto-instamart-raise-fees-as-quick-commerce-goes-mainstream-ws-l-99758.htm
- India.com, Upstox, NewsBytes, Growww Tech — fee-structure reporting (see research_notes/2026-08-21_quick-commerce-basket-size_research.md for full links)

## Claims deliberately excluded from the carousel

- Monthly quick-commerce GMV (~₹11,000 crore) and daily order volume (~7.8 million) figures: excluded from on-slide copy and caption, kept as background context only in research notes, since they come from a single search-summary pass without independent primary confirmation.
- Specific fee amounts (e.g., "₹54 extra on orders under ₹99"): excluded, since multiple platforms have changed these amounts within the past year and one (Zepto) has dropped several fees entirely. Slide 6 references the fee-prompt mechanism conceptually rather than with a frozen number.
- Any specific reported loss figure for Zepto or Swiggy Instamart: excluded, no single reliable, dated figure was found.

## Note on this carousel's topic and a production-process finding

This topic was chosen after an earlier draft on a different subject (loan apps and RBI's Default Loss Guarantee cap) was fully researched, written and rendered in this same session, then discarded before committing. While attempting the Google Drive delivery step for that draft, this session discovered the shared Drive folder holds a real production history back to 2026-07-27 that this repository's `published_log.csv` and `carousel_topic_bank.md` did not reflect, including a folder from 2026-08-09 titled `loan-apps-feel-harmless`, essentially the same topic and slug this session had independently chosen. Investigating further found 26 unmerged `claude/gracious-goodall-*` branches on GitHub and only one, still-open pull request (#1, from 2026-07-27), meaning each day's run has been branching from a `main` that never absorbed any prior day's history file updates. That is a routine-level issue, documented in full in `research_notes/2026-08-21_quick-commerce-basket-size_research.md`, and flagged separately to Kevin. This carousel's topic (quick commerce basket-size economics) was confirmed against the actual Drive folder history and has no overlap with any prior dated folder found there.

## Missing fonts

As with the discarded draft, `fonts/PlayfairDisplay-*.ttf` and `fonts/DMSans-*.ttf` are not present in the repository. This run used DejaVu Serif and DejaVu Sans as fallbacks, chosen because they render the ₹ symbol correctly (the alternative, Liberation Serif/Sans, does not). Add the real brand font files to `fonts/` and re-run `scripts/render_carousel.py` to pick them up automatically.
