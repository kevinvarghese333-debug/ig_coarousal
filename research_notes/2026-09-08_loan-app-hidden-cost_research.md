# Research Notes: The Loan App Doesn't Want You Doing The Maths

## Topic selected

How small-ticket digital loan apps are designed to make borrowing feel fast and harmless, contrasted with what RBI's digital lending framework already requires lenders to disclose and how they must settle funds.

## Why it was selected

- Checked `carousel_topic_bank.md`, `published_log.csv`, and `research_notes/` first: this is the first-ever production run for this repository. `published_log.csv` had no prior rows and `carousel_topic_bank.md`'s Published section was empty, so no 30-day repeat-topic conflict exists.
- Ran a research pass (2026-09-08) specifically looking for a timely (last 2-3 weeks) RBI/SEBI/PIB announcement with a clean primary source, per the routine's priority order. Nothing from the last 2-3 weeks cleared the bar for "verifiable with a clear primary source" (see "Timely-topic search" below). Went to the topic bank's evergreen list instead.
- Chose topic bank item 8, "How loan apps make small loans feel harmless," because: it is a common and expensive money mistake (priority 3) and a business model with a hidden mechanism (priority 4); it has a strong, checkable regulatory backbone (RBI's digital lending framework); and it converts naturally into a save-worthy checklist and a comment-worthy personal question, which the mastermind flags as strong engagement design.

## Timely-topic search (ruled out)

A research pass for Aug 18 to Sep 8, 2026 surfaced only:
- SEBI mandatory nomination for demat/mutual fund accounts, circular dated 29 May 2026, effective 1 Sept 2026. Real and current, but an account-admin rule, not a strong narrative carousel topic on its own. Not used.
- RBI MPC decision (repo rate held, neutral stance), announced 5 Aug 2026, roughly five weeks before this run. Outside the "last 2-3 weeks" window and not distinctive enough for a one-idea carousel. Not used.
- CIBIL/credit bureau reporting frequency change (bureaus now updated multiple times a month instead of once), effective 1 July 2026. Roughly two months old, good evergreen material for a future carousel, not used here because it is outside the timely window and this run needed a topic, not a queue addition.
- No verifiable Aug-Sept 2026 announcement was found on credit card rules, UPI rules, gold loan rules, or a major Indian fintech/NBFC business-model story with hard, sourced numbers.
- Decision: none of the above cleared the bar for "timely and verifiable with a clean primary source," so this run went evergreen instead of forcing a weak timely angle.

Note on method: primary regulator sites (rbi.org.in, sebi.gov.in, pib.gov.in) were not directly fetchable from this session's network (egress restrictions). Findings above come from web search snippets and secondary reporting, with source URLs recorded for Kevin to verify directly before these specific facts are ever used in a caption or comment reply. None of the timely items above were used on-slide, so this limitation does not affect the published carousel copy.

## Primary sources consulted (for the loan-app mechanism used on-slide)

- RBI (Digital Lending) Directions, reported as RBI/2025-26/36, DOR.STR.REC.19/21.07.001/2025-26, dated 8 May 2025, which reportedly consolidates and repeals the original 2022 Guidelines on Digital Lending and the 2023 Default Loss Guarantee (FLDG) guidelines.
  - Notification page (not directly fetched this session): https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12848&Mode=0
- Original RBI Guidelines on Digital Lending, reported as RBI/2022-23/111, DOR.CRE.REC.66/21.07.001/2022-23, dated 2 September 2022.
  - Notification page (not directly fetched this session): https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12382&Mode=0
  - PDF mirror referenced in secondary reporting: https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF
- RBI Working Group on Digital Lending (WGDL) report, November 2021, cited in secondary reporting as the basis for the 2022 guidelines' concerns about pooled/pass-through accounts, non-transparent pricing, and coercive recovery by unregulated lending apps.

All three are reported as genuine RBI documents by multiple secondary sources, but were not directly fetched and read in full inside this session. Treat exact notification numbers, dates and clause-level wording as [VERIFY] until confirmed against the live RBI page.

## Research notes (mechanism, as reported by multiple secondary sources)

- Digital lenders (banks/NBFCs) and any Loan Service Provider (loan app) working with them are required to route loan disbursement and repayment directly between the borrower's bank account and the regulated entity's bank account. No pass-through or pooling account operated by the loan app itself is permitted (except in specific co-lending arrangements between two regulated entities).
- A Key Fact Statement (KFS) must be provided to the borrower before loan execution, disclosing the Annual Percentage Rate (APR), i.e. the all-in annualised cost of credit, not just a flat processing fee.
- A cooling-off / look-up period must be offered, during which the borrower can exit the loan by repaying the principal and a proportionate part of the APR, without a prepayment penalty. Reported thresholds (roughly 3 days for loans of 7 days or longer tenor, 1 day for shorter tenors) are treated as [VERIFY] and were kept off-slide.
- First Loss Default Guarantee / Default Loss Guarantee (FLDG/DLG) arrangements, where a loan app or third party guarantees a portion of a lender's losses, are reportedly capped at 5% of the guaranteed loan portfolio. Treated as [VERIFY], not used on-slide.
- Historical context (pre-2022): multiple news investigations and the RBI's own Working Group report describe some unregulated or loosely-regulated lending apps prior to the 2022 guidelines pooling borrower repayments through their own (non-bank) accounts, disclosing costs only as a flat fee rather than an annualised rate, and using aggressive or coercive recovery tactics (including contact-list access and harassment). This is used on-slide (Slide 6) only in general terms ("some apps"), with no specific company named.

## Claims included in the carousel

- Loan apps commonly present cost as a flat rupee fee rather than an annualised rate, and disbursement is designed to feel instant (Slides 2, 4). General mechanism claim, not tied to one company.
- An illustrative worked example: Rs 5,000 loan, 15-day tenor, Rs 150 (3%) processing fee, annualised to roughly 73% APR using simple annualisation (3% x 365/15 ~ 73%) (Slide 5). This is arithmetic performed for teaching purposes on invented, round numbers, not a real product's actual fee schedule. Labelled "For illustration only" on-slide.
- Before 2022, some apps pooled repayments through their own accounts and used aggressive recovery, which is why RBI's rules exist (Slide 6). General historical claim, sourced to the RBI Working Group report and multiple news investigations, no specific company named.
- RBI's digital lending rules require the full APR shown upfront, a short cooling-off window, and bank-to-bank settlement rather than settlement through the app (Slide 7). Mechanism-level claim, exact clause wording marked [VERIFY].
- A 3-point practical checklist: check the APR not the flat fee, check the actual regulated lender's name not just the app's brand, check for a cooling-off period (Slide 8). This is a decision framework built from the disclosures above, not a claim of fact requiring its own citation.

## Claims removed or kept generic because they were not adequately verified

- Removed: any specific FLDG/DLG percentage cap (5%) from on-slide copy. Mentioned only in this research file as [VERIFY].
- Removed: exact cooling-off period day-counts (e.g. "3 days"). Slide 7 uses the generic phrase "a short cooling-off window" instead.
- Removed: any named loan app, bank, NBFC or fintech company. The notification on Slide 2 says "Loan App" generically.
- Removed: exact RBI notification numbers and dates from on-slide copy (kept only in this research file, marked [VERIFY]).
- Not used: the SEBI nomination rule and CIBIL reporting-frequency change surfaced during the timely-topic search; both are accurate as reported but were set aside as separate potential future topics rather than forced into this carousel.

## All [VERIFY] items

1. Exact RBI notification number and date for the current Digital Lending Directions (reported as RBI/2025-26/36, 8 May 2025).
2. Exact RBI notification number and date for the original 2022 Guidelines on Digital Lending (reported as RBI/2022-23/111, 2 September 2022).
3. FLDG/DLG cap at 5% of the guaranteed portfolio, and whether this cap carries forward unchanged under the 2025 Directions.
4. Exact cooling-off/look-up period thresholds (reported as ~3 days for tenor >= 7 days, ~1 day for shorter tenors).
5. Precise scope of the "no pass-through account" rule and its co-lending exception.

## Source links and dates

- RBI 2025 Digital Lending Directions notification page: https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12848&Mode=0 (reported date: 8 May 2025) [VERIFY, not directly fetched]
- RBI 2022 Guidelines on Digital Lending notification page: https://www.rbi.org.in/Scripts/NotificationUser.aspx?Id=12382&Mode=0 (reported date: 2 September 2022) [VERIFY, not directly fetched]
- RBI 2022 Guidelines PDF mirror: https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF [VERIFY, not directly fetched]
- RBI Working Group on Digital Lending report: search "Report of the Working Group on digital lending including lending through online platforms and mobile apps" on rbi.org.in (reported date: November 2021) [VERIFY, not directly fetched]
- SEBI demat/MF nomination circular (not used on-slide, logged for future reference): https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=1&ssid=7&smid=0 (circular reported dated 29 May 2026, effective 1 Sept 2026) [VERIFY]
