# Interface design notes

The custom local interface uses four task-focused views: Overview, Investigation, Request explorer, and Data & methods. Filters stay in one place and affect the KPI row, overview and records. Investigation deliberately retains all-borough reference data for the selected request type; an outline identifies the selected borough.

## Visual reference

Public Pinterest search viewed on 23 November 2026:
https://www.pinterest.com/search/pins/?q=analytics%20dashboard%20ui

The visible light ecommerce dashboard reference used a persistent navigation rail, compact KPI row, small metric icons, blue-violet accents and split analytical panels. Those layout ideas informed the final treatment. Dark and decorative references were not copied. Individual pins required login; only the publicly visible result images were inspected. No third-party artwork, logo, data or template code is included.

## Interpretation safeguards

Weekly intake has a count scale, week-start labels and an explicit warning about partial boundary weeks. Borough comparisons retain sample sizes and a small-sample flag. Closure is not proof of resolution. The interface and README preserve source attribution and interpretation limits.

## Current visual direction

The final revision uses a dark charcoal workspace with a lime primary metric and selected navigation. This direction was selected from the public finance-dashboard result grid viewed on 23 November 2026:
https://www.pinterest.com/search/pins/?q=finance%20dashboard%20ui%20design

Dark finance examples used a strong primary value, restrained bright accents, bordered analytical panels and clear separation between workspace navigation and data. The project adapts those ideas to operational requests, without imitating payment cards, invented financial values or reference artwork.

Manrope is bundled locally as a variable font under the SIL Open Font License. The font and license are in `web/fonts/`. Source:
https://github.com/google/fonts/tree/main/ofl/manrope

Typography is larger than the earlier prototype: desktop title 38px, KPI values 36px, body/control text 13–15px, panel headings 18px. Secondary labels remain smaller. Preview images should be normal viewport captures or readable detail crops, not an entire long page compressed into one phone image. Mobile navigation uses a two-by-two grid; tables remain supplemental horizontally scrollable records with the main KPI summary readable above them.
