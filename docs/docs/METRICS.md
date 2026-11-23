# KPI contract

**Grain:** one unique request ID, not one citizen or one distinct real-world problem. Several requests can describe related incidents. All dashboard metrics respond to selected request types and boroughs.

| Metric | Definition / denominator |
|---|---|
| Requests | All rows in selected cohort, including date-quality issues |
| Closed status share | Rows with status exactly `Closed` / all selected rows |
| Valid closure duration | Closed status, non-null creation and closure, closure >= creation, neither timestamp after extraction |
| Median / P90 closure | Quantile of valid closure hours only, divided by 24 for days. DuckDB continuous quantile and pandas linear quantile agree. Not an average of group medians |
| Non-closed count | Status not Closed. Current snapshot has only Open/In Progress in this set; future unfamiliar values require review |
| Open age | Extract timestamp minus creation for valid non-closed records. Not time to eventual closure |
| Small-sample warning | Fewer than 100 valid closed rows in a problem/borough segment. An analyst-chosen communication threshold, not a statistical guarantee |

Closure date is when the agency closed the record. It does not establish the issue was fixed or the citizen satisfied. Due Date describes an expected agency UPDATE under internal SLAs. We do not use it as a universal resolution deadline.

## Selection and time

- Agency DSNY; creation in [2025-01-01, 2025-04-01), using the source's local floating timestamps.
- Snapshot completed 2026-11-23T15:49:55.202687+00:00. Convert extraction instant to America/New_York before open-age arithmetic.
- Source dates are timezone-naive local wall times. Simple subtraction can be off by an hour across daylight-saving changes. Closure metrics are local wall-clock elapsed time, not business hours or precise UTC duration.
- Cohort closure statistics omit unfinished or invalid cases, so they have selection/censoring bias. Long follow-up reduces but does not eliminate this. Use closure share and unresolved age alongside duration, not duration alone.
- Current status is not a full status history. Do not claim historical month-end backlog or reopening rates.
- Do not interpret borough counts as population-adjusted need, citizen satisfaction, employee productivity, causal effects or staffing shortfall.
- Q1 has winter-specific requests; conclusions do not automatically generalize to all seasons.

## Audit and exclusions

73,362 raw rows and 73,362 unique IDs. 73,005 Closed status; 357 non-closed. 14 Closed rows lack valid closure duration. Thus 72,991 rows enter closure quantiles. All rows remain in the request table; invalid durations are null, never zero. 0 invalid creation dates, 0 negative/future closure dates and 0 non-closed rows with closure dates in this snapshot. No general claim that future extracts will have zero issues.

## Investigation shortlist, not ranking of service quality

Compare each problem/borough median to its same-problem overall median from individual valid closures. Candidate threshold: >=100 valid closed records, median >=1.25 times baseline and at least 24 hours above baseline. Sort remaining candidates by request count. These are transparent exploratory thresholds, not significance testing or causal evidence. Cross-borough case mix, incident severity, weather, resources and administrative practices remain uncontrolled. Review with domain staff before any operational intervention.
