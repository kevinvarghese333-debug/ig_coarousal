# Sources and Fact Check: The Minimum Due Trap

## Core claim used on-slide

Paying only the credit card's Minimum Amount Due, even on time, causes the card issuer to treat the bill as not paid in full. This revokes the interest-free (grace) period: interest is then charged from the date of each transaction, including new purchases made in that billing cycle, not from the payment due date.

**Verification status:** Verified at the mechanism level against the RBI Master Direction on Credit Card and Debit Card issuance, cross-checked with three independent secondary explainers. Direct automated fetch of the RBI PDF/FAQ returned an HTTP 403 in this session, so exact clause wording is reconstructed from search-engine snippets rather than a verbatim read. Kevin should open the source link directly before publishing to confirm wording.

- RBI Master Direction (Credit Card and Debit Card – Issuance and Conduct) Directions, 2022: https://rbidocs.rbi.org.in/rdocs/notification/PDFs/92MDCREDITDEBITCARDC423AFFB5E7945149C95CDD2F71E9158.PDF (effective 1 July 2022; referenced 2026-08-02)
- RBI FAQ on the Master Direction: https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf (referenced 2026-08-02)
- Moneyview, "RBI Guidelines on Credit Card Late Payment Charges": https://moneyview.in/credit-card/rbi-guidelines-on-credit-card-late-payment-charges (referenced 2026-08-02)
- Finowings, "RBI Credit Card Rules 2026: 3-Day Rule, Fees & CIBIL": https://www.finowings.com/Credit-Cards/rbi-credit-card-rules (referenced 2026-08-02)
- Arthzo, "RBI New Credit Card Rules 2026: 10 Important Changes": https://arthzo.com/rbi-new-credit-card-rules-2026/ (referenced 2026-08-02)

## Secondary claim used on-slide

The Minimum Amount Due is structured to cover interest, fees and taxes for the period plus a small part of the principal, so it keeps the account "current" without materially reducing the debt.

**Verification status:** Confirmed at a mechanism level across the sources above. The exact percentage split is issuer-specific and is not published by RBI as a single universal figure, so no percentage is stated on-slide (Slide 7's stacked bar is illustrative and unlabelled with numbers for this reason).

## Claims deliberately excluded from this carousel

- Any specific credit card APR/interest rate figure. Rates vary by issuer, card variant, and change over time; RBI does not publish one universal rate. Slide 8 instead tells the reader to check their own card's terms.
- A reported "3-day grace period" before late-payment penal charges apply. Search results gave conflicting effective dates (2025-26 vs an April 2027 rollout mentioned in one source), so this could not be confidently dated in this session. It is also not central to the carousel's point, since every source agrees this grace period does not extend the interest-free period.
- Any rupee example tied to a specific real bank, card product or real customer. The ₹40,000 / ₹2,000 example on Slide 6 is explicitly labelled "Illustrative example" for this reason.

## [VERIFY] items

1. Exact wording of the RBI FAQ clause on loss of interest-free period — confirm by opening the RBI link directly; this session's automated fetch was blocked (403).
2. Status and effective date of the "3-day grace period" on late payment charges — not used in this carousel, flagged for a possible future one once the timeline is confirmed.
3. Any current interest-rate figure, if Kevin wants to add one in a caption reply or comment — verify against at least two to three major issuers' current Most Important Terms and Conditions (MITC) documents first.

## Design/production notes relevant to accuracy

- No real bank app screenshots, statements, or logos were used. All visual elements (phone frame, receipt cards, timeline, comparison card, stacked bar, checklist) are generic, code-drawn shapes built with Pillow, not copies of any real product interface.
- Fonts requested (Playfair Display, DM Sans) were not present in `fonts/` for this run. DejaVu Serif and DejaVu Sans were used as fallbacks. This does not affect factual accuracy but is noted for the design record.
