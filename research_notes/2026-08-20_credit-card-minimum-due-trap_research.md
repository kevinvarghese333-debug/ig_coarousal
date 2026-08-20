# Research Notes: Credit Card Minimum Due Trap

## Topic selected

Why people who pay their credit card bill "on time" every month can still end up losing money to interest, because paying only the Minimum Amount Due (MAD) is not the same as paying the Total Amount Due (TAD).

## Why it was selected

- This is topic #2 on the priority list in `carousel_topic_bank.md` and is the exact worked example used inside `whenkevintalks_carousel_design_mastermind.md` itself as the model "one sharp idea," which signals it fits the brand voice well.
- No topics have been published yet (`published_log.csv` is empty), so there is no 30-day repeat conflict.
- It hits priority category 3 ("a common and expensive money mistake") and touches a near-universal audience behaviour: salaried people who treat "I paid something" as "I'm fine."
- Strong save/share/comment potential: it corrects a specific, common misunderstanding, gives a checkable decision rule, and invites a personal, non-embarrassing confession in comments ("did you check MAD vs TAD?").

## Primary sources consulted

Direct fetch of `rbi.org.in` was blocked by this session's network egress proxy (`EGRESS_BLOCKED`), so the underlying regulation could not be quoted verbatim from the primary PDF this session. The mechanism below is corroborated across multiple independent secondary sources reporting on the same RBI Master Direction — Credit Card and Debit Card, Issuance and Conduct (2022, last amended March 2024). Kevin should confirm against the primary RBI text before publishing (link included below for direct access, since it may not be blocked outside this sandboxed session).

- RBI Master Direction — Credit Card and Debit Card – Issuance and Conduct: https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300 (not directly fetchable this session; cited via secondary reporting below) — regulation dated April 2022, last amended March 2024.
- RBI consumer FAQ PDF on Credit/Debit Cards: https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf (not directly fetchable this session).
- Secondary reporting corroborating the interest-free-period mechanic: Moneyview "RBI Guidelines on Credit Card Late Payment Charges" (2026 update), Business Standard "RBI tightens norms for credit card billing" (2015, formula history), sharmadebtsolutions.in "Minimum Due in Credit Card (India) Explained: RBI Rules, Risks & Smarter Alternatives" (2025), urbanmoney.com "Minimum Amount Due on Credit Card: Meaning, CIBIL Impact & Risks", freed.care "Does Paying Minimum Due Affect CIBIL?".
- Interest rate range corroboration (2026): Forbes Advisor India "Credit Card Interest Rates", Bajaj Finserv Markets "Compare Credit Card Interest Rates in India 2026", Fincash "Credit Card Interest Rate 2026", Axis Bank and Airtel blogs on credit card interest rates.

## Research notes

1. **Loss of interest-free period.** If the cardholder does not pay the full Total Amount Due by the due date, the interest-free (grace) period is lost, and interest can be charged from the date of each transaction on the outstanding amount (adjusted for payments/refunds), not just on the unpaid minimum. This is reported consistently across secondary sources summarising the RBI Master Direction.
2. **Minimum Amount Due formula.** Secondary sources describe an RBI-aligned formula effective from December 1, 2022: the higher of (100% of interest, fees and taxes billed; 5% of the total amount due) plus the higher of (past due amount; over-limit amount) plus any EMI instalments due. In practice this is commonly summarised as "around 5% of the outstanding balance." Treated as [VERIFY] since the primary RBI text could not be fetched this session.
3. **Mandatory disclosure.** Statements are required to carry a written warning that paying only the minimum due stretches repayment over months or years with compounded interest. This supports the "the bank already has to warn you" angle but was not used as a specific on-slide quote since exact wording could not be confirmed against the primary source this session.
4. **Credit score / bureau impact.** Paying at least the minimum by the due date generally keeps the account marked "current" and is not reported as a missed payment. The score damage described in these secondary sources is indirect: a rising unpaid balance increases credit utilisation, which can affect creditworthiness over time. This is the basis for Slide 7's "score looks fine, damage is elsewhere" claim.
5. **Interest rate range.** Multiple 2026 secondary sources converge on a broad range of roughly 2.5% to 3.75% per month (commonly cited around 3% to 3.6%), translating to roughly 35% to 45% annualised, with wide variation by issuer, card variant and customer relationship. Treated as illustrative and hedged with "often"/"can be" language on-slide, since exact rates are issuer-specific and change over time.

## Claims included in the carousel

- Paying only the Minimum Amount Due keeps an account status "current" but does not stop interest, and interest can start from the date of each purchase rather than the due date, once the interest-free period is lost. (Slide 4, hedged with "under RBI's card rules" and "can apply.")
- Minimum Amount Due is commonly around 5% of the outstanding balance. (Slide 4/5, hedged as "usually around.")
- An illustrative example using round numbers (₹40,000 bill, ~₹2,000 minimum, ₹38,000 remaining) is explicitly labelled as an illustrative example, not a real card statement. (Slide 5.)
- Card interest rates are often in the 3% to 3.75% per month range depending on the card. (Slide 5, hedged as "often," "depending on the card.")
- Minimum due payments keep the account marked current; the more durable risk is rising credit utilisation, not an immediate score drop. (Slide 7, hedged as general behaviour, not a guarantee for every bureau/lender.)

## Claims removed because they were not adequately verified

- An exact, issuer-agnostic number for how much revenue card issuers earn from revolving interest was considered for Slide 6 and removed. No verified, current, general figure was found; the slide was rewritten to describe the incentive qualitatively ("one of the more reliable ways card issuers earn revenue") instead of citing a number.
- The RBI's specific "3-day grace period before a payment can be reported as past due" was researched but left out of the on-slide copy to keep the carousel to one idea. It is a genuine and separate RBI protection (against late fees and adverse bureau reporting for very short delays) and would deserve its own carousel rather than being folded in here, since it addresses a different question (lateness) rather than partial payment.
- A specific single number for "typical minimum due percentage" beyond "usually around 5%" was avoided, since the actual formula has multiple components (interest/fees floor, past-due floor, EMI amounts) and varies by cardholder circumstances.

## All [VERIFY] items

| # | Item | Status |
|---|---|---|
| 1 | RBI Master Direction wording on loss of interest-free period and interest from transaction date | [VERIFY] against primary RBI PDF/Master Direction text before publishing |
| 2 | Minimum Amount Due formula components and "around 5%" simplification | [VERIFY] against primary RBI source or current issuer T&Cs |
| 3 | Interest rate range "often 3% to 3.75% a month" | [VERIFY] against 2-3 current issuer rate cards close to publish date, since rates change |
| 4 | Credit score/utilisation impact of carrying a minimum-due balance | [VERIFY] against CIBIL or a credit bureau's own consumer education page, if a firmer source is wanted before publishing |

## Source links and dates

- https://www.rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300 — RBI Master Direction (original April 2022, last amendment referenced March 2024). Not fetched directly this session (network egress blocked); referenced via secondary reporting.
- https://www.rbi.org.in/commonman/Upload/English/FAQs/PDFs/FAQMDCreditCardandDebitCard.pdf — RBI consumer FAQ. Not fetched directly this session (network egress blocked).
- https://moneyview.in/credit-card/rbi-guidelines-on-credit-card-late-payment-charges — accessed via search summary, 2026.
- https://sharmadebtsolutions.in/minimum-due-in-credit-card-india/ — accessed via search summary, 2025 article.
- https://www.urbanmoney.com/credit-score/minimum-amount-due-credit-card-cibil-impact-csgen — accessed via search summary.
- https://www.forbes.com/advisor/in/credit-card/credit-card-interest-rate/ — accessed via search summary, 2026.
- https://www.bajajfinservmarkets.in/credit-card/credit-card-interest-rates — accessed via search summary, 2026.
- https://www.fincash.com/l/pf/credit-card-interest-rate — accessed via search summary, 2026.

Note: Because primary regulator PDFs could not be fetched directly in this sandboxed session (egress blocked to rbi.org.in), every regulatory claim above is corroborated only via secondary reporting. This is flagged clearly in the draft's "Facts to Verify" table and should be a quick primary-source check for Kevin before publishing, not a blocker for producing the draft and PNGs.
