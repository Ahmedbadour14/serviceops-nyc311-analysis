-- Grain: one unique service request. Keep questionable rows visible in audit.
CREATE OR REPLACE TABLE requests AS
WITH typed AS (
 SELECT unique_key AS request_id, try_cast(created_date AS TIMESTAMP) AS created_at,
 try_cast(closed_date AS TIMESTAMP) AS closed_at, agency,
 coalesce(nullif(trim(complaint_type),''),'Unknown') AS problem,
 coalesce(nullif(trim(borough),''),'Unknown') AS borough,
 coalesce(nullif(trim(status),''),'Unknown') AS status
 FROM read_json_auto('data/raw/requests.json')
), flags AS (
 SELECT *, created_at IS NULL OR created_at > $snapshot AS invalid_created,
 closed_at IS NOT NULL AND (closed_at < created_at OR closed_at > $snapshot) AS invalid_closed,
 status = 'Closed' AS is_closed_status,
 status = 'Closed' AND closed_at IS NOT NULL AND closed_at >= created_at AND closed_at <= $snapshot AS valid_closed
 FROM typed
)
SELECT *, CASE WHEN valid_closed AND NOT invalid_created THEN date_diff('second',created_at,closed_at)/3600.0 END AS closure_hours,
 CASE WHEN NOT is_closed_status AND NOT invalid_created THEN date_diff('second',created_at,$snapshot)/3600.0 END AS open_age_hours
FROM flags;

CREATE OR REPLACE TABLE segment_summary AS
SELECT problem, borough, count(*) AS requests,
 count(*) FILTER(WHERE is_closed_status) AS closed_status_count,
 count(closure_hours) AS valid_closure_count,
 count(*) FILTER(WHERE NOT is_closed_status AND NOT invalid_created) AS unresolved_count,
 median(closure_hours) AS median_hours, quantile_cont(closure_hours,0.9) AS p90_hours,
 median(open_age_hours)/24 AS median_open_days
FROM requests GROUP BY problem,borough;

CREATE OR REPLACE TABLE weekly_volume AS
SELECT date_trunc('week',created_at)::DATE AS week,problem,borough,count(*) AS requests
FROM requests WHERE NOT invalid_created GROUP BY 1,2,3;
