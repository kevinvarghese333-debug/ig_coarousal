# Carousel Topic Bank

## Priority topics

1. Why zero-cost EMI is not always a free decision
2. Why people who pay their credit-card bill on time still get into money trouble
3. The ₹100 digital-gold button: convenient is not the same as protected
4. Why salary hikes still leave people broke
5. The business behind 10-minute delivery
6. Why a company can report profit while cash is disappearing
7. What a credit score does not tell a lender
8. How loan apps make small loans feel harmless
9. Why cashback changes spending behaviour
10. The real cost of buying a phone for a small monthly EMI

## Rule

Do not repeat a topic published in the prior 30 days unless the angle is materially different. Move used topics to the Published section with date and link.

## Known routine bug: this file does not reflect real production history

As of 2026-08-21, this file and `published_log.csv` were found to be out of sync with the actual production history in the connected Google Drive delivery folder, which holds dated output folders back to 2026-07-27. The root cause: each day's routine runs on a fresh `claude/gracious-goodall-*` branch off `main`, and these branches have not been merged back into `main` (26 unmerged branches, one open, unmerged pull request as of this date). So every run's history check has effectively been running against an empty record, and several topics have been produced multiple times within days of each other without anyone knowing, including at least five loan-app carousels and six to seven "no-cost EMI" carousels between 2026-07-27 and 2026-08-20. See `research_notes/2026-08-21_quick-commerce-basket-size_research.md` for the full investigation. Until the branches are merged (or the routine is changed to push to `main` directly, or to check Drive history in addition to this file), do not trust this file's "Published" section as complete. Cross-check the Drive delivery folder's dated subfolders before finalising a topic.

## Topics covered in the Drive delivery folder (2026-07-27 through 2026-08-21), not yet reflected below

- no-cost-emi-hidden-cost / zero-cost-emi-hidden-cost / no-cost-emi-real-cost (variants): 2026-07-27, 07-28, 07-29, 08-01, 08-06, 08-13, 08-15, 08-16, 08-17
- credit-card-minimum-due-trap / on-time-credit-card-trap / credit-card-emi-trap (variants): 2026-07-30, 08-02, 08-03, 08-05, 08-07, 08-08, 08-10, 08-20
- loan-apps-feel-harmless / loan-apps-small-loans-feel-harmless / small-loan-disclosure-rule / loan-app-friction-design (variants): 2026-08-09, 08-11, 08-14, 08-19
- digital-gold-not-protected: 2026-08-12
- credit-score-timing-trap: 2026-08-18
- rbi-weekly-credit-reporting: 2026-07-31
- quick-commerce-basket-size (this run): 2026-08-21

## Published

- 2026-08-21: The 10 Minutes Was Never the Business Model (quick-commerce-basket-size). Central idea: quick commerce apps compete on average order value, not delivery speed, since dark-store fixed costs do not shrink for a small basket. Draft: `drafts/2026-08-21_quick-commerce-basket-size_carousel.md`.
