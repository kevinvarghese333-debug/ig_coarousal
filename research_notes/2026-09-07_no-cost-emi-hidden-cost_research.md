# Research Notes: No Cost EMI Is Not Free

## Topic selected

Why "No Cost EMI" / "zero percent interest" checkout offers are not actually free, and what the cost is disguised as.

## Why it was selected

- It is the #1 priority topic in `carousel_topic_bank.md` and has never been published (log is empty; this is the first run of the routine).
- It is a near-universal behaviour for the 21-40 Indian audience: phones, appliances, and big-ticket purchases are routinely offered on "No Cost EMI" at checkout on marketplaces and in stores.
- It has a clean, verifiable regulatory hook (RBI's stated position that zero percent interest schemes do not genuinely exist) plus well-documented mechanics (processing fees, GST on fees, foreclosure charges) that make the mechanism explainable without speculation.
- It fits the "common and expensive money mistake" and "common audience confusion" priority tiers, and mirrors the exact worked example used in `whenkevintalks_carousel_design_mastermind.md` ("Zero-cost EMI is not always a free decision"), so voice and structure fit alongside the design bible's own guidance.
- No topic has been drafted or published in the last 30 days (published_log.csv is empty), so there is no repeat-topic conflict.

## Primary sources consulted

1. RBI notification, "Zero percent Interest Finance Schemes for Consumer Durables" (PDF hosted at rbidocs.rbi.org.in/rdocs/notification/PDFs/31069.pdf). This is the RBI's own primary document on the subject. **[VERIFY]** The exact circular date and reference number could not be directly confirmed in this session because the RBI document domain (rbidocs.rbi.org.in) is blocked by this environment's outbound network policy and could not be fetched directly. Secondary reporting (below) consistently dates the RBI action to September 2013.
2. Business Standard, "RBI bans zero per cent interest rate scheme for buying goods" (business-standard.com, article URL pattern indicates a September 25, 2013 publish date). Reports that RBI called the zero percent interest concept "non-existent" and said the interest element is "camouflaged" and passed on to the customer as a processing fee. **[VERIFY]** Could not directly re-fetch the full article text in this session (domain blocked by network policy); relying on search-result summary snippets that quote RBI's language consistently across multiple outlets.
3. Business Standard, "RBI asks banks to charge uniform interest rate on retail EMI schemes" (same September 2013 story cluster) — reports RBI's requirement that processing fees and rate of interest be kept uniform across sourcing channels, rather than varied to disguise a "zero percent" headline rate.
4. Moneylife, "RBI says no zero percent interest scheme for buying consumer goods" — independent secondary confirmation of the same RBI notification and its rationale (protecting "vulnerable customers" from schemes designed to allure them).
5. General market reporting on current No Cost EMI mechanics (CardCheck, BankBazaar, CRIF High Mark, aggregated via search) on: processing fees typically in the 1%-3% range of the converted amount (plus GST on the fee), and foreclosure/early-closure charges typically in the 2%-4% range of outstanding principal (plus GST), billed when a No Cost EMI plan is closed before its tenure ends. **[VERIFY]** Exact fee percentages and rupee amounts vary by issuer, card, and merchant tie-up, and change over time; these are not attributed to a single verified current primary source, so exact numbers are excluded from on-slide copy in favour of general, hedged ranges.

## Research notes

- The mechanism: a merchant/brand or bank funds a "discount" on the listed price that is sized to offset the interest the bank would otherwise charge over the EMI tenure. The card statement then shows 0% "interest," but the discount that would have applied to a cash purchase is typically absorbed into that offsetting instead of being available as a separate cash discount.
- RBI's core objection (2013) was not that a discount-funded EMI is illegal, but that marketing it as literally "zero percent" or "no cost" misrepresents what is happening, and that some issuers were camouflaging the interest component as a processing fee to keep the headline rate at zero.
- Two real, current costs beyond the "discount you gave up" are well documented across issuer/marketplace terms and multiple explainer sources: (a) a processing fee charged to convert a purchase into EMI (commonly quoted as roughly 1%-3% of the transaction, plus GST), and (b) a foreclosure/early-closure charge if the EMI is paid off before the full tenure (commonly quoted as roughly 2%-4% of outstanding principal, plus GST). Because exact figures are issuer-specific and change over time, the carousel uses hedged language ("often," "can," "check current terms") rather than a single fixed number, per the design mastermind's rule on fragile fee data.
- Behavioural angle (not attributed to a specific study, used only as observational commentary, not stated as a proven fact): a "0%" badge lowers the felt cost of a purchase decision at the point of sale, which is a plausible reason retailers favour it. This is framed in the carousel as an interpretive point ("what it is really selling you"), not as a cited statistic.

## Claims included in the carousel (on-slide copy)

- RBI has stated that the concept of zero percent interest is not genuinely valid / does not exist, and has described the interest component in some schemes as camouflaged as a processing fee. (Sourced to RBI notification + consistent secondary reporting; date marked [VERIFY] on exact circular date.)
- No Cost EMI discounts are typically sized to offset the interest the bank would otherwise charge, meaning the "zero" is a relabeling, not an absence of cost.
- Processing fees are commonly charged on EMI conversion, often with GST added, generally in a low single-digit percentage of the transaction. (Range only, no fixed rupee figure used on-slide.)
- Foreclosure/early-closure charges commonly apply if a No Cost EMI is paid off before the end of its tenure, generally a few percent of outstanding principal, often plus GST. (Range only, no fixed rupee figure used on-slide.)
- The practical decision rule (check for a cash-price alternative, check the processing fee and GST treatment, check the foreclosure terms before committing) is derived directly from the above and does not require separate verification; it is decision guidance, not a specific claim.

## Claims removed or excluded because they were not adequately verified for on-slide use

- Any specific rupee processing-fee figure (e.g., "₹99," "₹249," "₹299") — excluded because these are bank/card-specific, change over time, and could not be tied to one current verified source. The research notes above record the general range only.
- Any specific foreclosure-fee percentage tied to a single issuer — excluded for the same reason; a hedged range is used instead.
- The exact date and reference number of the RBI circular — flagged [VERIFY] below rather than stated as fact, since the RBI PDF itself could not be fetched in this session.
- Any claim about a specific company, bank, or fintech app's current EMI terms — excluded; the carousel deliberately avoids naming or depicting any specific lender, bank, or app to avoid making an inaccurate or dated claim about a named entity's product terms.

## All [VERIFY] items

| Item | Why it needs verification |
|---|---|
| Exact date and reference number of the RBI "zero percent interest" notification | Primary RBI document (rbidocs.rbi.org.in) could not be fetched in this session due to a network egress restriction; date is inferred from consistent secondary reporting (September 2013) but not confirmed against the primary PDF text. |
| Exact wording of RBI's operative sentence in the notification | Only summarised/quoted via secondary sources in this session, not the primary PDF directly. |
| Current processing-fee percentage/rupee range for No Cost EMI conversion | Varies by issuer and card; changes periodically; no single current authoritative source was used, only aggregated secondary explainers. |
| Current foreclosure/early-closure fee percentage for No Cost EMI | Same as above; issuer-specific and time-variable. |

## Source links and dates

- RBI notification PDF (primary, title confirmed via search index, full text not directly fetchable in this session): https://rbidocs.rbi.org.in/rdocs/notification/PDFs/31069.pdf — title indexed as "Zero percent Interest Finance Schemes for Consumer Durables." [VERIFY exact date]
- Business Standard, "RBI bans zero per cent interest rate scheme for buying goods," business-standard.com (URL pattern indicates September 25, 2013).
- Business Standard, "RBI asks banks to charge uniform interest rate on retail EMI schemes," business-standard.com (same September 2013 cluster).
- Moneylife, "RBI says no zero percent interest scheme for buying consumer goods," moneylife.in.
- Aggregated current-market context on processing fees, GST treatment, and foreclosure charges for No Cost EMI: CardCheck (cardcheck.in), BankBazaar (bankbazaar.com), CRIF High Mark (crifhighmark.com) — used only for general range context, not for any single fixed figure placed on a slide.

## Note on this session's research limitations

This session's network egress policy blocked direct retrieval of rbidocs.rbi.org.in, business-standard.com, and moneylife.in, so findings above rely on search-result snippets rather than full primary-source text. Before publishing, Kevin should personally open the RBI PDF link and at least one Business Standard link above to confirm the exact date and wording quoted on Slide 4, and adjust or remove that citation if it does not match.
