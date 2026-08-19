# Research Notes: Loan-App Friction Design Carousel

## Topic selected

How instant loan apps engineer borrowing to feel small and harmless, and why that engineered ease is the mechanism behind repeat borrowing. Sourced from `carousel_topic_bank.md` priority item 8: "How loan apps make small loans feel harmless."

## Why it was selected

- This is the first production run for this repository. `published_log.csv` had no prior entries and `carousel_topic_bank.md` marked all ten priority topics as unused, so no 30-day repeat conflict exists.
- The topic sits in the "Trap or Warning" carousel type: appealing surface, missing question, risk, safer way to think.
- It has strong verifiable regulatory backing (RBI Guidelines on Digital Lending, RBI Working Group Report) rather than resting on vague behavioural claims.
- It is timely and relevant to the audience (21 to 40, salaried, first-time borrowers who interact with instant credit apps).
- Strong save potential (a practical pre-acceptance checklist) and strong comment potential (a common, often quietly embarrassing habit).

## Primary sources consulted

1. RBI, "Guidelines on Digital Lending," effective 2 September 2022.
   https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF
2. RBI, "Report of the Working Group on Digital Lending including Lending through Online Platforms and Mobile Apps," 18 November 2021.
   https://rbidocs.rbi.org.in/rdocs/PublicationReport/Pdfs/DIGITALLENDINGF6A90CA76A9B4B3E84AA0EBD24B307F1.PDF
3. PIB press release on RBI's Digital Lending Apps (DLA) public directory.
   https://www.pib.gov.in/PressReleasePage.aspx?PRID=2241255&reg=3&lang=2
4. Secondary reporting used to summarise the above primary sources (not used as the sole basis for any on-slide numeric claim): SCC Online blog on the RBI Working Group release (22 Nov 2021); Zee News report citing the RBI panel's count of illegal loan apps; Business Standard coverage of RBI's implementation timeline (10 Aug 2022, 30 Mar 2023); Medianama coverage of the DLA centralised directory (2025).
5. CRIF High Mark / Digital Lenders Association of India, "How India Lends" report, and TransUnion CIBIL commentary on small-ticket personal loans — consulted for context on small-ticket loan growth but excluded from on-slide copy (see "Claims removed" below).

## Research notes

- RBI's Digital Lending Guidelines took effect from the date of the circular (2 September 2022), with compliance for existing loans required by 30 November 2022.
- The guidelines require:
  - A mandatory Key Fact Statement (KFS) before loan execution, in a standardised format, showing the Annual Percentage Rate (APR), recovery mechanism, and grievance redressal officer details.
  - A cooling-off / look-up period during which a borrower can exit the loan by paying the principal plus proportionate APR, with no penalty. Reported minimums: not less than 3 days for loan tenor of 7 days or more, and 1 day for tenor under 7 days.
  - Disbursements and repayments routed only through bank accounts of the borrower and the regulated entity, not through pooled third-party accounts.
  - No unilateral increase in credit limit without explicit borrower consent.
- RBI's November 2021 Working Group Report found, per its review window (roughly January to February 2021), approximately 1,100 mobile lending apps available to Indian Android users across 80-plus app stores. Secondary reporting on the same report states that a panel identified more than 600 of these as illegal/unauthorised. These figures come from the RBI's own working group and are corroborated across multiple secondary outlets, but were not independently re-verified against the primary PDF's exact page/table in this research pass, so they are flagged [VERIFY] below.
- RBI operationalised a public "Digital Lending Apps (DLA)" directory on its website, reported as effective 1 July 2025, listing DLAs deployed by RBI-regulated entities (banks, small finance banks, NBFCs) or their authorised Lending Service Providers, so borrowers can check whether an app is tied to a regulated lender. Apps not traceable to a regulated entity on this directory are treated as unauthorised.
- Under Section 69A of the IT Act, 2000, MeitY can direct blocking of unauthorised loan apps once identified, following due process under the 2009 blocking rules.
- Industry data (CRIF High Mark / DLAI, TransUnion CIBIL) suggests substantial recent growth in small-ticket personal loans (commonly defined as loans under ₹50,000 to ₹1 lakh) since 2022, including rising origination share and, per TransUnion CIBIL commentary, rising delinquency in this segment. Specific percentage figures varied between sources and were not fully reconciled against a single primary dataset, so no precise growth percentage was used on-slide.

## Claims included in the carousel

- RBI's Digital Lending Guidelines exist and require a Key Fact Statement plus cooling-off period. Used in research/design-handoff context; not directly quoted with specific day-counts on-slide to avoid over-claiming precision, but referenced generally on Slide 8 ("Read the Key Fact Statement for the real APR").
- The 2021 RBI Working Group figures (~1,100 apps reviewed, ~600 flagged unauthorised) are used on Slide 5 and in the caption, with a small source note on-slide and full citation in this file. Flagged [VERIFY] for Kevin to confirm against the primary PDF before publishing (see table below and the draft's "Facts to Verify" table).
- The existence of RBI's public DLA directory is used on Slide 8 as a practical, actionable check ("Confirm the app appears on RBI's Digital Lending Apps directory"), without citing a specific effective date on-slide, since that date is a secondary detail not essential to the instruction.

## Claims removed because they were not adequately verified

- Specific percentage growth figures for small-ticket personal loans (for example, "25 percent of loan originations" or "50 percent of the personal loan market") were considered for Slide 5 or 6 but removed from on-slide copy. Different sources (CRIF-DLAI, TransUnion CIBIL) reported different denominators and time windows, and none was confirmed against a primary RBI dataset. Keeping the carousel's evidentiary weight on the RBI's own working group figures, which are more clearly primary-sourced, was judged safer than blending in unreconciled industry percentages.
- No claim about current effective interest rates (APR) charged by specific apps was included, since these vary by lender and are exactly the kind of fragile, product-specific number the production rules ask to avoid ("check the current terms" applies here rather than a fixed figure).
- No claim naming any specific loan app, company, or brand was included. The carousel discusses the category and the regulatory response to it, not individual companies, to avoid unverified reputational claims.

## All [VERIFY] items

1. [VERIFY] The exact figures "~1,100 apps reviewed" and "~600 flagged as unauthorised" from the RBI Working Group Report (18 Nov 2021), used on Slide 5 and in the caption. Confirm against the primary PDF: https://rbidocs.rbi.org.in/rdocs/PublicationReport/Pdfs/DIGITALLENDINGF6A90CA76A9B4B3E84AA0EBD24B307F1.PDF (source date: 2021-11-18).
2. [VERIFY] The cooling-off period detail (3 days for 7+ day tenor, 1 day for shorter tenor) referenced generally in the design handoff and Slide 8 instruction. Confirm against the primary circular, noting RBI issued further digital lending clarifications and a 2025 Digital Lending Directions update since the original 2022 guidelines. Source: https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF (source date: 2022-09-02).
3. [VERIFY] The current effective date and URL for RBI's public Digital Lending Apps (DLA) directory referenced conceptually on Slide 8. Source: https://www.pib.gov.in/PressReleasePage.aspx?PRID=2241255&reg=3&lang=2 (source date: 2025, exact day not confirmed in this pass).

## Source links and dates

| Source | URL | Date |
|---|---|---|
| RBI, Guidelines on Digital Lending | https://rbidocs.rbi.org.in/rdocs/notification/PDFs/GUIDELINESDIGITALLENDINGD5C35A71D8124A0E92AEB940A7D25BB3.PDF | 2022-09-02 |
| RBI, Report of the Working Group on Digital Lending | https://rbidocs.rbi.org.in/rdocs/PublicationReport/Pdfs/DIGITALLENDINGF6A90CA76A9B4B3E84AA0EBD24B307F1.PDF | 2021-11-18 |
| PIB press release, RBI Digital Lending Apps directory | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2241255&reg=3&lang=2 | 2025 |
| SCC Online summary of RBI Working Group report | https://www.scconline.com/blog/post/2021/11/22/rbi-releases-report-of-working-group-on-digital-lending-including-lending-through-online-platforms-and-mobile-apps/ | 2021-11-22 |
| Zee News, RBI panel finds 600 illegal loan apps | https://zeenews.india.com/economy/digital-lending-fraud-rbi-panel-finds-600-illegal-loan-apps-on-app-stores-2411928.html | undated (2021/2022 reporting window) |
| Business Standard, RBI implementation timeline for digital lending norms | https://www.business-standard.com/amp/article/finance/rbi-to-implement-some-recommendations-of-working-group-on-digital-lending-122081000784_1.html | 2022-08-10 |
| CRIF High Mark / DLAI, "How India Lends" (small-ticket loan context, not used on-slide) | https://www.business-standard.com/amp/industry/banking/personal-loans-see-a-resurgence-post-covid-says-cfri-dlai-report-124011901028_1.html | 2024-01-19 |
