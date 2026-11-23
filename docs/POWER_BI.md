# Optional Power BI handoff

No PBIX file is included or claimed tested. The main runnable dashboard uses dashboard.py; app.py is an optional Streamlit fallback. These CSVs allow an additional Power BI exercise on Ahmed's own installation.

1. Import `data/processed/requests.csv`. Set request_id, problem, borough and status to Text. Set timestamps to Date/Time; duration fields to Decimal Number; flags to True/False.
2. Use this single request-grain fact table first, avoiding joins that multiply requests. Add separate distinct problem/borough dimensions only when useful, with one-to-many single-direction relationships.
3. All measures below must use the same filter context. Check the totals against reports/audit.json before trusting charts.

```dax
Requests = COUNTROWS(requests)
Closed Status = CALCULATE([Requests], requests[is_closed_status] = TRUE())
Closed Share = DIVIDE([Closed Status], [Requests])
Valid Closures = COUNT(requests[closure_hours])
Median Closure Days = DIVIDE(MEDIAN(requests[closure_hours]), 24)
P90 Closure Days = DIVIDE(PERCENTILEX.INC(FILTER(requests, NOT ISBLANK(requests[closure_hours])), requests[closure_hours], 0.9), 24)
```

These are measure specifications for review, not a substitute for validating them in Power BI. Blank durations must not become zeros during import. Main checks:73,362 requests;73,005 Closed;72,991 valid closure durations;median30.364722hours;P90181.354444hours. Filter Snow or Ice/BROOKLYN:3,335 requests,median104.596944hours. Closed date does not prove a problem was fixed. Do not label due_date a resolution SLA.
