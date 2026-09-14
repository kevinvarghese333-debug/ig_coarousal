# Sources and Fact-Check: No Cost EMI Already Has a Cost

Full research trail: `research_notes/2026-09-14_zero-cost-emi-hidden-cost_research.md`

## Claims used on-slide and their backing

1. **"Banks in India are not allowed to lend at zero percent."** (Slide 3)
   General mechanism reported consistently by multiple secondary outlets
   covering RBI's 2013 action on zero-interest EMI schemes. Primary RBI
   PDF could not be fetched directly this run (network egress restriction
   on `rbidocs.rbi.org.in`). **[VERIFY]** exact circular number and date
   before publishing if this claim is ever quoted more specifically.
   - https://www.moneylife.in/article/rbi-says-no-zero-percent-interest-scheme-for-buying-consumer-goods/34611.html
   - https://www.business-standard.com/article/finance/rbi-cracks-whip-on-retail-finance-schemes-with-hidden-cost-113092500706_1.html

2. **"The discount gets rebuilt as the loan's interest, a processing fee
   often still applies, and GST can sit on top of both."** (Slide 4)
   No specific percentage or rupee figure is claimed. General mechanism
   sourced from:
   - https://www.bankbazaar.com/credit-card/no-cost-emi.html
   - https://www.crifhighmark.com/blog/no-cost-emi
   - https://cleartax.in/s/gst-on-no-cost-emi
   - https://www.bankbazaar.com/credit-card/gst-on-credit-card-emi.html
   **[VERIFY]** current GST rate before ever stating a percentage; rates
   on financial services have been revised in recent years.

3. **Illustrative ₹60,000 / ₹57,600 example.** (Slide 5) Explicitly
   labelled "AN ILLUSTRATIVE EXAMPLE" and "*illustrative, varies by seller
   and offer" on-slide. Not a sourced market statistic, no verification
   needed, but flagged here for transparency.

4. **"Return the product, close the EMI early, or miss one due date, and
   the discount you thought you got is usually the first thing you
   lose."** (Slide 6) General mechanism corroborated by payment-processor
   documentation and brand/bank offer terms and conditions:
   - https://docs.payu.in/docs/refunds-for-emi
   - https://www.desidime.com/discussions/what-will-happen-to-no-cost-emi-when-fk-cancel-order-and-refund-amount
   **[VERIFY]** per issuer if a specific bank or platform is ever named.

## Claims deliberately excluded from on-slide copy

- Any specific GST percentage figure.
- Named-bank processing fee amounts (SBI, HDFC, ICICI, Axis, Kotak, IDFC
  First, etc.).
- A specific rupee gap between cash price and No Cost EMI price presented
  as a real market statistic (only used as a labelled illustrative
  example instead).
- The exact RBI circular date/number (kept to background research only).

## Number of [VERIFY] items: 4

See the "Facts to Verify Before Publishing" table in
`drafts/2026-09-14_zero-cost-emi-hidden-cost_carousel.md` for the full
verification table with source links.

## Fonts and assets

- Fonts used: Playfair Display (Bold, Regular) and DM Sans (Regular,
  Medium, Bold), fetched from Google Fonts and stored in `fonts/`. No
  missing fonts this run.
- No external images, screenshots or logos were used. Every visual
  element (receipt motif, comparison cards, checklist, price tags) is
  code-rendered with Pillow in `scripts/render_carousel.py`.
