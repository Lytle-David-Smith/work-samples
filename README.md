# Work Samples — Lytle David Smith

Senior healthcare data analyst · SQL · Power Query / Power BI · Reporting architecture
Louisville, KY · [linkedin.com/in/lytledavidsmith](https://linkedin.com/in/lytledavidsmith)

Everything here is my own work: personal tools built on my own time, or utilities built on
public CMS data. No employer code or data appears in this repository. All code follows a
written formatting standard I maintain (see `Example Code by Lytle David Smith.sql` for the
annotated version) — when you inherit my work, it all reads the same.

---

## LDS+N — Excel add-in

**Start here: [LDS+N Quick Tour.pdf](LDS%2BN%20Quick%20Tour.pdf)** — an illustrated
walkthrough of the add-in in action, written for any reader, technical or not.
`LDS+N Sample Data.xlsx` is the workbook used throughout the tour, so every step can be
reproduced, and `LDS+N.xlam` is the compiled add-in itself for hands-on evaluation
(after downloading, right-click → Properties → Unblock before opening).

**What it is:** A 5,000+ line VBA add-in (22 modules) that streamlines working with the wide
tables Power Query delivers into Excel.

**The problem it solves:** Power Query hands you correct data in an unreadable state — dozens
of columns, no formatting, no way to inspect a single record. Analysts lose time re-formatting
the same tables after every refresh and scrolling sideways to read one row.

**What to notice:**
- *Format Table Columns* — one keystroke applies data-type-aware formatting and widths to an
  entire table, with a persistent cache so each column is only ever configured once.
- *Row Viewer* — a live panel showing every field of the current row vertically; follows the
  cursor as you move, so wide tables become readable.
- *Formula Report* — audits an entire workbook's formulas, external references, and errors
  into one table, collapsing filled ranges into single canonical findings. Built for assessing
  inherited reporting workbooks.
- For the technically inclined: class-based selection history (browser-style back/forward),
  an application-level event sentinel driving the modeless viewer, DPI-aware programmatic
  form generation, and ribbon integration.

## Power Query (M) function library (`fn*.m`)

**What it is:** Reusable M functions that speed development of reporting solutions.

**The problem it solves:** Power Query connects to server data read-only — you can pull data
down, but you can't push a local filter list up. `fnSQLSelectFromValues` generates type-aware
SQL from local Excel data so a spreadsheet-driven population can filter a server-side query
with no write access, no staging tables, and no engineering ticket. Implemented for three
dialects — T-SQL, MySQL, and DuckDB — because the pattern proved useful across three
different employers' database engines.

**Also here:**
- `fnQueryProfile_ServerSideSQL` — generates per-column profiling SQL that runs on the
  server, so exploring a new table doesn't mean dragging it into Excel first.
- `fnUnzipContents` — parses ZIP file binary structure in pure M (no external tools).
- `fnAddGroupIndexColumn`, `fnStack`, `fnSQL_Indent`, and other development utilities.

## SQL Server search utilities

**What they are:** Two SSMS template-parameter scripts for finding things in unfamiliar
databases — the first job on every new engagement.

- `Search Database.sql` — searches schema, table, view, synonym, column, and module names,
  and module source code, in one pass (Azure SQL compatible).
- `Search Table Data.sql` — searches for a *value* across specified columns and tables
  (adapted from a public query by Reto Egeter, credited in the header).

## NPPES pipeline

**What it is:** Databricks notebooks that download the current NPPES provider file from the
public CMS site, extract and load it, and build normalized dimension views — plus an Excel
workbook (`CMS NPPES API Example.xlsx`) demonstrating the NPPES API called live from
Power Query.

**Why it's here:** Acquisition → extraction → loading → normalized presentation of a healthcare
data source, end to end. NPPES is public data, so the full pipeline can be shown and run.

## Code standard (`Example Code by Lytle David Smith.sql`)

An annotated exemplar of the SQL formatting standard used throughout this repository:
element-per-line construction, leading commas, vertical alignment of like elements, CTEs over
nested subqueries. The point is maintainability — code written to be inherited.

`CodeFormatter.py` — a Notepad++ Python plugin that tokenizes SQL and M and applies this
standard automatically; the exemplar describes the rules, the formatter enforces them.

---

*Assembled August 2026. The add-in and library are in active use; questions and walkthrough
requests welcome.*

© Lytle David Smith. Shared for professional review; all rights reserved.
No license is granted for reuse or redistribution — contact me if you'd like to use something here.
