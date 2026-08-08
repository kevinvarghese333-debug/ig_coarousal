# Research Notes: The Minimum Due Trap

## Topic selected

Why paying only the credit card "minimum amount due" every month, on time, without ever missing a payment, still leads to a growing debt problem, even though the credit score stays fine.

## Why it was selected

- Fits priority tier 2 (a common audience confusion) and tier 3 (a common, expensive money mistake).
- Not present in `carousel_topic_bank.md` published history (log is empty, no 30-day conflict).
- High save/share potential: this is a decision framework ("always pay in full") plus a myth correction (score stays fine, but debt does not).
- Directly usable by the 21-40 salaried/credit-card audience described in the brand brief.
- Central idea passes the one-sentence test: "Paying the minimum due keeps your credit score safe. It does not keep your money safe."

## Primary sources consulted

1. **RBI Master Direction – Credit Card and Debit Card – Issuance and Conduct Directions, 2022** (and associated RBI FAQ document), referenced via RBI notification pages:
   - https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300
   - https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf
   - Note: Direct fetch of rbi.org.in was blocked by the research environment's network egress policy during this run. Content below is drawn from the RBI FAQ document's well-documented required cardholder warning language, corroborated by multiple independent secondary finance-industry sources (moneyview.in, finowings.com, sharmadebtsolutions.in, billcut.com) that quote or summarise the same FAQ. Treated as [VERIFY] pending a direct primary-source read before publishing.
   - Search date: 2026-08-08.

2. **Bank-published interest rate pages** (secondary aggregation, since direct fetch of bank domains was also blocked by network policy):
   - ICICI Bank credit card interest rate range (via bajajfinservmarkets.in summary of ICICI's published rate card): 3.40%–3.75% per month (~41%–45% annually) on revolving balances.
   - HDFC Bank credit card interest rate (via search summary): up to ~3.4% per month.
   - General market range across major Indian issuers commonly cited: 2.5%–3.75% per month, i.e., roughly 30%–45% annualised, charged on the unpaid revolving balance from the transaction date once the bill is not paid in full.
   - Search date: 2026-08-08.

3. **Credit bureau / score impact** (secondary sources: bajajhousingfinance.in, moneyview.in, bankbazaar.com):
   - Paying at least the minimum due, on time, is reported to the bureau as "paid," not delinquent, so it does not by itself trigger the score damage a missed payment would.
   - Credit utilisation (balance carried relative to the limit) is a separate score factor. Commonly cited guidance: keeping utilisation under roughly 30% of the limit supports a healthier score. Carrying a large revolving balance month to month, which is what happens when only the minimum is paid, tends to keep utilisation high.
   - Search date: 2026-08-08.

## Research notes (mechanism)

1. Minimum Amount Due (MAD) is typically calculated as roughly 5% of the statement outstanding, plus any EMI instalments, past dues and over-limit amount, plus 100% of interest/fees/taxes for the cycle. Paying only this amount avoids late fees and delinquency reporting.
2. Under RBI's card-issuance rules, if the cardholder does not pay the **total** amount due by the due date, the interest-free (grace) period is lost for that cycle. Interest is then charged from the **original transaction date**, not just on the balance left after the minimum payment.
3. Because interest is charged from the transaction date on the full outstanding, and new purchases in the following cycle typically get no interest-free period either (while a balance is carried), the compounding effect keeps stacking on itself. RBI's own required cardholder warning (used across issuer T&Cs) states, in substance: making only the minimum payment every month results in repayment stretching over months or years with consequential compounded interest.
4. RBI's 2022 conduct directions also require that there be no "negative amortisation" and that unpaid charges/levies/taxes are not further capitalised for compounding — a consumer-protection guardrail, but one that does not change the basic economics above: at 30-45% annualised interest, a revolving balance grows fast even under that guardrail.
5. Score mechanics: minimum-due payment ≠ default, so it will not by itself crash a score. But (a) high utilisation from a growing carried balance is itself a scoring factor, and (b) the cardholder's real cost is the accumulating interest, not the credit score. This distinction, "the number that looks fine (score) vs. the number that is not fine (owed amount)," is the carousel's central engine.

## Claims included in the carousel (on-slide)

- Paying only the minimum due, on time, does not by itself damage your credit score. [supported by bureau-impact sources above]
- If you do not clear the full bill, the interest-free period is lost and interest is charged on the outstanding balance from the transaction date. [supported by RBI-derived FAQ language, corroborated by multiple secondary sources]
- Credit card interest in India commonly runs at roughly 30% to 45% a year on carried balances (framed as "3% and up, every month" on slide, not naming a single bank). [supported by multiple bank rate summaries; presented as a range, not a specific bank's exact current rate, per accuracy rules on fragile numbers]
- Minimum due is commonly around 5% of the outstanding, and mainly covers that cycle's interest and fees rather than shrinking the principal much. [supported by MAD formula sources]
- Carrying a balance keeps utilisation high, which is a separate score factor from on-time payment. [supported by bureau-impact sources]

## Claims removed or softened because they could not be adequately verified

- Removed: any specific bank's exact current interest rate (e.g., "ICICI charges 3.75% per month") — rates vary by bank, card variant and change over time; using one bank's number risked being stale or unrepresentative. Replaced with an industry range framed as "3% and up, every month."
- Removed: any specific rupee example tied to a real bank's real fee schedule. Replaced with a rounded, clearly illustrative arithmetic example (₹50,000 balance, ~40% annualised) labelled as an illustration, not a live product quote.
- Removed: any claim about a fixed number of days for the interest-free period (commonly cited as "20 to 50 days" but varies by issuer and billing cycle) — softened to "the interest-free period" without a specific day count.
- Softened: RBI's exact grace-period language is described in substance (loss of interest-free period, interest from transaction date) rather than quoted as verbatim regulatory text, since the primary PDF could not be directly re-read in this session.

## [VERIFY] items — confirm before publishing

- [VERIFY] Re-confirm current RBI Master Direction language on loss of interest-free period directly from rbi.org.in (blocked in this research session by network policy) before treating the mechanism slide as regulator-quoted rather than regulator-derived.
- [VERIFY] Confirm current representative interest rate range (30%-45% annually) against at least one live bank rate card at time of publishing, since rates can change.
- [VERIFY] Confirm current Minimum Amount Due formula description (5% of outstanding + fees/interest + EMIs + past dues) against a current issuer's cardholder agreement, since exact formulas vary by bank.

## Source links and dates

| Source | URL | Date accessed |
|---|---|---|
| RBI Master Direction listing (Credit Card and Debit Card) | https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300 | 2026-08-08 (search-indexed; direct fetch blocked) |
| RBI FAQ PDF on Credit Card and Debit Card Directions | https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf | 2026-08-08 (search-indexed; direct fetch blocked) |
| Moneyview: RBI guidelines on credit card late payment charges | https://moneyview.in/credit-card/rbi-guidelines-on-credit-card-late-payment-charges | 2026-08-08 |
| Sharma Debt Solutions: Minimum Due in Credit Card explained | https://sharmadebtsolutions.in/minimum-due-in-credit-card-india/ | 2026-08-08 |
| Billcut: Stuck in the Minimum Due Loop | https://www.billcut.com/blogs/read/minimum-due-credit-card-trap/ | 2026-08-08 |
| Bajaj Finserv Markets: ICICI credit card interest rates | https://www.bajajfinservmarkets.in/credit-card/icici-bank-credit-card-interest-rate | 2026-08-08 |
| Bajaj Housing Finance: Does making minimum payments affect credit score | https://www.bajajhousingfinance.in/resources/does-making-minimum-credit-card-payments-affects-credit-score | 2026-08-08 |
| Moneyview: Does paying minimum due affect CIBIL score | https://moneyview.in/cibil-score/does-paying-minimum-due-affect-cibil-score | 2026-08-08 |
