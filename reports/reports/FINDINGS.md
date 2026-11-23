# Investigation memo

Snapshot: 2026-11-23T15:49:55.202687+00:00. Historical cohort: DSNY requests created January–March 2025. This is an educational analysis, not an official agency assessment.

## Answer

Start a diagnostic review with Brooklyn Snow or Ice and Bronx Missed Collection, not a blanket claim that one borough performs poorly. Both have substantial volume and materially longer median closure than the overall same-request-type baseline. Validate case mix and administrative closure practice before making operational changes.

## Baseline

- 73,362 requests, all unique IDs.
- 73,005 Closed-status records (99.51%);357 non-closed records at extraction.
- 72,991 valid closed durations;14 Closed records have missing valid duration and are excluded, not zero-filled.
- Median closure 1.27 days;P90 7.56 days. These describe valid closed cases only.

## Investigation leads

| Request type / borough | Requests | Median closure | Same-type overall median |
|---|---:|---:|---:|
| Snow or Ice / Brooklyn | 3,335 | 4.36 days | 2.22 days |
| Missed Collection / Bronx | 928 | 7.90 days | 2.23 days |

The candidate file uses an analyst-chosen screen: at least100 valid closures, median >=1.25times the same-type median and a gap of at least24hours. It is not a significance test. See `investigation_candidates.csv` for the complete resulting shortlist. Source mix and reporting practices can explain differences.

## Actions to investigate, not claimed outcomes

1. Review a sample of long-duration cases with domain staff. Separate record-keeping delays from service delays before changing staffing or workflow.
2. For Snow or Ice, inspect weather-event timing and volume surges within the same request type. Do not infer winter patterns apply year-round.
3. For Missed Collection, inspect route/process context if independently available. We have no staffing, route schedule or cost data, so cannot estimate savings or prescribe headcount.
4. Reconcile the357 non-closed records with the agency if possible. They may include stale records; this is not the March2025 backlog.

## What would change the conclusion

A second comparable quarter, issue severity, weather, local resource data and verified status history could strengthen or reverse these leads. No causal claim, citizen satisfaction claim, universal SLA-breach rate or projected financial benefit is justified from this dataset alone.

Source: https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9
