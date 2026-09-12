# GitHub Activity Data Warehouse — Run Book, Part 1 (Stage 1)

**Audience:** strong Python and SQL, first time with Airflow, dbt, Spark, and Databricks.
**Rule of this document:** it tells you precisely *what* to build and *how to check that you built it right*. It deliberately contains no code to copy. Typing it yourself is the point.

---

## 0. Stage 1 scope

### 0.1 What Stage 1 is

Stage 1 takes you from an empty directory to a **scheduled, idempotent, tested pipeline that lands seven consecutive days of GH Archive data and answers one of the four project questions end to end.**

You are building a vertical slice, not a layer at a time. A thin pipeline that runs on a schedule and survives a rerun teaches more than a wide pipeline that only runs once by hand.

**Concrete deliverables at the end of Stage 1:**

| #   | Deliverable                                                                                                |
| --- | ---------------------------------------------------------------------------------------------------------- |
| 1   | A git repo with an installable Python package, an Airflow project, a dbt project, and Spark job scripts    |
| 2   | A Databricks Free Edition workspace with a Unity Catalog catalog, four schemas, and a volume               |
| 3   | A **raw zone**: GH Archive `.json.gz` files landed byte-for-byte, immutably, one object per source hour    |
| 4   | A **bronze** Delta table: one row per event, full payload preserved, safely re-runnable per hour           |
| 5   | A **silver** Delta layer: typed, deduplicated events plus two event-type-specific tables                   |
| 6   | A **dbt project** producing `dim_repo`, `dim_actor`, `dim_date`, `fct_pull_request_activity`, and one mart |
| 7   | **Airflow 3 running locally in Docker**: an hourly ingest DAG and a daily transform DAG                    |
| 8   | A completed **7-day backfill**, including at least one deliberately broken and recovered hour              |
| 9   | **Tests**: pytest unit tests on pure Python, a bronze quality gate, dbt schema tests                       |
| 10  | `docs/OPERATIONS.md` — how to backfill, how to recover a failed hour, what to check when it breaks         |

**The one question Stage 1 answers:** *How long does a pull request wait for its first review?*

### 0.2 What Stage 1 is explicitly *not*

Write these down and resist them. Scope creep is the main way learning projects die.

- **No full history backfill.** Seven days only. 2011–present is Stage 3 work.
- **No pre-2015 schema.** The event schema changed on 2015-01-01; you will only touch modern data.
- **No contributor retention analysis.** Six-month retention needs six months of history. Impossible now, by construction.
- **No bus factor / concentration metrics.** Stage 2.
- **No CI/CD, no alerting, no Databricks Asset Bundles, no Terraform.** Stage 2 and 3.
- **No streaming, no Auto Loader, no Delta Live Tables.** Batch only. Learn the boring path first.

### 0.3 A limitation you must document, not solve

The PR review latency question asks specifically about *first-time* contributors. With a 7-day window you cannot know whether someone is a first-time contributor — you can only know whether this is their first event *inside your window*. That is a biased proxy: someone with a decade of history looks identical to a genuine newcomer.

Stage 1 requirement: compute the metric with a clearly named `is_first_seen_in_window` flag, and write a paragraph in `docs/KNOWN_LIMITATIONS.md` explaining why the number is not yet trustworthy and what would fix it. **Being explicit about the limits of your data is a core data engineering skill.** Most tutorials never model it.

### 0.4 Architecture

```
GH Archive HTTPS  ──(1)──►  local temp disk  ──(2)──►  Unity Catalog Volume   [RAW: immutable .json.gz]
                                                              │
                                                             (3) PySpark on Databricks serverless
                                                              ▼
                                                     bronze.events (Delta)     [one row per event, VARIANT payload]
                                                              │
                                                             (4) PySpark
                                                              ▼
                                              silver.events / silver.pull_request_* (Delta)
                                                              │
                                                             (5) dbt on a SQL warehouse
                                                              ▼
                                                    gold: dims, facts, marts
```

Airflow runs **locally in Docker** and orchestrates all five arrows. It does no heavy computation itself.

**Why downloads happen outside Databricks:** Databricks Free Edition is serverless-only and restricts outbound internet access to a limited set of trusted domains. Your Spark job cannot reach `data.gharchive.org`. This constraint is a gift — separating extract from transform is correct design anyway, and it makes your raw zone replayable without re-downloading.

### 0.5 Platform constraints to design around

Databricks Free Edition, verified limits:

- Serverless compute only; custom compute configurations are not supported. One SQL warehouse, limited to 2X-Small. Max 5 concurrent job tasks per account. R and Scala are unsupported.
- Serverless uses Spark Connect: only Spark Connect APIs are supported, and RDD APIs are not. Stick to the DataFrame and SQL APIs — you should be doing that anyway.
- DBFS access is limited; use Unity Catalog volumes or workspace files instead.
- Exceeding your quota shuts down compute for the rest of the day. Data and settings are not deleted.

That last one is the important one: **run out of quota and you lose a day.** Do your exploration on one file, not one hundred.

### 0.6 Tooling versions

Pin these in your project and note them in the README. Check for newer patch versions when you start.

| Tool           | Version                             | Note                                                                                                                                         |
| -------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| Python         | 3.11 or 3.12                        | Match what your Airflow image ships                                                                                                          |
| Apache Airflow | 3.3.x                               | Airflow 3.3.1 released 2026-08-12. Airflow 3 removed `execution_date`; use `logical_date`. `catchup` now defaults to `False`                 |
| Astro CLI      | latest                              | Easiest local Airflow. Alternative: the official Docker Compose file                                                                         |
| dbt Core       | 1.12.x with `dbt-databricks` 1.12.x | Use the mature Python engine. dbt's new Fusion engine has a Databricks adapter but it is still in preview — not what you want while learning |
| Databricks CLI | v0.2xx (the new Go CLI)             | Not the legacy Python `databricks-cli`                                                                                                       |
| Spark          | whatever serverless provides        | Serverless is versionless and always current                                                                                                 |

### 0.7 Time budget

Roughly 40–60 focused hours. If a step takes 3× the estimate, that is normal and is where the learning is.

| Steps | Theme                                       | Estimate |
| ----- | ------------------------------------------- | -------- |
| 1–5   | Foundations, accounts, data understanding   | 8–10 h   |
| 6–10  | Extract, load, and first Spark job          | 10–14 h  |
| 11–14 | Airflow, scheduling, backfill, quality gate | 10–14 h  |
| 15–18 | Silver and the dbt warehouse                | 10–14 h  |
| 19–20 | Full orchestration and operations           | 4–6 h    |

### 0.8 Glossary

Learn these words now; the rest of the run book uses them without explanation.

- **Grain** — what one row of a table represents. The single most important thing to decide about any table.
- **Idempotent** — running the same task twice produces the same result as running it once.
- **Backfill** — running a scheduled pipeline for past time periods it never ran for.
- **Logical date / data interval** — in Airflow, the *time period the run is responsible for*, which is not the wall-clock time the run happens.
- **Medallion (bronze/silver/gold)** — a convention: bronze is raw-ish and faithful, silver is cleaned and typed, gold is modeled for business questions.
- **Delta table** — Parquet files plus a transaction log, giving ACID transactions and time travel.
- **VARIANT** — a Databricks column type for semi-structured JSON that stays queryable without a fixed schema.
- **Unity Catalog** — Databricks' governance layer. Objects are addressed as `catalog.schema.table`.
- **Volume** — a Unity Catalog-governed place to store *files* (as opposed to tables).

---

# The Steps

Each step has a **Goal**, an **Implementation** section, a **Verify** section, and a **Done when** line. Do not move on until "Done when" is true. Several steps have a **Gotchas** section listing failures you will otherwise spend hours on.

---

## Step 1 — Repository, environment, and project skeleton

**Goal:** a reproducible local environment and a directory layout that will not need reorganizing in Stage 2.

### Implementation

1. Create a git repository named `gh-warehouse`. Initialize it with a README and a `.gitignore` covering Python artifacts, `.env`, virtual environments, `logs/`, `target/`, `dbt_packages/`, and `.astro/`.
2. Install a modern Python package manager. `uv` is fastest; Poetry is fine. Use it for everything — do not use bare `pip install` into your system Python.
3. Create this directory layout:

```
gh-warehouse/
├── ghwh/                  # installable Python package — pure, testable logic
│   ├── config.py          # settings loaded from environment
│   ├── extract.py         # downloading from GH Archive
│   ├── load.py            # uploading to Databricks volumes
│   ├── paths.py           # URL and volume path construction
│   └── hours.py           # hour-range and calendar helpers
├── jobs/                  # PySpark scripts that run ON Databricks
├── airflow/               # Astro/Airflow project (created in Step 11)
├── dbt/                   # dbt project (created in Step 16)
├── tests/                 # pytest, mirroring ghwh/
├── docs/
│   ├── DATA_CONTRACT.md
│   ├── OPERATIONS.md
│   └── KNOWN_LIMITATIONS.md
├── notebooks/             # scratch exploration, committed but never imported
├── .env.example
├── pyproject.toml
└── README.md
```

4. In `pyproject.toml`, declare `ghwh` as an installable package. Dependencies for now: an HTTP client (`httpx` or `requests`), the Databricks SDK for Python, and a settings library (`pydantic-settings` is worth it). Dev dependencies: `pytest`, `ruff`, `mypy`.
5. Install the package in editable mode into your virtual environment.
6. Add `docs/DECISIONS.md` and write your first entry: one paragraph on why raw files are landed before any parsing happens. Keep adding an entry every time you make a non-obvious choice. In six months this file is the most valuable thing in the repo.

### Verify

- Open a fresh Python REPL in the virtual environment and import `ghwh`. It should import with no path manipulation.
- Run `pytest`. It should exit 0 with zero tests collected — proving the test runner is wired up.
- Run `ruff` across the repo; it should pass or report only style issues you then fix.
- Run `git status`. Your virtual environment directory must not appear.

**Done when:** a colleague could clone the repo, run two commands, and have a working environment.

---

## Step 2 — Accounts, credentials, and secret hygiene

**Goal:** working authenticated access to Databricks from your laptop, with no secret ever committed.

### Implementation

1. Sign up for **Databricks Free Edition**. Choose the cloud region closest to you. You get one workspace and one metastore. DONE
2. In the workspace, confirm you can open a serverless notebook and run a trivial SQL query. If serverless does not start, stop and resolve that before continuing — everything downstream depends on it. **DONE**
3. Generate a **personal access token** (User Settings → Developer → Access tokens). Set a short-ish expiry and diary a renewal reminder; an expired token is a classic 3 a.m. pipeline failure. **DONE**
4. Install the **Databricks CLI** (the Go one — verify by checking that its version reports `v0.2x`, not `0.17`). Configure a profile with your workspace host and token. The CLI stores this in `~/.databrickscfg`. **DONE**
5. Create `.env.example` in the repo listing every variable name your project will need with dummy values: workspace host, token, catalog name, volume path, SQL warehouse HTTP path. Create a real `.env` locally, and confirm it is git-ignored. **DONE**
6. In `ghwh/config.py`, define a settings object that reads those variables from the environment and **fails loudly at import time if a required one is missing**. Never default a credential to an empty string. **<u>DONE</u>**
7. Create a SQL warehouse if one does not exist. On Free Edition it will be 2X-Small; that is your only option. Note its **HTTP path** — dbt needs it in Step 16. **DONE**

### Verify

- Use the CLI to list catalogs in your workspace. You should see the default catalogs. **DONE**
- Use the CLI to list your workspace's current user. This confirms the token is valid, not merely present. **DONE**
- From Python, use the Databricks SDK with credentials from `ghwh.config` to list clusters or warehouses. This proves your config layer works, not just the CLI's. **DONE**
- Deliberately unset one required environment variable and import `ghwh.config`. It must raise a clear error naming the missing variable. **DONE**
- Run `git log -p` and search for your token string. Zero hits.**DONE**

**Gotchas**

- If you already had the legacy Python `databricks-cli` installed, the two binaries collide on `PATH`. Uninstall the old one.
- Free Edition has **no account console and no account-level APIs** — some tutorials assume these exist. Skip those sections.

**Done when:** you can authenticate to Databricks from the CLI, the SDK, and your own config module, and `.env` is untracked.

---

## Step 3 — Explore GH Archive by hand, with no Spark

**Goal:** understand the data and size the project *before* writing a pipeline. This is capacity planning, and skipping it is why pipelines get rebuilt.

### Implementation

1. Learn the URL format: files live at `https://data.gharchive.org/` with the pattern `YYYY-MM-DD-H.json.gz`. **The hour is not zero-padded** — hour 3 is `-3.json.gz`, not `-03.json.gz`. This trips up nearly everyone. Hours run 0–23 in UTC. **DONE**
2. Download exactly one hour by hand with `curl` or your browser. Record its compressed size. **DONE**
3. Decompress it and inspect it in a notebook with plain Python — no Spark, no pandas at first. It is newline-delimited JSON (one complete JSON object per line), not a JSON array. **DONE**
4. Answer these questions and write the answers into `docs/DATA_CONTRACT.md`:
   - How many lines (events) are in one hour? **DONE**
   - What is the uncompressed size? What is the compression ratio? **DONE**
   - What are the distinct values of the top-level `type` field, and their counts? You should see on the order of 15 event types. **DONE**
   - What top-level keys does *every* record have? Compare the key sets of the first 10,000 records and take the intersection and the union. The difference between those two sets is your schema drift. **DONE**
   - For each event type, what keys appear inside `payload`? These differ wildly by type — that is the central modeling problem of this project. **DONE**
   - What are the top 20 repositories by event count? Compute what share of all events the top 1% of repos account for. This is your skew, and it will shape every join you write later. **DONE**
5. Focus on the event types you need for the review-latency question: `PullRequestEvent`, `PullRequestReviewEvent`, `PullRequestReviewCommentEvent`, `IssueCommentEvent`. For each, dump one full example record, pretty-printed, into `docs/DATA_CONTRACT.md`. Note the exact JSON path to: PR number, PR creation timestamp, PR author login, review submission timestamp, review state, and repository full name. **DONE**
6. **Capacity plan.** Multiply your single-file compressed size by 168 (7 days × 24 hours). Compare that to (a) your laptop's free disk and (b) what you are willing to store in Databricks. If the number is uncomfortable, pick an older 7-day window — GH Archive files from earlier years are substantially smaller — but stay after 2015-01-01. Write your chosen window into the README and commit to it. **DONE**
7. Note the `created_at` field is UTC ISO-8601, and that event `id` is a numeric string, not an integer. **DONE**

### Verify

- You can state, from your own measurement and not from this document, the event count and byte size of one GH Archive hour. **DONE**
- `docs/DATA_CONTRACT.md` contains a table of event types with counts, and one full example record for each of the four PR-related types. **DONE**
- You have written down the exact JSON paths for the six fields listed above. **DONE**
- You have committed to a specific 7-day window with specific dates. 
- Request an hour you expect not to exist (a date in the future) and observe the HTTP status code. You will need to handle this in Step 13.

**Done when:** you could explain to someone else what a GH Archive record looks like without opening a file.

---

## Step 4 — Design the tables before you build them

**Goal:** written decisions about grain, keys, and layer boundaries. One hour here saves a week later.

### Implementation

Write `docs/DATA_CONTRACT.md` sections for each table below. For every table state: **grain (one row = ?), primary key, partitioning/clustering, and write mode.**

1. **`raw` volume layout.** Decide a path convention. Recommended: `events/dt=YYYY-MM-DD/hour=HH/YYYY-MM-DD-H.json.gz`, with the hour zero-padded *in the directory* but the filename kept exactly as the source names it. Rationale: directories sort and glob predictably; the filename remains provably identical to the source. Write down which of those two conventions is authoritative if they ever disagree.
2. **`bronze.events`.** Grain: one row per GitHub event. Columns:
   - Promoted scalars for filtering and partitioning: `event_id` (string), `event_type` (string), `created_at` (timestamp), `actor_id` (bigint), `actor_login` (string), `repo_id` (bigint), `repo_name` (string), `org_id` (bigint, nullable), `event_date` (date), `event_hour` (tinyint).
   - `payload` as **VARIANT** — the whole nested payload, unparsed and lossless.
   - Audit columns: `_source_file` (string, full volume path), `_source_url` (string), `_ingested_at` (timestamp), `_run_id` (string, the Airflow run identifier).
   - Partition by `event_date`. Write mode: **overwrite-by-predicate on `(event_date, event_hour)`**.
   - Explicit non-goal: bronze does **not** deduplicate and does **not** filter. It is a faithful, replayable transcription of the raw file plus lineage. Any judgment call belongs in silver.
3. **`silver.events`.** Grain: one row per *distinct* event. Deduplicated on `event_id`. Typed. Bad rows quarantined rather than dropped silently.
4. **`silver.pull_request_events`** and **`silver.pull_request_review_events`.** Grain: one row per PR event / per review event, with payload fields extracted into real typed columns. These are the tables that make schema drift visible.
5. **Gold layer.** Sketch the star: `fct_pull_request_activity` at the grain of one row per PR-related event, joined to `dim_repo`, `dim_actor`, and `dim_date`. Decide now whether your dimensions are Type 1 (overwrite; repo renames lose history) or Type 2 (track history). **Choose Type 1 for Stage 1** and write down why, plus what it costs you: repository renames are common on GitHub and Type 1 will silently rewrite history. That is an acceptable Stage 1 trade-off and a deliberate Stage 2 upgrade.
6. Decide your **surrogate key strategy**. GitHub gives you natural keys (`repo_id`, `actor_id`) that are stable across renames. Prefer them over hashed surrogates for now, and write down that `repo_name` is *not* a key.

### Verify

- Every table above has a one-sentence grain statement you could read aloud.
- For each gold table, you can trace every column back to a JSON path in a raw record. If you cannot, you have invented a column with no source.
- You have written the answer to: "if I reprocess hour 2024-03-05T14 tomorrow, what changes in each table?" Do this now, in prose. Steps 9 and 13 will test whether you were right.

**Done when:** `docs/DATA_CONTRACT.md` is a document you would be willing to hand to another engineer as a build spec.

---

## Step 5 — Create Unity Catalog objects and land one file manually

**Goal:** the storage skeleton exists, and you have proven a file can get from your laptop into it.

### Implementation

1. In a Databricks SQL editor or notebook, create a catalog named `gh_archive`.
2. Inside it create four schemas: `raw`, `bronze`, `silver`, `gold`. Also create `gold_dev` — dbt will use it as your personal development target so you never develop against production tables.
3. Create a **managed volume** in the `raw` schema, named `gharchive_files`. Note its full path: `/Volumes/gh_archive/raw/gharchive_files/`.
4. Using the Databricks CLI's filesystem commands, upload the single `.json.gz` file you downloaded in Step 3 into your chosen path convention.
5. Open a serverless notebook. Read the file directly from the volume path using Spark's text reader and count the lines. Do not parse anything yet — you are only proving that Spark can see the bytes.
6. Compare that line count to the count you got with plain Python in Step 3. They must match exactly.

### Verify

- `SHOW SCHEMAS` in the catalog returns your five schemas.
- The CLI can list the file at its volume path and reports the same byte size as your local copy.
- Spark's line count equals your local Python line count. If it does not, you are almost certainly comparing a decompressed count to a compressed one, or Spark is silently reading more files than you think — print the input file paths to check.
- Reading a deliberately wrong volume path raises a clear error rather than returning zero rows. (Spark returning an empty DataFrame for a non-existent path is a real hazard; know which behavior you get.)

**Gotchas**

- Volume paths are `/Volumes/<catalog>/<schema>/<volume>/...`. Getting a level wrong yields confusing permission errors rather than "not found".
- Spark reads `.gz` transparently. Gzip is **not splittable**, so one file is processed by one task. With one file per hour this is fine; remember it when someone suggests one giant file.

**Done when:** a file you put there from your laptop is readable by Spark in the workspace, with a matching row count.

---

## Step 6 — The extract module: download one hour, well

**Goal:** a pure, unit-tested Python function that fetches one hour of GH Archive to local disk and is honest about failure.

### Implementation

1. In `ghwh/paths.py`, write a function that takes a UTC datetime (or a date and an integer hour) and returns the GH Archive URL. Handle the non-zero-padded hour. Write a second function returning the destination volume path per your Step 4 convention.
2. In `ghwh/extract.py`, write a function that downloads one hour to a caller-supplied local directory. Requirements:
   - **Stream to disk.** Never read the whole response into memory. Use the HTTP client's streaming interface and write in chunks.
   - **Write to a temporary filename, then atomically rename** on success. A crash mid-download must never leave a file that looks complete.
   - **Retry with exponential backoff** on connection errors and 5xx responses. Do not retry on 404.
   - **Raise a distinct, named exception for 404** (`SourceHourMissing` or similar) — Step 13 depends on being able to catch this specifically and treat it differently from a real failure.
   - Return a small result object: local path, byte count, HTTP status, and elapsed seconds.
3. Add a **verification step inside the download**: after writing, open the file with the gzip library and read the first and last line. A truncated `.gz` will fail here. Raise a distinct `CorruptDownload` exception. This is cheap and catches a genuinely common failure.
4. Add structured logging — the hour being fetched, bytes written, duration. Log at INFO. You will read these logs in Airflow later, so make them greppable.
5. Do **not** put Databricks, Airflow, or Spark imports in this module. It must be runnable from a plain REPL.

### Implementation — tests

In `tests/test_extract.py`, using `pytest` and a mocking library (`respx` for httpx, or `responses` for requests):

- URL construction for hours 0, 9, 10, and 23, asserting the zero-padding behavior.
- A successful download writes the expected bytes and returns the correct size.
- A 404 raises `SourceHourMissing` and leaves **no file on disk**.
- A 500 followed by a 200 succeeds after retry; three consecutive 500s raise.
- A truncated gzip body raises `CorruptDownload` and leaves no file behind.

### Verify

- All tests pass, and they run in under two seconds — because they hit no network.
- Actually download one real hour and confirm the byte count matches what `curl` reports.
- Download the same hour twice into the same directory. Decide and then *implement* the behavior you want: skip, or re-download and overwrite. Write the choice in `docs/DECISIONS.md`.
- Kill the process mid-download (Ctrl-C on a large file). Confirm no file with the final name exists in the directory afterward.

**Done when:** the "kill it halfway" test leaves your directory clean.

---

## Step 7 — The load module: land the file in the volume

**Goal:** get the local file into the Unity Catalog volume, immutably and verifiably.

### Implementation

1. In `ghwh/load.py`, write a function that uploads a local file to a volume path using the Databricks SDK's files API. It takes the local path and the destination volume path, and streams the upload.

2. Add an **existence check with a policy**. Raw is immutable, so decide: if the destination already exists, do you skip, or fail, or overwrite? Recommended for Stage 1: skip by default, with an explicit `overwrite` flag for reprocessing. Document it.

3. Add **integrity verification**: after upload, stat the remote object and compare its size to the local file's size. Mismatch raises. (A content hash is stronger; size is a reasonable Stage 1 compromise. Note the upgrade in `docs/DECISIONS.md`.)

4. Write a **landing manifest**. After a successful upload, append a record — source URL, volume path, byte size, event count if known, download duration, timestamp, run id — to a small Delta table `gh_archive.raw.landing_manifest`, or to a JSON sidecar file in the volume if writing a table from local Python is awkward. Prefer the Delta table; you will query it constantly.
   *Why:* this manifest is your answer to "did hour X ever land, and when?" without listing thousands of files. Every mature pipeline has one. Most tutorials omit it.

5. Write a `cleanup` function that deletes the local temp file after successful upload and manifest write, and *only* then.

### Verify

- Upload your Step 3 file. Confirm via the CLI that remote size equals local size.
- Query `landing_manifest` and see exactly one row.
- Run the same upload again. With default policy it should skip and not create a second manifest row. Then run with `overwrite=True` and confirm it does re-upload — and decide whether that writes a second manifest row or updates the first. (Recommended: append a new row. The manifest is an event log, not a state table.)
- Simulate a failure: point the upload at a volume path in a schema that does not exist. Confirm you get a clear error and that no manifest row is written. **The manifest must never claim something landed that did not.**
- Confirm the local temp file is gone after a successful run, and still present after a failed one.

**Done when:** `landing_manifest` is a trustworthy record of what is in your raw zone.

---

## Step 8 — First Spark job: raw file → bronze table

**Goal:** understand Spark by writing a real transformation, interactively, for one hour.

Work in a **Databricks notebook first**. Iterating in a notebook and refactoring to a script afterward is the normal professional workflow, not a shortcut.

### Implementation

1. Create a notebook attached to serverless compute. Read the volume file using Spark's **text** reader, producing a DataFrame with one string column, one row per JSON line.
2. Add a column that parses each line into a **VARIANT** using the `parse_json` SQL function. Name it `event`.
   - *Fallback:* if VARIANT is unavailable in your workspace, keep the line as a `STRING` column and use `from_json`/`get_json_object` for extraction. Note the substitution in `docs/DECISIONS.md`. Everything downstream still works.
3. Extract the promoted scalar columns from the VARIANT using `variant_get` (or the equivalent path syntax) at the JSON paths you recorded in Step 3. **Cast every one explicitly** — do not let Spark infer. Specifically: `event_id` to string, `created_at` to timestamp, `actor_id` and `repo_id` to bigint.
4. Derive `event_date` and `event_hour` **from the job's hour parameter, not from `created_at`**. This matters: GH Archive occasionally places an event in a neighbouring hour's file, and you need your partitions to correspond to *files you processed*, not to event timestamps, or reprocessing an hour will not fully replace what it wrote. Add a boolean column `created_at_matches_source_hour` so the discrepancy is visible rather than hidden.
5. Add the audit columns from Step 4. `_source_file` should come from Spark's `input_file_name` function so it is the truth rather than a variable you passed in.
6. Write the DataFrame to `gh_archive.bronze.events` as a Delta table partitioned by `event_date`. For this first pass use append mode; Step 9 fixes that.
7. **Explore what you built.** Count rows. Group by `event_type`. Pull one full VARIANT payload back and read it. Query a nested field directly out of the VARIANT with SQL to convince yourself the payload is genuinely queryable and you have lost nothing.
8. Look at the Spark UI for your job. Find the number of tasks in the read stage. Explain to yourself why it is 1. (Gzip is not splittable.) Then find where the shuffle happens, if any.

### Verify

- Bronze row count equals the line count from Steps 3 and 5. Exactly. Not approximately.
- `SELECT count(*) WHERE event_id IS NULL` returns 0.
- `SELECT count(DISTINCT event_id)` — note whether it is less than the total. If so, GH Archive has duplicates within a single hour, which is a real and known phenomenon. Record the number in `docs/DATA_CONTRACT.md`; silver will handle it.
- The distinct `event_type` values and counts match what you computed in plain Python in Step 3.
- `SELECT count(*) WHERE NOT created_at_matches_source_hour` — record this number. It is usually small and non-zero.
- `DESCRIBE DETAIL` on the table shows format Delta, one partition, and the file count. Note the file count; small-file accumulation is a Step 20 topic.
- Pick one specific `event_id` and trace it: find its line in the local raw file, and confirm every promoted column in bronze matches. Do this manually, once. It is the only way to know your extraction paths are right.

**Gotchas**

- Serverless runs **ANSI SQL by default**. A cast that would have silently produced NULL on older Spark will now raise. This is good; do not disable it.
- Serverless uses **Spark Connect**, which defers analysis until execution. Errors surface later than you expect. Do not conclude a transformation is correct because defining it did not error — call an action.

**Done when:** you have traced a single event end to end by hand and bronze's row count matches the source file exactly.

---

## Step 9 — Make bronze idempotent

**Goal:** running the same hour twice leaves the table exactly as it was after the first run. This is the single most important property in the whole project.

### Implementation

1. Understand the failure first. With your Step 8 append-mode job, **run the same hour a second time.** Observe the row count double. Do not skip this — feeling the bug is worth more than being told about it.
2. Change the write to use Delta's **`replaceWhere`** option with a predicate on `event_date` *and* `event_hour`. This makes the write an atomic "delete these rows and insert these rows" transaction.
   - Because `event_date` is the partition column but `event_hour` is not, this is a *data column* predicate, not just a partition predicate. Understand the difference: a partition-only predicate can be satisfied by dropping files; a data-column predicate requires Delta to rewrite files. Both are atomic. Look up the Delta configuration flag that controls data-column `replaceWhere` and confirm whether your runtime enables it by default.
   - Ensure your written DataFrame **cannot contain rows outside the predicate**, or the write will fail. This is Delta protecting you — do not work around it. It is exactly why Step 8 derives `event_date`/`event_hour` from the parameter and not from `created_at`.
3. Consider and then reject the alternatives, writing your reasoning in `docs/DECISIONS.md`:
   - `DELETE` then `INSERT` as two statements — **not atomic**; a crash between them leaves the hour missing.
   - `MERGE` on `event_id` — correct but far more expensive, and wrong for the semantics you want. Bronze's unit of truth is *the file*, not *the row*. If a source file is re-issued with fewer events, MERGE would leave the removed events behind; `replaceWhere` would not.
   - Full-table `overwrite` — correct and catastrophically expensive.
4. Add a guard: before writing, assert the DataFrame's distinct `(event_date, event_hour)` pairs number exactly one and equal the parameter. Fail fast with a clear message.

### Verify

- Run the same hour three times. Row count is identical after each run.
- Run a *different* hour on the same date. Row count increases by the second hour's count, and the first hour's rows are untouched.
- `DESCRIBE HISTORY` on the bronze table. Read the operation type and `operationMetrics` for each version. Confirm the second run's numbers show rows removed and rows added, not just added. This is Delta's transaction log, and being able to read it is a genuinely useful skill.
- Use Delta **time travel** to query the table as of the version before your second run and confirm the counts. You now have an undo button; know that you have it.
- Corrupt the guard test: manually construct a DataFrame containing two different hours and try to write it with a single-hour `replaceWhere`. Confirm it fails rather than silently writing.

**Done when:** you can run any hour any number of times, in any order, and the table is correct.

---

## Step 10 — Package the job as a parameterized Databricks Job

**Goal:** the same logic, running as a headless job triggered with an hour parameter — the thing Airflow will call.

### Implementation

1. Refactor the notebook into `jobs/bronze_ingest.py`. Structure:
   - An `argparse` (or `click`) interface taking `--source-date`, `--source-hour`, `--catalog`, and `--run-id`.
   - A `main()` that builds or acquires a Spark session, calls a pure-ish `build_bronze_df(spark, params)` function, and writes.
   - Keep transformation logic in functions that take a DataFrame and return a DataFrame. This makes them testable and readable.
2. **Get the code into the workspace.** Two options:
   - *Simplest:* use the Databricks CLI to import the file into a workspace path such as `/Workspace/Users/<you>/gh-warehouse/jobs/`. Add a small script or Makefile target that does this, so "deploy" is one command.
   - *Better, if it works on your account:* connect the workspace to your GitHub repo as a Git folder, so deployment is `git push` plus a pull in the workspace. Try this; fall back to the CLI import if it fights you.
3. Create a **Databricks Job** with a single `spark_python_task`, pointing at the workspace file, running on serverless, with **job parameters** for date, hour, catalog, and run id. Give the job a name you can find later.
4. Trigger the job manually from the UI with a specific hour. Then trigger it from the CLI with different parameters. Then trigger it from Python with the SDK. All three should work.
5. Add a top-level exception handler that logs the parameters it received before re-raising. Half of debugging a failed job is discovering it ran with parameters you did not expect.

### Verify

- The job succeeds for an hour you have already landed, and produces the same bronze result as the notebook did.
- Trigger it for the *same* hour again and confirm idempotency still holds through the job path.
- Trigger it for an hour whose raw file has **not** been landed. It should fail with a clear "input file missing" error, and it must **not** leave a partially written or emptied partition. Verify with `DESCRIBE HISTORY` that no new version was committed. (If Spark's reader returns an empty DataFrame instead of erroring, add an explicit existence check — this is a common and dangerous default.)
- In the job run page, find and read the driver logs. Confirm your parameter-logging line is there.
- Check your Free Edition job quota usage — you have a cap of 5 concurrent job tasks and daily compute limits.

**Done when:** you can run bronze ingestion for an arbitrary hour with a single CLI command, and a missing input fails safely.

---

## Step 11 — Stand up Airflow 3 locally and connect it to Databricks

**Goal:** a running local Airflow that can authenticate to your workspace.

### Implementation

1. Install the **Astro CLI** and initialize an Airflow project inside `airflow/`. It generates a `Dockerfile`, `requirements.txt`, `dags/`, `include/`, and `tests/`. Confirm the base image is Airflow 3.x.
   - *Alternative if you prefer no vendor CLI:* use the official Airflow Docker Compose file. It is more moving parts and more educational; it is also more to debug. Either is fine.
2. Add to `requirements.txt`: the Databricks provider package (`apache-airflow-providers-databricks`) and your own `ghwh` package. For `ghwh`, either build a wheel into `include/` and install it, or mount the source and install it editable via the Dockerfile. Restart Airflow so the image rebuilds.
3. Start Airflow. Log into the UI. **Read the interface before writing a DAG**: find the DAGs list, a DAG's grid view, the graph view, task logs, the Connections page, and the Variables page.
4. Create a **Databricks connection** in Airflow (Admin → Connections). Connection type Databricks, host = your workspace URL, and the token in the password/extra field as the provider expects. Do this via the UI first to see it work, then learn the environment-variable form of connections so it can be automated later.
5. Create Airflow **Variables** for your catalog name, volume root, and the Databricks job id from Step 10. Do not hardcode these in DAG files.
6. Write a throwaway DAG with one task that lists Databricks catalogs via the connection. Trigger it manually. Delete it once it works.

### Concepts to internalize before Step 12

Read the Airflow docs on these; the next step assumes them.

- **Logical date and data interval.** A DAG run scheduled `@hourly` for the interval starting 14:00 runs *after* 14:00 completes. `data_interval_start` is the hour you want to process. In Airflow 3, `execution_date` is gone — use `logical_date` and the data interval.
- **`catchup`.** Defaults to `False` in Airflow 3. Turning it on means Airflow will create runs for every missed interval since `start_date`. This is how you backfill, and it is also how you accidentally launch 8,000 runs.
- **Idempotent tasks.** Airflow retries. Your tasks must tolerate that — which is exactly why Steps 7 and 9 exist.
- **TaskFlow API.** Decorator-based tasks that pass values via XCom. Cleaner than classic operators for Python work.
- **XCom is for small metadata, not data.** Pass a path, never a DataFrame.

### Verify

- The Airflow UI is reachable and the scheduler is healthy (check the scheduler component's status in the UI).
- Your throwaway DAG succeeds and its task log shows the catalog list.
- Restart the whole stack. The connection and variables survive.
- In a DAG task, print `data_interval_start` and `data_interval_end` and confirm you understand which hour a given run "owns" before you rely on it.

**Gotchas**

- If your `ghwh` package imports fine locally but not in Airflow, it is not installed *in the image*. The Airflow container has its own environment.
- Airflow parses every file in `dags/` on a timer. Never put slow code, network calls, or heavy imports at module top level in a DAG file.

**Done when:** an Airflow task can reach Databricks using a stored connection, and you can explain what `data_interval_start` means.

---

## Step 12 — The hourly ingestion DAG

**Goal:** one DAG that lands and ingests exactly one hour per run.

### Implementation

1. Create `airflow/dags/gh_archive_ingest_hourly.py`. DAG-level configuration:
   - `schedule` hourly.
   - `start_date` set to the first hour of your chosen 7-day window.
   - `catchup=False` **for now** — you will enable it deliberately in Step 13.
   - `max_active_runs=1`. Free Edition's concurrency limits make parallel runs a bad idea, and serial runs are much easier to reason about while learning.
   - Sensible `retries` (2–3) with an exponential `retry_delay`.
   - Tags, an owner, and a docstring that renders in the UI.
2. Task 1 — **`resolve_hour`**: derive the source date and hour from `data_interval_start`. Return them as a small dict via XCom. Having this as a visible task, rather than inline templating, makes debugging enormously easier.
3. Task 2 — **`download`**: calls `ghwh.extract`. Downloads to a path under the container's temp directory that includes the run id, so concurrent or retried runs cannot collide. Returns the local path and byte count.
4. Task 3 — **`land_to_volume`**: calls `ghwh.load`. Uploads, verifies size, writes the manifest row, deletes the local file.
5. Task 4 — **`ingest_bronze`**: uses the Databricks provider's run-now operator against the job from Step 10, passing the date, hour, catalog, and the Airflow run id as job parameters. Configure it to poll until completion and to surface the Databricks run URL in the Airflow log.
6. Task 5 — **`log_completion`**: writes a summary line (hour, rows landed, duration). Trivial, but it gives you a single grep target per hour.
7. Set dependencies as a straight line. Resist branching until you need it.

### Verify

- Unpause the DAG and trigger a single run manually. All five tasks go green.
- Open the `ingest_bronze` task log, find the Databricks run URL, click through, and confirm the job page shows the parameters your DAG passed. Parameter passing is where these integrations break.
- Clear the `ingest_bronze` task and let it rerun. Bronze row count must not change. **This is the idempotency test running through the full orchestration path** — it is different from Step 9's test and it is the one that matters.
- Clear the *entire* DAG run and rerun from the start. The download re-runs, the upload skips (per your Step 7 policy), and bronze is unchanged.
- Break it on purpose: stop the Databricks warehouse, or revoke the token temporarily. Confirm the task fails, retries per your policy, and produces a log message that tells you what is wrong. Then fix it and clear the task.
- Confirm no temp files accumulate in the container across runs (exec into the scheduler/worker container and look).

**Done when:** a single hour flows from GH Archive to bronze with no manual intervention, and rerunning any task is safe.

---

## Step 13 — Backfill seven days and handle missing hours

**Goal:** 168 hours in bronze, and a documented policy for the hours that do not exist.

### Implementation

1. **Decide your missing-hour policy first, in writing.** GH Archive hours occasionally go missing entirely (HTTP 404) and files are occasionally truncated. Your options:
   
   - Fail the DAG run and require manual intervention.
   - Mark the hour as permanently missing in the manifest, skip downstream tasks, and let the run succeed.
   - Retry for a bounded window (the file sometimes appears late), then mark missing.
   
   Recommended: **retry on a bounded schedule, then record `status='missing'` in the manifest and skip downstream via Airflow's skip mechanism.** The pipeline must not be permanently red because of a source-side gap, but the gap must be *visible* rather than silently absent. Write the policy into `docs/OPERATIONS.md`.

2. Implement it: catch the `SourceHourMissing` exception from Step 6, write a manifest row with the missing status, and raise Airflow's skip exception so downstream tasks are marked skipped rather than failed. Note the visual difference in the grid view — skipped and failed look different for a reason.

3. Add `max_active_runs=1` if you have not already, and set `catchup=True`.

4. Run the backfill. Use the Airflow CLI's backfill command (or unpause with catchup on) for your 7-day window. Watch the grid view fill in.

5. **Watch your Databricks quota while this runs.** 168 job runs on Free Edition is not free of consequences. If you approach the daily limit, pause and resume tomorrow — and note in `docs/OPERATIONS.md` that backfills need rate limiting. This is a genuine production concern, not an artifact of the free tier.

6. Break one hour deliberately: pick a landed hour, delete its file from the volume, and clear that DAG run. Watch it fail, then recover it. Document the exact recovery steps in `docs/OPERATIONS.md`. This is your first real runbook entry.

### Verify

- Query bronze: `SELECT event_date, count(DISTINCT event_hour), count(*) FROM bronze.events GROUP BY 1 ORDER BY 1`. You should see 7 dates and, for each, 24 hours minus any genuinely missing ones.
- Cross-check against the manifest: every hour in your window has a manifest row, with a status of landed or missing. **Zero hours should be absent from the manifest entirely.** An hour you never attempted is far more dangerous than an hour you know failed.
- Write a query that returns the missing hours by generating the expected 168-hour sequence and left-joining the manifest. Save it in `docs/OPERATIONS.md` as a description of what to compute — this is your completeness check and you will run it constantly.
- Plot or list events per hour across the week. You should see a clear daily and weekday/weekend cycle. A flat line means something is wrong; a hour with 10× its neighbours means a duplicate load.
- Total bronze row count should be within a plausible range of (mean hourly count × hours landed). A large discrepancy needs investigating before you continue.
- `DESCRIBE HISTORY` should show roughly one write version per hour processed, not several — several means retries wrote repeatedly, which is fine but worth understanding.

**Done when:** you have a complete, verified 7-day window and a written recovery procedure you have actually executed.

---

## Step 14 — A bronze data quality gate

**Goal:** the pipeline detects its own bad data instead of passing it downstream.

### Implementation

1. Create `jobs/bronze_quality_check.py`, a Databricks job task taking the same hour parameters. It runs assertions and **fails the task** when they break. Checks:
   - **Volume:** the hour's row count is within a tolerance band of the trailing median for the same hour-of-day over the past week. Wide bands (say, 50%–200%) to start; tighten later. This catches partial loads.
   - **Completeness:** `event_id`, `event_type`, `created_at`, `repo_id` are non-null in 100% of rows.
   - **Validity:** every `event_type` is in a known allow-list. New types appearing is a *warning*, not a failure — GitHub adds event types, and you want to be told, not blocked.
   - **Timeliness:** the share of rows where `created_at_matches_source_hour` is false is below a threshold.
   - **Uniqueness (informational):** duplicate `event_id` count for the hour, recorded but not failed on. Bronze does not deduplicate.
2. **Write results to a table**, `gh_archive.bronze.quality_results`, one row per check per hour: check name, status, observed value, threshold, timestamp. Do this even for passing checks. A history of passing checks is what makes a threshold tunable.
3. Distinguish **warn** from **fail** explicitly. A check that can only fail will get its threshold loosened until it never fires. A check that can warn stays useful.
4. Add the check as a task in the hourly DAG, downstream of `ingest_bronze`.

### Verify

- Run the check against a known-good hour. All checks pass and rows appear in `quality_results`.
- Manufacture a failure: temporarily lower the volume threshold so a normal hour breaches it. Confirm the task fails, the DAG run goes red, and a row with status `fail` is written. **The result row must be written even when the check fails** — a quality system that records nothing on failure is useless.
- Manufacture a warning: add a fake event type to a test copy of the data, or drop one from the allow-list. Confirm it warns and does not fail.
- Confirm the check is idempotent: run it twice for the same hour and decide whether you get two result rows or one updated row. Either is defensible; the choice must be deliberate.
- Query `quality_results` across your whole backfill and confirm you have a complete grid of check × hour.

**Done when:** you can answer "was hour X clean?" with a single query, for every hour in your window.

---

## Step 15 — Silver: typed, deduplicated, and schema-drift-aware

**Goal:** turn faithful-but-messy bronze into tables you would actually join.

### Implementation

1. Create `jobs/silver_build.py`, parameterized by **date** (silver runs daily, not hourly — a deliberate change of cadence, and a good thing to notice).
2. **`silver.events`** — one row per distinct event:
   - Read bronze for the date.
   - Deduplicate on `event_id` using a window function ordered deterministically (by `_ingested_at`, then `_source_file`) so reruns produce identical output. **A non-deterministic dedup is a bug that only appears on rerun**; make the ordering total.
   - Cast and validate types. Rows failing validation go to `silver.events_quarantine` with a reason column, **not to the bit bucket**. Being able to answer "what did we throw away?" is the point.
   - Write with `replaceWhere` on `event_date`. Same idempotency lesson, one level up.
3. **`silver.pull_request_events`** — one row per `PullRequestEvent`:
   - Filter bronze by type, then extract typed columns from the VARIANT: PR number, PR id, action (`opened`/`closed`/`reopened`), PR created-at, PR merged-at, PR author login and id, base repo id and name, additions, deletions, changed files, and the draft flag.
   - Where an expected path is absent, produce NULL — but **count how often** each path is missing and write those counts to a `silver.extraction_stats` table. That table *is* your schema drift monitor. If a field's null rate jumps from 0% to 100% on a given date, GitHub changed something and you will know the exact day.
4. **`silver.pull_request_review_events`** — one row per `PullRequestReviewEvent`: review id, review state (`approved`/`changes_requested`/`commented`), submitted-at, reviewer login and id, PR number, PR id, repo id. Consider whether `PullRequestReviewCommentEvent` also counts as "a review" for your metric; **decide, and document the decision** — it materially changes the answer.
5. **Handle skew.** Group bronze by `repo_id` for one date and look at the distribution. A handful of repos will have orders of magnitude more events than the rest. In the Spark UI for your silver job, find whether any single task takes far longer than the others. If so, read about salting and adaptive query execution, and write what you find in `docs/DECISIONS.md` — even if the fix is "not needed at this volume." Knowing why you didn't need it is the lesson.
6. Add the silver job as a task in a new **daily** DAG, `gh_warehouse_daily`. Its first task should be a **readiness check**: query bronze and confirm all 24 hours of the target date are present and passed quality. If not, fail with a message naming the missing hours. Do not build silver on incomplete bronze.

### Verify

- `silver.events` row count = `SELECT count(DISTINCT event_id)` from bronze for that date. Exactly.
- Run the silver job twice for the same date. All silver row counts are unchanged.
- Quarantine table row count plus silver row count accounts for every distinct bronze event. Nothing vanished.
- Sum of the type-specific tables' counts is less than `silver.events` (you only extracted a few types), and each equals the corresponding bronze count for that type minus duplicates.
- Trace one PR through: pick a `PullRequestEvent` with action `opened`, find its raw JSON line, and confirm every extracted column. Then find the corresponding review events for the same PR number and repo. If you cannot find any, pick a different PR — but confirm you *can* find at least one PR with both an open and a review inside your window, because Step 18 depends on it.
- Query `extraction_stats` and confirm null rates are stable across your seven days.

**Done when:** silver reproduces exactly on rerun and nothing is discarded without a record.

---

## Step 16 — dbt against Databricks: setup and staging models

**Goal:** a working dbt project connected to your warehouse, with a build that runs green.

### Implementation

1. In your project virtual environment (or a separate one), install `dbt-core` 1.12.x and `dbt-databricks` 1.12.x.

2. Initialize a dbt project in `dbt/`. Configure `profiles.yml` with a Databricks connection: host, HTTP path of your SQL warehouse, token, catalog `gh_archive`, and schema `gold_dev`. **Keep `profiles.yml` outside the repo** (the default `~/.dbt/` location) or template it from environment variables. Never commit a token.

3. Add a `prod` target in the same profile pointing at schema `gold`. You now have dev/prod separation from day one, which is the correct habit.

4. Test the connection with dbt's debug command. Fix it before writing a single model.

5. Configure `dbt_project.yml`: project name, model paths, and per-directory materializations — `staging` as views, `marts` as tables.

6. Define **sources** in a `sources.yml` pointing at your silver tables. Add `freshness` configuration based on the silver tables' timestamp columns. Sources are how dbt knows where the warehouse ends and the lake begins; do not skip them and reference tables directly.

7. Build **staging models**, one per source table, named `stg_gh__events`, `stg_gh__pull_request_events`, `stg_gh__pull_request_review_events`. Staging models should do exactly four things and nothing else:
   
   - Select from exactly one source.
   - Rename columns to your naming convention (pick one — `snake_case`, `_id` suffix for keys, `_at` suffix for timestamps — and write it in `docs/DATA_CONTRACT.md`).
   - Cast types.
   - Light, non-destructive cleanup (trimming, lowercasing logins for join safety).
   
   No joins. No aggregation. No business logic. This discipline is what makes a dbt project maintainable, and violating it is the most common dbt mistake.

8. Add a `schema.yml` beside the staging models with a description for every model and column, plus `not_null` and `unique` tests on each primary key.

9. Run `dbt build` (which runs models and tests together — prefer it over `run` followed by `test`).

### Verify

- `dbt debug` reports a successful connection.
- `dbt build` completes with zero errors and zero test failures.
- Query one staging view directly in Databricks SQL and confirm its row count matches the underlying silver table.
- Check that the views were created in `gold_dev`, not `gold`. If they landed in `gold`, your target is wrong and you would have overwritten production.
- Run `dbt docs generate` and serve the docs. Explore the lineage graph. Confirm your sources appear as source nodes, distinct from models.
- Deliberately break a test: add a `unique` test to a column you know has duplicates. Confirm `dbt build` fails and tells you the row count that violated it. Then remove it.
- Run `dbt compile` and read the generated SQL in `target/`. Understanding what dbt actually sends to the warehouse demystifies the whole tool.

**Done when:** `dbt build` is green, docs render, and you have read the compiled SQL for at least one model.

---

## Step 17 — The dimensional layer

**Goal:** conformed dimensions and a fact table, with tests that would catch a bad join.

### Implementation

1. **`dim_date`** — one row per calendar date across your window plus generous padding. Columns: date key, year, quarter, month, ISO week, day of week, weekday/weekend flag. Build it from a generated date sequence, not from your event data — a date dimension that only contains dates you have events for will silently drop rows from time-series reports.
2. **`dim_repo`** — one row per repository. Key: `repo_id`. Attributes: current `repo_name`, owner login, first-seen and last-seen timestamps within your window. Type 1 per Step 4. Add a column `distinct_names_seen` counting how many different names this `repo_id` has had — it makes the renaming problem, and your Type 1 trade-off, visible in the data.
3. **`dim_actor`** — one row per GitHub actor. Key: `actor_id`. Attributes: current login, first-seen and last-seen timestamps, and a `first_seen_in_window` date. Add an `is_likely_bot` flag using a login-suffix heuristic (`[bot]` and similar). **Bots are a large share of GitHub events and will wreck your latency metric if you ignore them.** Document the heuristic and its known imprecision.
4. **`fct_pull_request_activity`** — one row per PR-related event. Foreign keys to the three dimensions. Degenerate dimensions: PR number, PR id, action, review state. Measures: additions, deletions, changed files. Materialize as a table.
5. Materialize dims as tables. Do not bother with incremental models yet — at 7 days of data, full refresh is fast, and incremental logic is a whole category of bugs you do not need while learning. Note in `docs/DECISIONS.md` that this is a deliberate deferral to Stage 2.
6. Add tests in `schema.yml`:
   - `unique` and `not_null` on every dimension key.
   - `relationships` tests from each fact foreign key to its dimension. **This is the test that catches broken joins**, and it is the one beginners skip.
   - `accepted_values` on `action` and `review_state`.
   - `not_null` on the fact's date key.
7. Add one **singular test** (a SQL file in `tests/` that should return zero rows): assert no PR has a review event whose timestamp precedes the PR's own creation timestamp. If it returns rows, you have either a data problem or a join problem — and you want to know which before you build the mart on top.

### Verify

- `dbt build` green, including all relationship tests.
- Fact row count equals the sum of the relevant silver tables' row counts. If it is lower, your joins to dimensions are dropping rows — find out why before continuing. This is the classic fan/chasm trap and it is worth hitting once.
- `SELECT count(*) FROM fct WHERE repo_key IS NULL` returns 0.
- The top 10 repos by fact row count are recognizable, plausible, large open-source projects. If your top repo is something odd, investigate.
- The bot flag: count events by `is_likely_bot`. Look at the top 20 actor logins overall and confirm the flag is catching the obvious ones.
- Break a relationship on purpose: temporarily filter one repo out of `dim_repo`, rebuild, and confirm the relationships test fails and names the orphaned key. Then revert.
- Regenerate docs and confirm the lineage graph shows source → staging → dim/fact with no unexpected edges.

**Done when:** every foreign key in your fact resolves, and you have seen a relationship test fail on purpose.

---

## Step 18 — The first mart: PR review latency

**Goal:** answer the project question, honestly, including about its own limitations.

### Implementation

1. Build `int_pull_request_first_review` in an `intermediate` directory. Grain: one row per (repo, PR number). Logic:
   - Find the `opened` event for each PR from the fact table. That gives PR open time and author.
   - Find the **earliest** review event for the same (repo id, PR number) that occurs at or after the open time.
   - Compute `hours_to_first_review` as the difference.
   - Handle PRs with no review in the window: keep them, with a NULL latency and a `has_review` boolean. **Dropping them would bias your metric downward — the slowest PRs are exactly the ones without a review yet.** This is survivorship bias and it is the most common way this metric gets computed wrong.
   - Add a `censored` flag for PRs opened near the end of your window that simply have not had time to be reviewed. Right-censoring is real and you must at minimum flag it.
2. Build `mart_pr_review_latency`. Grain: one row per (repo, week, first-seen-in-window flag). Measures: PR count, reviewed count, median and 90th-percentile `hours_to_first_review`, and share reviewed within 24 hours.
   - Use **median, not mean.** The distribution has a long tail and a mean will be dominated by one abandoned PR.
   - Exclude bot-authored PRs by default; expose the flag so it can be included.
   - Join `is_first_seen_in_window` from `dim_actor` for the newcomer split.
3. Write `docs/KNOWN_LIMITATIONS.md` covering, at minimum: the 7-day window makes "first-time contributor" a proxy that is wrong for most people; right-censoring inflates the reviewed-share and deflates latency; the review-event definition choice from Step 15; bot detection is heuristic; and events for a PR opened before your window are invisible so those PRs are absent entirely.
4. Add tests: latency is never negative; percentiles are non-null wherever `reviewed_count > 0`; the mart's PR count reconciles to the intermediate model's.

### Verify

- Query the mart. Look at the numbers and ask whether they are *plausible* — a median first-review latency measured in hours-to-a-few-days is believable; a median of 4 seconds or 400 days is a bug.
- Pick the single repo with the most PRs. Manually verify three of its PRs end to end: find the open event in silver, find the review events, compute the latency by hand, and compare to the mart. **Do this. Every automated check can pass on wrong logic.**
- Count PRs with no review. Compute what share that is. Confirm the censored flag concentrates in the final days of your window — if censored PRs are evenly spread, your flag logic is wrong.
- Compare newcomer vs. established latency. Note the direction of the difference and whether the sample size makes it meaningful. Resist drawing a conclusion from 7 days of data — and write down *why* you are resisting.
- `dbt build` green including the new singular tests.

**Done when:** you have hand-verified three PRs against the mart and written down why you do not yet trust the headline number.

---

## Step 19 — Orchestrate dbt from Airflow and run the whole thing

**Goal:** one command, one schedule, raw file to mart.

### Implementation

1. Make dbt available inside the Airflow image: add `dbt-core` and `dbt-databricks` to the Airflow `requirements.txt`, and make the dbt project directory available to the container (mount it or copy it in the Dockerfile). Be aware that dbt and Airflow have historically had dependency conflicts; if resolution fights you, the standard escape hatch is to run dbt in its own container or virtualenv. Note whichever you choose in `docs/DECISIONS.md`.
2. Supply the dbt profile via environment variables rather than a checked-in file, with the Databricks token pulled from the Airflow connection.
3. Add to the daily DAG `gh_warehouse_daily`, in order:
   - `check_bronze_complete` (from Step 15)
   - `build_silver`
   - `silver_quality_check`
   - `dbt_build` — a single task running `dbt build` with the `prod` target
   - `post_build_checks` — a handful of SQL assertions against the marts
4. Configure `dbt_build`'s failure behaviour: on failure, the task must surface which model or test failed in the Airflow log, not just a non-zero exit code. Make sure dbt's output is being captured.
5. *Optional but worth knowing about:* `astronomer-cosmos` renders each dbt model as its own Airflow task, giving per-model retries and a real lineage view in the Airflow graph. It is the better production pattern. Do it as a Stage 2 upgrade, once the single-task version works — one new tool at a time.
6. **The full end-to-end test.** Pick a date outside your existing window. Enable both DAGs. Let the hourly DAG land all 24 hours, then let the daily DAG run. Do not intervene.

### Verify

- The new date appears in bronze (24 hours), silver, the fact table, and the mart, with no manual steps.
- Total elapsed wall-clock time from first hourly run to mart availability — write it down. This is your pipeline's latency and it is a number you should always know.
- Rerun the entire daily DAG for a date already processed. Every downstream table is unchanged. This is idempotency at the whole-pipeline level and it is the real prize.
- Break the chain: delete one hour from bronze and rerun the daily DAG. `check_bronze_complete` must fail and name the missing hour, and silver must not be rebuilt from incomplete data.
- Make a dbt test fail on purpose (drop a row from a dimension). Confirm the DAG goes red and the Airflow log names the failing test.
- Check the Databricks jobs page: the number of runs should match the number of DAG tasks that invoked jobs. Reconciling orchestrator and platform is a routine debugging move.

**Done when:** a date you have never touched flows all the way to the mart while you watch, and rerunning it changes nothing.

---

## Step 20 — Operate it, then write down what you learned

**Goal:** turn a project into something maintainable, and capture the knowledge before you forget it.

### Implementation

1. **Finish `docs/OPERATIONS.md`.** It should contain, in the form of instructions someone else could follow at 2 a.m.:
   - How to backfill a range of hours, and how to rate-limit that backfill against quota.
   - How to reprocess a single hour after correcting a bug.
   - How to recover from: a 404 hour, a corrupt download, an expired token, a failed dbt test, a quota shutdown.
   - The completeness query from Step 13 and the quality query from Step 14.
   - How to read `DESCRIBE HISTORY` and how to time-travel a table back after a bad write.
2. **Table maintenance.** Run `OPTIMIZE` on bronze and check the file count before and after with `DESCRIBE DETAIL`. Notice how many small files 168 hourly writes produced, and understand why that matters for read performance. Read about `VACUUM` and its retention interaction with time travel — then decide your retention policy and write it down. **Do not run `VACUUM` with a short retention while you are still learning to time-travel.**
3. **Cost and quota review.** Look at how much compute the 7-day backfill consumed against your Free Edition allowance. Estimate what a full 2011–present backfill would cost at that rate. This number will shape all of Stage 2 — it is likely to be the reason Stage 2 uses the BigQuery public dataset for history rather than replaying every file.
4. **Reliability drill.** Pause everything for 48 hours. Come back, unpause, and let catchup fill the gap. Confirm it recovers without manual intervention. This is the most realistic test in the entire run book.
5. **Write a retro** in `docs/STAGE1_RETRO.md`: what took longer than expected, what you got wrong the first time, what you would design differently, and the three things you now understand that you did not before Step 1.
6. **Tag the repo** `stage-1-complete`.

### Verify — Stage 1 definition of done

Every box must be true:

- [ ] 7+ consecutive days of GH Archive data in bronze, with a manifest row for every hour including missing ones
- [ ] Bronze, silver, and the full dbt build are each idempotent — verified by rerunning, not by assumption
- [ ] A missing source hour causes a skip, not a permanent failure, and is visible in the manifest
- [ ] A quality check failure fails the pipeline and is recorded in `quality_results`
- [ ] `dbt build` is green including relationship tests and at least one singular test
- [ ] `mart_pr_review_latency` returns plausible numbers, hand-verified against raw JSON for three PRs
- [ ] `docs/` contains DATA_CONTRACT, OPERATIONS, DECISIONS, KNOWN_LIMITATIONS, and STAGE1_RETRO
- [ ] A brand-new date flows end to end with zero manual steps
- [ ] Unit tests pass and run without network access
- [ ] Nothing secret is in git history

**Done when:** you could hand the repo to another engineer and they could operate it from the docs alone.

---

## What Stage 2 will be (preview only — do not start it yet)

Written here so you can stop yourself from doing it early:

1. **History.** Backfill months or years, using the BigQuery public dataset where replaying files is uneconomic. Handle the pre-2015 schema as a genuinely separate source with its own parser.
2. **Incremental models.** Convert the dbt marts to incremental materializations and learn the failure modes: late-arriving data, the `is_incremental` trap, full-refresh discipline.
3. **The remaining three questions.** Contributor retention (needs the long history), bus factor / concentration, and project trajectory.
4. **Type 2 dimensions.** Track repository renames and actor login changes properly.
5. **Cosmos, or per-model Airflow tasks.** Real lineage in the orchestrator.
6. **CI/CD.** Tests and `dbt build` against a dev schema on every pull request. Databricks Asset Bundles for job deployment.
7. **Observability.** SLAs, freshness alerting, an elementary-style anomaly monitor on the marts.
8. **Deliberate breakage.** Let it run for a month. Do not fix it immediately when it breaks. Read the logs cold and find out whether the observability you built is actually enough.

That last one is the real curriculum. Stage 1 built the pipeline; Stage 3 is where operating it teaches you the rest.
