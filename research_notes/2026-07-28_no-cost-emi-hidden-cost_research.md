# Research Notes: No Cost EMI Is Not the Same as Free

## Topic Selected

Why "No Cost EMI" at online checkout is not actually free, and where the cost really goes (forfeited cash discount, plus GST on the interest/fee the bank charges the merchant).

## Why It Was Selected

- Matches priority topic #1 in `carousel_topic_bank.md` ("Why zero-cost EMI is not always a free decision"), a topic with strong verifiable regulatory grounding and daily relevance to the 21-40 salaried audience.
- Nothing has been published yet (`published_log.csv` is empty), so no 30-day repeat conflict exists.
- High save/share potential: gives readers a reusable 3-point checklist for a decision (EMI vs full payment) they make repeatedly, at checkout, across many platforms.
- Fits the "Trap or Warning" carousel type structure from the design mastermind: appealing surface → missing question → risk → safer way to think.

## Primary Sources Consulted

1. **RBI Master Directions on Credit Card and Debit Card – Issuance and Conduct Directions, 2022** (RBI/2022-23/92, DoR.AUT.REC.No.27/24.01.041/2022-23), issued 21 April 2022, effective 1 July 2022.
   - URL: https://rbidocs.rbi.org.in/rdocs/notification/PDFs/92MDCREDITDEBITCARDC423AFFB5E7945149C95CDD2F71E9158.PDF
   - Direct automated fetch of the PDF returned an HTTP 403 (blocked to the fetch tool used this run). Content below is reconstructed from secondary legal/industry summaries that quote the directive, not from a first-hand read of the PDF text in this session.
   - Reported requirement: card issuers must ensure "complete transparency" when converting a credit card transaction to EMI, clearly indicating the principal, interest, and any upfront discount from the merchant/issuer that makes the EMI "no cost," both before the conversion is confirmed and separately on the credit card statement.
   - Reported requirement: EMI conversions that carry an interest component must not be "camouflaged" as zero-interest or no-cost EMI.
   - [VERIFY] Exact paragraph/clause number within the Master Direction. Not confirmed from primary text this run due to the fetch block.

2. Secondary legal/industry summaries corroborating the above (used only to triangulate the RBI requirement, not as primary sources for on-slide claims):
   - Mondaq, "Master Directions On Credit Card And Debit Card – Issuance And Conduct Directions, 2022" — https://www.mondaq.com/india/financial-services/1214312/master-directions-on-credit-card-and-debit-card-issuance-and-conduct-directions-2022
   - LiveLaw, same title — https://www.livelaw.in/law-firms/law-firm-articles-/issuance-and-conduct-directions-2022-rbi-urban-cooperative-banks-pradhan-mantri-jan-dhan-yojana-non-banking-financial-companies-204696

3. Consumer finance explainer content on the GST/processing-fee mechanics of no-cost EMI (used for background understanding of the mechanism only; NOT used as the source for any specific number placed on-slide):
   - myPaisaa, "What is No Cost EMI? The 18% GST Trap & Hidden Math" — https://blog.mypaisaa.com/what-is-no-cost-emi/
   - CardCheck, "No-cost EMI on credit cards in India (2026 explained)" — https://cardcheck.in/blogs/no-cost-emi-credit-card-india-explained-2026
   - These are not primary regulatory or company sources. They corroborate the general mechanism (GST applies to the interest the bank charges the merchant, and issuers may recover some of that via a processing fee) but their specific worked-example numbers were not used on-slide.

## Research Notes

- The core mechanism is a merchant subvention model: when a purchase is converted to "no cost EMI," the bank still charges interest, but the merchant (not the customer) pays it, usually recovering that cost by removing a cash discount otherwise available to full-payment buyers, or by adjusting price.
- GST (financial services generally sit in the 18% slab under CGST/SGST) applies to the interest the bank charges the merchant on the EMI conversion. Whether and how this GST cost is passed on to the cardholder, e.g. bundled into a "processing fee," varies by issuer and by product. This is not universal, so on-slide language uses hedged wording ("can," "often") rather than a blanket claim.
- The RBI disclosure requirement means the "hidden" cost is not technically hidden. The break-up screen showing principal, interest and discount exists precisely so a customer can see what "no cost" is built from. Most customers do not read it. This became Slide 7's insight beat.
- A 2013 RBI notification restricting "zero percent interest" retail finance schemes on non-card lending exists as older, adjacent regulatory history, but it addresses a different product structure (retail EMI schemes outside the 2022 card directions) and was not used in this carousel's claims to avoid conflating two separate rules.

## Claims Included in the Carousel

1. Banks do not lend for free; when a customer pays no interest, someone else (the merchant) is covering it. — General mechanism, supported by the subvention model described in multiple industry sources.
2. RBI requires card issuers to show principal, interest and discount before an EMI conversion is confirmed, and bars presenting interest-bearing EMI as zero-interest/no-cost. — Sourced to the 2022 RBI Master Directions (see [VERIFY] on exact clause number above).
3. GST can apply to the interest component, and this cost can land on the cardholder as part of a processing fee. — Hedged language used ("can," "often") because pass-through practice varies by issuer; treated as a general mechanism, not a universal claim.
4. Illustrative example: a ₹50,000 phone with a ₹2,000 cash discount for full payment, where the discount is typically forfeited on a no-cost EMI conversion. — Explicitly framed on-slide as a hypothetical ("Say a...") to explain the mechanism, not presented as a real, sourced statistic.

## Claims Removed Because They Were Not Adequately Verified

- A specific rupee figure for the GST/processing-fee cost cited in a consumer blog (approximately ₹756 GST and roughly 8.7% effective annual cost on a ₹50,000/12-month example) was NOT used on-slide. The source is a blog aggregator, not a primary source, and the underlying assumptions (bank interest rate, specific processing fee amount) were not independently verifiable this run.
- A specific list of which banks (SBI, HDFC, ICICI, Axis, Kotak, IDFC First) charge EMI-conversion processing fees, and at what amount, was NOT used. Fee amounts and applicability change by issuer and card product and were not verified against each bank's current, dated fee schedule this run.
- The exact RBI Master Direction paragraph/clause number for the EMI disclosure requirement was NOT stated as a specific number on-slide, since it could not be confirmed from the primary PDF this run (blocked fetch). Slide 7 cites the source generically ("RBI, Master Directions on Credit Card and Debit Card, 2022") without a fabricated clause number.

## All [VERIFY] Items

- [VERIFY] Exact paragraph/clause number in the RBI 2022 Master Directions for the EMI principal/interest/discount disclosure requirement.
- [VERIFY] Current GST treatment and pass-through practice for EMI-conversion processing fees, confirmed against a primary CBIC notification and/or current issuer T&Cs, before publishing Slide 6 language as-is.

## Source Links and Dates

| Source | Link | Date accessed / issued |
|---|---|---|
| RBI Master Directions on Credit Card and Debit Card – Issuance and Conduct Directions, 2022 | https://rbidocs.rbi.org.in/rdocs/notification/PDFs/92MDCREDITDEBITCARDC423AFFB5E7945149C95CDD2F71E9158.PDF | Issued 21 Apr 2022, effective 1 Jul 2022; automated fetch attempted 28 Jul 2026, returned HTTP 403 |
| Mondaq summary of the 2022 Master Directions | https://www.mondaq.com/india/financial-services/1214312/master-directions-on-credit-card-and-debit-card-issuance-and-conduct-directions-2022 | Accessed 28 Jul 2026 |
| LiveLaw summary of the 2022 Master Directions | https://www.livelaw.in/law-firms/law-firm-articles-/issuance-and-conduct-directions-2022-rbi-urban-cooperative-banks-pradhan-mantri-jan-dhan-yojana-non-banking-financial-companies-204696 | Accessed 28 Jul 2026 |
| myPaisaa, "What is No Cost EMI? The 18% GST Trap & Hidden Math" (background only, not cited on-slide) | https://blog.mypaisaa.com/what-is-no-cost-emi/ | Accessed 28 Jul 2026 |
| CardCheck, "No-cost EMI on credit cards in India (2026 explained)" (background only, not cited on-slide) | https://cardcheck.in/blogs/no-cost-emi-credit-card-india-explained-2026 | Accessed 28 Jul 2026 |
