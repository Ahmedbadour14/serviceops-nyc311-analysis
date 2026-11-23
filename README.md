# ServiceOps | NYC311 Service Request Analysis

**Ahmed Badour · Analyst / BI portfolio**

An analysis of 73,362 NYC sanitation service requests, combining a reproducible SQL pipeline, data-quality checks and an interactive local dashboard. The question: **which high-volume request segments warrant a closer look at closure times?**

![ServiceOps overview](docs/images/overview.png)

## Results at a glance

| Metric | Result | Definition |
|---|---:|---|
| Requests | 73,362 | Unique request IDs created Jan–Mar 2025, agency DSNY |
| Closed status | 73,005 (99.51%) | Status at the November 2026 extraction |
| Valid closure durations | 72,991 | Closed records with usable timestamps |
| Median closure | 1.27 days | Valid closed cases only |
| P90 closure | 7.56 days | 90th percentile of valid closed durations |

Two descriptive investigation leads emerged:

- **Brooklyn, Snow or Ice:** 3,335 requests; median 4.36 days versus 2.22 days across the same request type.
- **Bronx, Missed Collection:** 928 requests; median 7.90 days versus 2.23 days across the same request type.

These are leads for review, not proof of poor performance. Request mix, reporting practices and administrative closure can affect differences. Closure does not prove that a resident's problem was solved. See [findings and limitations](reports/FINDINGS.md).

## Explore the analysis

The dashboard has four views:

- **Overview:** request volume, weekly intake and borough-level closure summaries.
- **Investigation:** same-request-type borough comparisons, sample sizes and a highlighted selected borough. KPI cards retain the active filters.
- **Request explorer:** latest 100 filtered records and export of those displayed rows.
- **Data & methods:** metric definitions, source quality and interpretation limits.

![Workload and weekly intake](docs/images/analysis-detail.png)

![Filtered investigation with all-borough reference](docs/images/investigation.png)

The weekly chart uses Monday-start weeks. Its first and last weeks are partial, so the final drop must not be read as a demand collapse. The interface supports keyboard row selection and a mobile layout. Screenshots show the working application, not a hosted interactive demo.

## Technical approach

**Python · DuckDB SQL · HTML/CSS/JavaScript · pytest**

1. Download a scoped NYC311 snapshot with ordered pagination and bounded retries.
2. Record extraction timestamps and a SHA256 checksum.
3. Model one row per request, flag invalid dates and calculate eligible durations in SQL.
4. Reconcile counts, export reusable CSVs and generate an audit report.
5. Query the local database through a loopback-only Python server for dashboard filtering.

[SQL model](sql/model.sql) · [Build pipeline](src/build.py) · [Dashboard server](dashboard.py) · [Metric definitions](docs/METRICS.md)

## Run locally

Python 3.11 or 3.12 recommended. Also confirmed running on Windows with Python 3.13.3. Download or clone the repository, open its root folder in a terminal, then:

### Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe dashboard.py
```

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python dashboard.py
```

Open **http://localhost:8765** on the same computer. Keep the terminal open. The first run builds the local database from the bundled snapshot. Installation needs internet; daily use with the snapshot and bundled font does not. If `py` is unavailable on Windows but `python --version` works, use `python` for the first command.

This repository contains source code and screenshots. GitHub does not run the Python dashboard for visitors, and the localhost address is not a public demo link.

### Validate or rebuild

Using the virtual environment's Python executable in place of `python`:

```bash
python src/build.py
python -m pytest -q
```

The 11 tests cover snapshot checksum, unique IDs, cohort boundaries, count reconciliation, duration rules, exports, a hand-calculated SQL fixture, dashboard filters and the local API. The packaged project was rebuilt and tested after clean extraction.

Optional Streamlit fallback: `python -m streamlit run app.py`.

## Data and reproducibility

Source: [NYC Open Data / NYC311](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9). Requests created **January 1–March 31, 2025**, agency **DSNY**. Snapshot completed **November 23, 2026**, recorded in UTC in [the manifest](data/raw/manifest.json).

The bundled fields exclude street addresses, contact details and resolution free text. The frozen raw JSON and CSV exports support reproducibility. The source updates; historical request creation dates do not make the extracted status a historical backlog record.

`python src/download.py` reuses the snapshot. `python src/download.py --refresh` explicitly replaces it from the live source and changes the results. Rebuild and retest after any refresh. The API download is paginated, not an atomic source transaction; delete cached `data/raw/pages` before a new continuous extraction if resuming older pages would mix sessions.

[Source metadata](data/raw/source_metadata.json) · [Audit report](reports/audit.json) · [Source terms](https://opendata.cityofnewyork.us/overview/#termsofuse)

## Project map

```text
dashboard.py          Local dashboard server
web/                  Custom interface and bundled font
sql/model.sql         Request-grain model and aggregates
src/                  Acquisition and build scripts
tests/                Data, SQL fixture and dashboard/API tests
data/raw/             Frozen source snapshot, metadata and manifest
data/processed/       CSV exports; database rebuilt locally
reports/              Findings, audit and investigation shortlist
docs/                 Metrics, Arabic learning guide and design notes
```

## Authorship and licensing

This is Ahmed Badour's analyst/BI portfolio project, using public NYC311 data. It is an educational analysis, not professional client work or an official City assessment.

The code is provided under the [MIT License](LICENSE). NYC source data remains subject to its own terms, and the bundled Manrope font has its [SIL Open Font License](web/fonts/OFL.txt). No ownership of the underlying public dataset or third-party font is claimed. This is not an official City assessment.

[Arabic walkthrough and practice questions](docs/LEARN_AR.md) · [Optional Power BI notes](docs/POWER_BI.md)
