# Research Notes: The Minimum-Due Trap

## Topic selected

Why paying only the "Minimum Amount Due" on a credit card, before the due
date, still triggers interest charges from the date of each purchase, on
the whole billing cycle, not just the unpaid balance.

## Why it was selected

- Matches priority 2 (common audience confusion) and priority 3 (common,
  expensive money mistake) in the production brief.
- Not published or drafted in the prior 30 days (published_log.csv and
  carousel_topic_bank.md both show no prior entries; this is the first
  production run in this repository).
- The mechanism is a fixed regulatory rule (RBI Master Direction), not a
  volatile number, so it stays accurate for a long time. Safer than a
  topic built on a fee percentage or a market data point that ages fast.
- High save/share potential: it is a decision rule people can act on
  immediately and forward to a parent, sibling, or friend who says "I pay
  something before the due date every month."
- Distinct from the examples already used inside
  whenkevintalks_carousel_design_mastermind.md (zero-cost EMI, digital
  gold), so it does not recycle the mastermind's own illustrations as the
  carousel's substance.

## Primary sources consulted

1. RBI Master Direction on Credit Card and Debit Card Issuance and
   Conduct, as amended effective March 7, 2024. Direct PDF
   (rbidocs.rbi.org.in) could not be fetched in this run because the
   network egress policy for this session blocks that domain. Findings
   below are drawn from secondary reporting that cites and quotes the
   Master Direction directly (law-firm and compliance-newsletter
   analysis, listed below), cross-checked against two independent
   write-ups that agree on the same clause content.
   - [Recent Amendments to Master Directions on Credit Card and Debit
     Card - Lexology](https://www.lexology.com/library/detail.aspx?g=39f783e9-74c7-45e3-92fe-14abc1c61ddc)
   - [Updates to RBI Master Direction on Credit and Debit Card Issuance
     and Conduct - K&K newsletter](https://ksandk.com/newsletter/rbi-master-direction-on-credit-debit-cards-updates/)
   - [RBI's 2024 Amendment on Credit & Debit Card Issuance -
     Enterslice](https://enterslice.com/learning/rbi-amends-master-direction-on-credit-debit-card-insurances-2024/)
   - [Enhancing consumer protection and regulation - Bar and
     Bench](https://www.barandbench.com/view-point/consumer-protection-amendments-master-direction-credit-card-debit-card)
   - [RBI Credit Card Rules: 3-Day Rule, Fees & CIBIL -
     Finowings](https://www.finowings.com/blog/rbi-credit-card-rules)
2. Credit-utilisation and CIBIL explainer sources (used only for
   background context, not included as an on-slide claim, to keep the
   carousel to one idea):
   - [How Credit Utilization Ratio Works - Paisabazaar](https://www.paisabazaar.com/credit-score/how-credit-utilization-ratio-works-and-what-percentage-maintain-aio/)
   - [The Hidden Impact of Credit Utilization Ratio on CIBIL Score -
     Paytm blog](https://paytm.com/blog/credit-score/the-hidden-impact-of-credit-utilization-ratio-on-cibil-score/)

Source dates: all secondary sources accessed 2026-09-03, reporting on the
RBI Master Direction amendment effective 2024-03-07.

## Research notes

- Under the RBI Master Direction (as amended, effective 2024-03-07), if a
  cardholder does not pay the **Total Amount Due (TAD)** in full by the
  payment due date, the card issuer is permitted to withdraw the
  interest-free (grace) period and charge interest from the date of each
  transaction, on the outstanding amount, adjusted for payments, refunds
  and reversed transactions, rather than only from the due date forward.
- The Minimum Amount Due (MAD) is a separate, much smaller figure. Multiple
  sources describe it as the higher of: 100% of interest, fees and taxes
  billed; or roughly 5% of the total payment due, plus any overdue or
  over-limit amount and EMI instalments due. Paying only the MAD keeps the
  account "regular" (no late-payment mark, no missed-payment fee) but does
  **not** preserve the interest-free period on the rest of the balance.
- The Master Direction also requires card issuers to carry a clear warning
  on billing statements about the effect of paying only the minimum
  amount due.
- Once the interest-free period is lost for a cycle, new purchases in that
  cycle also stop earning interest-free treatment until the full
  outstanding amount is cleared.
- The exact minimum-due floor amount (reported by some secondary sources
  as an indicative ₹250) and the exact annualised interest rate charged
  by any given issuer are card-specific, vary by bank, and change over
  time. These are marked [VERIFY] below and were kept out of on-slide
  copy; the carousel instead tells the reader to check their own card's
  current terms.

## Claims included in the carousel (on-slide)

1. Paying on time and paying in full are different tests; only the second
   protects the interest-free period. (Source: RBI Master Direction as
   amended 2024-03-07, per Lexology / K&K / Enterslice / Bar and Bench
   summaries above.)
2. If the Total Amount Due is not paid in full, the issuer can charge
   interest from the date of each transaction, not just from the due
   date, on the outstanding balance. (Same source.)
3. Card issuers are required to warn cardholders on the statement about
   the effect of paying only the minimum due. (Same source.)
4. The Minimum Amount Due is a small fraction of the Total Amount Due,
   commonly linked to unpaid interest, fees, and a small percentage of
   the principal, not a repayment plan for the purchase itself. (Same
   source, general description, no fixed number used on-slide.)
5. Credit card interest rates run far higher than most other consumer
   borrowing (used only as a qualitative comparison, no fixed percentage
   stated on-slide; framed as "check your card's current rate").

## Claims removed or kept off-slide because they were not adequately verified

- An exact minimum-due floor figure (e.g. a fixed ₹250 minimum). Reported
  by some secondary sources as indicative, not confirmed against the
  primary RBI text in this run. Left out of on-slide copy.
- Any specific annualised or monthly interest rate percentage. Rates are
  set per issuer and per card and change over time. On-slide copy uses
  "far higher than most other borrowing" and "check your card's current
  rate" instead of a number.
- The credit-utilisation-and-CIBIL-score angle. This is a real and
  separate mechanism but was excluded from the carousel to keep to one
  central idea, per the one-idea rule in the design mastermind.

## [VERIFY] items

- [VERIFY] Exact minimum-amount-due floor value currently mandated or
  indicative (reported informally as ~₹250 by some secondary sources).
  Best primary source: RBI Master Direction on Credit Card and Debit
  Card Issuance and Conduct (rbidocs.rbi.org.in), latest consolidated
  version.
- [VERIFY] Exact wording of the mandatory minimum-due warning statement
  issuers must print, and where in the Master Direction it appears
  (clause number). Best primary source: same RBI Master Direction PDF,
  which could not be fetched directly in this session due to a network
  egress block on rbidocs.rbi.org.in.
- [VERIFY] Whether the "interest from transaction date" rule applies
  identically across all issuers or leaves scope for issuer-specific
  variation in practice. Best primary source: individual card issuers'
  Most Important Terms and Conditions (MITC) documents, cross-checked
  against the RBI Master Direction.

## Source links and dates

| Source | URL | Accessed |
|---|---|---|
| Lexology summary of RBI amendment | https://www.lexology.com/library/detail.aspx?g=39f783e9-74c7-45e3-92fe-14abc1c61ddc | 2026-09-03 |
| K&K newsletter on RBI Master Direction updates | https://ksandk.com/newsletter/rbi-master-direction-on-credit-debit-cards-updates/ | 2026-09-03 |
| Enterslice on RBI 2024 amendment | https://enterslice.com/learning/rbi-amends-master-direction-on-credit-debit-card-insurances-2024/ | 2026-09-03 |
| Bar and Bench on consumer-protection amendments | https://www.barandbench.com/view-point/consumer-protection-amendments-master-direction-credit-card-debit-card | 2026-09-03 |
| Finowings RBI credit card rules explainer | https://www.finowings.com/blog/rbi-credit-card-rules | 2026-09-03 |
| Paisabazaar on credit utilisation ratio (background only) | https://www.paisabazaar.com/credit-score/how-credit-utilization-ratio-works-and-what-percentage-maintain-aio/ | 2026-09-03 |
| Paytm blog on credit utilisation and CIBIL (background only) | https://paytm.com/blog/credit-score/the-hidden-impact-of-credit-utilization-ratio-on-cibil-score/ | 2026-09-03 |

## Note on source access

The primary RBI Master Direction PDF (rbidocs.rbi.org.in) and several
independent finance blogs (finowings.com, ksandk.com) returned a network
egress block in this session's sandboxed environment when fetched
directly. Findings above rely on WebSearch result summaries of these
pages rather than a direct fetch of the full text. Kevin should confirm
the exact clause wording against the live RBI Master Direction PDF before
publishing, and the two remaining [VERIFY] items above reflect that gap.
