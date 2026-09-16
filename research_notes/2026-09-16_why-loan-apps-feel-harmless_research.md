# Research Notes: Why Loan Apps Feel Harmless

## Topic Selected

How loan apps make small loans feel harmless — the product is the speed
and the removal of friction, not the credit itself, and RBI has had to
legislate friction back in (cooling-off period, Key Fact Statement,
centralised app directory) to protect borrowers.

## Why This Topic Was Selected

Selection priority used (per routine instructions): matched priority 1
(timely and verifiable regulatory development — RBI's Digital Lending
Directions, 2025 consolidated and updated the rules this year) and
priority 4 (a business model with a hidden mechanism). It draws directly
on the creator's NBFC/lending background, has not been covered in any
prior draft (published_log.csv and carousel_topic_bank.md are both
empty/unused as of this run), and sits squarely in the "fintech, loan
apps and financial traps" pillar. It is also topic #8 in
carousel_topic_bank.md ("How loan apps make small loans feel harmless").

## Primary Sources Consulted

Note on access: this environment's network egress proxy blocked direct
fetches of rbi.org.in / rbidocs.rbi.org.in and several secondary domains
(medianama.com, argus-p.com, kinaracapital.com) during this run. Facts
below were sourced through web search summaries citing RBI's own
circulars, cross-checked across multiple independent legal/fintech
sources reporting the same primary documents. Kevin should verify
clause-level wording against the original RBI PDF before publishing if
he wants exact section numbers.

1. **RBI "Guidelines on Digital Lending"** — issued 2 September 2022.
   Referenced via: RBI circular (rbidocs.rbi.org.in, not directly
   fetchable this run), summarised consistently by Kinara Capital,
   Medianama, AMLegals, Kissht.
   - Lenders must give a **Key Fact Statement (KFS)** to the borrower
     before the loan agreement is signed, in a standard format, before
     loan approval/disbursal.
   - Loan disbursal must go **directly to the borrower's bank account**
     (not routed through a third-party pool account of a lending
     service provider/app).
   - Regulated entities may store only the **minimum necessary borrower
     data**; biometric data may not be stored by the digital lending app.
   - No charges or penalties may be levied that were not disclosed in
     the KFS.
   - Coverage: all commercial banks, urban/state/district co-operative
     banks, and NBFCs (including HFCs).

2. **RBI FAQs clarifying the Digital Lending Guidelines** — February
   2023, and subsequent legal commentary (Vinod Kothari Consultants FAQ
   summary; corroborated by Tata Capital, Finnable, Helpa explainer
   pages).
   - **Cooling-off / look-up period**: not less than **3 days** for
     loans with tenor of 7 days or more, and not less than **1 day**
     for loans with tenor under 7 days. Each lender's board can set a
     longer period.
   - During this window, the borrower has an **explicit right to exit**
     the loan by repaying the principal plus the **proportionate APR**
     for the days elapsed, **with no exit penalty** (RBI has clarified a
     reasonable one-time processing fee may still be retained).
   - After the cooling-off period, ordinary prepayment rules apply.

3. **RBI (Digital Lending) Directions, 2025** — effective 8 May 2025;
   consolidates the 2022 guidelines and 2023 Default Loss Guarantee
   guidance into one framework. Referenced via Lexology, Precisa.in,
   Legal500, Lawrbit, Medianama summaries.
   - RBI operationalised a **public directory of Digital Lending Apps
     (DLAs)** on its website, live from **1 July 2025**, so a borrower
     can check whether an app is genuinely tied to an RBI-regulated
     lender.
   - Regulated entities were required to report all their DLAs (owned
     or via lending service providers) on RBI's CIMS portal by
     **15 June 2025**.
   - Multi-lender arrangement provisions take effect **1 November 2025**.

## Claims Included in the Carousel

- The Key Fact Statement (KFS) requirement and that it must show the
  APR, not just the EMI. [Slide 8]
- The cooling-off/look-up period: minimum 1 day (loans under 7-day
  tenor) or minimum 3 days (loans 7 days or longer), with the right to
  exit by paying principal + proportionate APR, no penalty. [Slide 7, 8]
- Disbursal must go directly to the borrower's bank account (used to
  frame the mechanism slide — this RBI safeguard is often experienced
  by the borrower simply as "speed"). [Slide 4]
- The existence of RBI's public DLA directory as a way to check an app
  is genuinely tied to a regulated lender. [Slide 7]
- General, non-app-specific description of the common "small first
  loan, fast repayment, automatically raised limit" product loop used
  across much of the short-tenor lending-app industry. This is a
  widely reported industry pattern, not a claim about any named company
  or a specific statistic. [Slide 5, 6]

## Claims Removed Because They Were Not Adequately Verified

- Any specific market-size, growth-rate, default-rate, or user-count
  statistic for the digital lending / loan-app industry in India.
  Multiple secondary sources cite different, sometimes conflicting
  numbers, and the primary RBI/industry-body source could not be
  fetched directly in this run. Removed rather than risk an inaccurate
  figure on-slide.
- Any claim naming a specific loan app or NBFC by name in a negative
  light. The mechanism described is industry-general; naming a specific
  company would need direct verification against that company's own
  disclosures, which is out of scope for an evergreen explainer.
- A specific rupee figure for "average first loan size" — no verified
  primary source found this run.

## [VERIFY] Items (flag before publishing)

- [VERIFY] Exact clause/paragraph numbers in the original RBI circular
  for the KFS and cooling-off requirements (could not fetch the RBI PDF
  directly this run; content corroborated across 4+ independent
  secondary sources, but Kevin should confirm exact section references
  from rbi.org.in before citing them verbatim in a reply to comments).
- [VERIFY] Whether the cooling-off period as stated in the RBI (Digital
  Lending) Directions, 2025 is unchanged from the 2023 FAQ clarification
  (secondary sources treat it as carried forward, but this should be
  confirmed against the 2025 Directions text directly).

## Source Links and Dates

- RBI Guidelines on Digital Lending PDF: https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF — dated 2 September 2022 (not directly fetchable this run; accessed via secondary summaries).
- Kinara Capital summary of RBI digital lending guidelines: https://kinaracapital.com/rbi-protects-borrowers-in-the-latest-guidelines-on-digital-lending/ (accessed via search summary, 2026-09-16).
- Medianama summary of RBI FAQs on Digital Lending Guidelines: https://www.medianama.com/2023/02/223-rbi-faqs-digital-lending-guidelines/ (accessed via search summary, 2026-09-16; original dated February 2023).
- Vinod Kothari Consultants, FAQs on Digital Lending Regulations: https://vinodkothari.com/2022/08/faqs-on-digital-lending-regulations/ (accessed via search summary, 2026-09-16).
- Medianama, "RBI Asks Digital Loan Apps To Register With Centralised Directory": https://www.medianama.com/2025/05/223-rbi-digital-lending-apps-centralised-directory/ (accessed via search summary, 2026-09-16; reports directory live from 1 July 2025).
- Lexology, "Rewriting the Rules of Digital Lending: RBI Digital Lending Directions, 2025": https://www.lexology.com/library/detail.aspx?g=b5bc9efb-1199-41ee-bc2d-4a149573793b (accessed via search summary, 2026-09-16).
- Lawrbit, "RBI Digital Lending Guidelines 2025: Key Rules & CIMS Portal": https://www.lawrbit.com/article/reserve-bank-of-india-digital-lending-directions-2025/ (accessed via search summary, 2026-09-16).
