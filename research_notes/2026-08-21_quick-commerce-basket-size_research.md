# Research Notes: The 10 Minutes Was Never the Business Model

## Topic Selected

The real business lever behind India's quick commerce apps (Blinkit, Zepto, Swiggy Instamart, Flipkart Minutes): average order value, not delivery speed, is what decides unit economics, and the fee/nudge prompts inside these apps exist to move that number up.

## Why It Was Selected, and an Important Course Correction

This topic replaces an earlier draft produced earlier in this same session, "The Loan App Does Not Need You to Repay" (about RBI's Default Loss Guarantee cap on loan apps). That draft was fully written, researched and rendered before being discarded. It is documented here because the reason for discarding it is itself a significant finding for Kevin.

While attempting the Google Drive delivery step for the loan-app carousel, this session found the shared Drive delivery folder (https://drive.google.com/drive/folders/172n6BtZiBcFQYVn3oyMraQrYH0yKJ4Kl) contains dated subfolders going back to 2026-07-27, i.e. a real production history that this repository's `published_log.csv` and `carousel_topic_bank.md` do not reflect (both show zero prior published topics). Cross-checking against the GitHub repository confirmed why: 26 `claude/gracious-goodall-*` branches exist, each holding one day's work, and only one pull request has ever been opened (PR #1, from 2026-07-27, still open and unmerged). Every daily run has been branching from `main`, which has never absorbed any prior day's `published_log.csv` or `carousel_topic_bank.md` updates, so each run's history check has been running against a permanently empty record.

The practical effect: the Drive folder shows the exact same "loan apps feel harmless" topic already produced on 2026-08-09 (folder: `2026-08-09_loan-apps-feel-harmless`) and a close variant on 2026-08-11 (`2026-08-11_loan-apps-small-loans-feel-harmless`), plus two more loan-app carousels on 2026-08-14 (`small-loan-disclosure-rule`, about the Key Fact Statement and APR-vs-EMI) and 2026-08-19 (`loan-app-friction-design`, about RBI's working-group figures and the DLA directory). This session's independently-chosen loan-app carousel would have been a fifth near-duplicate in roughly two weeks. Other topics show the same pattern: "no-cost-emi-hidden-cost" or close variants appear on 2026-07-27, 07-28, 07-29, 08-01, 08-06, 08-13 and 08-17 (six to seven times), and "credit-card-minimum-due-trap" or close variants appear on 08-02, 08-03, 08-07, 08-08, 08-10 and 08-20 (six times).

Given this, the loan-app carousel drafted earlier in this session was deleted rather than committed, and this topic (quick commerce basket-size economics) was chosen instead, since no prior Drive folder covers it. This is flagged prominently to Kevin as a routine-level issue that needs fixing (either merge the outstanding branches/PR regularly, or change the routine so it pushes directly to `main`, or have the routine check the Drive folder's history in addition to the git repo before finalising a topic), separate from today's actual deliverable.

## Why This New Topic Was Selected

- Priority order match: "timely and verifiable Indian business development" (quick commerce fee changes and market growth are active through 2025–2026) and "a business model with a hidden mechanism" (average order value, not delivery speed, as the real profitability lever).
- Zero overlap with any topic found in the Drive delivery folder's history (checked against all 24 dated folders currently in the destination Drive folder, spanning 2026-07-27 through 2026-08-20).
- Strong "Business Breakdown" structure per the design mastermind: headline claim, customer behaviour, business model, hidden constraint, lesson.
- Gives the reader a concrete, personally checkable habit (pausing before an "add more to avoid a fee" prompt) rather than generic advice.

## Primary Sources Consulted

Direct fetches to company investor-relations pages and individual platform fee/terms pages were not attempted in this session due to the same network egress restrictions observed earlier (several domains blocked with `EGRESS_BLOCKED`). Research relies on two targeted web searches, each returning summaries that cite multiple industry and market-analysis outlets.

Sources referenced by the search results:

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
- India.com — "Bad news for Zomato Blinkit, Swiggy Instamart, Zepto customers, now pay these fees for orders...": https://www.india.com/business/bad-news-for-zomato-blinkit-swiggy-instamart-zepto-customers-now-pay-service-fees-for-orders-do-not-meet-mov-7917273/
- Upstox — "Zepto scraps all handling, surge fees; How does it stack up against Instamart and Blinkit?": https://upstox.com/news/business-news/latest-updates/zepto-scraps-all-handling-surge-fees-how-does-it-stack-up-against-instamart-and-blinkit/article-183964/
- NewsBytes — "Zepto drops all fees, offering free delivery above ₹99 orders": https://www.newsbytesapp.com/news/business/zepto-waives-handling-surge-fees-to-take-on-blinkit-instamart/story
- Growww Tech — "Blinkit vs Zepto vs Instamart: Fee Breakdown": https://growwwtech.com/blog/blinkit-vs-zepto-vs-instamart-fees-d2c-brands

## Research Notes

**Market scale**
- Quick-commerce GMV reportedly reached roughly ₹11,000 crore in a single month in early 2026, described as up about 100% year on year, on roughly 7.8 million orders a day.
- Industry estimates put the total number of dark stores in India at roughly 5,000–5,500, led by Blinkit, Zepto and Swiggy Instamart.
- These macro figures were not used on-slide; they are background context only, since they are the least independently verifiable numbers found in this research pass.

**Dark store economics (structural claim used on Slide 4)**
- A typical dark store is reported as 1,000–2,000 sq ft of commercial space, usually ground floor, serving a delivery radius of roughly 3–4 km.
- The core structural claim used on-slide, that a dark store's fixed costs (rent, staff, inventory holding) do not meaningfully shrink for a smaller individual order, is a general industry-economics point repeated across multiple sources rather than a single citable statistic, and is treated as a structural, not company-specific, claim.

**Average order value by platform (used on Slide 5)**
- Blinkit: reported AOV of approximately ₹547, across roughly 2,027 active dark stores in about 200 cities, with roughly 1,200 daily orders per dark store.
- Zepto: reported AOV of approximately ₹390, across roughly 1,113 active dark stores in about 70 cities, with roughly 1,757 daily orders per dark store (highest order-frequency figure found).
- Flipkart Minutes: reported AOV of approximately ₹750–800, across roughly 800 active dark stores in 80–100 cities. This is the newest entrant and its figures appear in fewer independent sources than Blinkit's or Zepto's.
- Profitability framing: search results describe Blinkit as closest to profitability among the three, with Swiggy Instamart and Zepto described as still posting large, and in Zepto's case widening, losses through 2025. This framing is used narratively on Slide 5 but not quantified with a specific loss figure, since no single reliable loss number was found across sources.

**Fees (referenced conceptually, not with a frozen figure, on Slide 6)**
- Through 2025, multiple platforms introduced handling fees, small-cart fees and platform fees on orders below a minimum value. Reported example figures (not used on-slide as fixed facts, since they are volatile): Blinkit charging roughly ₹54 extra on orders under ₹99 (a mix of delivery, small-cart and handling charges) and roughly ₹30 for deliveries under ₹199; Instamart charging roughly ₹55 extra on orders under ₹99 with platform fees separately ranging ₹2–₹10.
- Zepto is reported to have reversed course and scrapped handling and surge fees, lowering its free-delivery threshold to ₹99, which is exactly why this carousel avoids citing one frozen fee number as a central fact: the figures are already inconsistent across platforms and actively changing.

## Claims Included in the Carousel

1. A dark store's fixed costs do not meaningfully shrink for a smaller order, so average order value, not delivery speed, is the metric that decides margin. (Slide 4) — structural industry claim, not a single citable statistic.
2. Average order value differs meaningfully across platforms (Blinkit ≈ ₹547, Zepto ≈ ₹390, Flipkart Minutes ≈ ₹750–800), and the platform with the highest AOV is described as closest to profitability. (Slide 5) — sourced to industry/market reporting, flagged [VERIFY].
3. Quick commerce platforms use fee prompts and minimum-order nudges to push order value up; the specific fee amounts are not stated on-slide since they vary by platform and have changed multiple times through 2025–2026. (Slide 6)

## Claims Removed Because They Were Not Adequately Verified

- The ₹11,000 crore monthly GMV and 7.8 million orders/day figures were considered for the caption or an early slide but excluded from on-slide copy, since they come from a single search-summary pass without independent primary-source confirmation and are the kind of large, round, fast-moving statistic that ages poorly.
- Specific fee amounts (e.g., "₹54 extra on orders under ₹99") were excluded from on-slide copy for the reason described above: multiple platforms have already changed these amounts within the past year, and Zepto has dropped some entirely, so freezing one number risks becoming visibly wrong within weeks.
- Any specific reported loss figure for Zepto or Swiggy Instamart was excluded, since no single reliable, dated figure was found across the sources checked in this pass.

## [VERIFY] Items

- [VERIFY] The three AOV figures (Blinkit ₹547, Zepto ₹390, Flipkart Minutes ₹750–800) and the associated dark-store counts, directly against the most recent investor disclosures (Eternal Ltd. for Blinkit) or high-quality reporting dated as close to publish time as possible. This session could not fetch investor-relations pages directly.
- [VERIFY] The "Blinkit is closest to profitability" framing, since profitability positioning in this sector changes quarter to quarter.
- [VERIFY] That Slide 6's fee-prompt framing stays accurate at publish time, i.e. that platforms still use some form of minimum-order or fee-avoidance nudge, even though this carousel deliberately does not cite one specific frozen amount.

## Source Links and Dates

| Source | Date | Used for |
|---|---|---|
| iThink Logistics, Unicommerce, Startupfeed, RevQ, Digital in Asia, AIIQA, Cityscope, Legal Parivar News, Berkeley CMR (industry/market analysis, secondary) | Articles dated 2026 | Dark-store structure, AOV-by-platform figures, profitability framing |
| Storyboard18, India.com, Upstox, NewsBytes, Growww Tech (industry/consumer reporting, secondary) | Articles dated 2025–2026 | Fee-structure context (used conceptually, not as a frozen figure) |
