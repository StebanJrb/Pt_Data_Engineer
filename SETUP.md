# SETUP

Steps to get the project running from scratch.

## 1. Clone the repository

```bash
git clone <repository-url>
cd PT_DataEngineer_Tp
```

## 2. Create and activate the virtual environment

```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/Mac
source env/bin/activate
# Windows 
.\env\Scripts\activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

You also need the **ODBC Driver 17 for SQL Server** installed at the
operating-system level (used by `pyodbc`/`mssql-django` to connect); it is
not installed via pip.

## 4. Configure environment variables

Copy `.env.example` to `.env` and fill in the real credentials:

```bash
cp .env.example .env
```

Variables expected by `DPDO/settings.py` (read with `python-dotenv` +
`os.getenv`):

- `DB_NAME`: database name (defaults to `dpdo`).
- `DB_USER`: SQL Server login the application will use.
- `DB_PASSWORD`: password for that login.
- `DB_HOST`: SQL Server host or instance (e.g. `localhost` or `localhost\SQLEXPRESS`).
- `DB_PORT`: SQL Server port (defaults to `1433`).

## 5. Create the schema in SQL Server

Run the scripts in `SQL_Scripts/` against the SQL Server instance, in this
order (for example from SSMS or `sqlcmd`):

1. `SQL_Scripts/dpdo.sql` — creates the `dpdo` database, its tables and indexes.
2. `SQL_Scripts/populate_database.sql` — seed data (positions, cities,
   categories, event, employees, sample registrations and results).
3. `SQL_Scripts/stored_procedures.sql` — creates `sp_GetCategoryWinners` and
   `sp_GetRegistrationStatistics`.

## 6. Grant permissions on the stored procedures

The user configured in `DB_USER` needs explicit execute permission on the
stored procedures — without it, the API responds with
`EXECUTE permission was denied on the object...`. As sysadmin/`sa`, run:

```sql
GRANT EXECUTE ON sp_GetCategoryWinners TO actual_user_name;
GRANT EXECUTE ON sp_GetRegistrationStatistics TO actual_user_name;
```

(This same `GRANT` is included, commented out, at the end of
`SQL_Scripts/stored_procedures.sql` as a reference.)

> **Note on the driver:** the connection to SQL Server is made with `pyodbc`
> through `mssql-django`. Calls to the stored procedures
> (`DPDO_API/procedures.py`) use a parametrized `EXEC`
> (`cursor.execute("EXEC sp_Name @Param = %s", [...])`), **not**
> `cursor.callproc()`, because `pyodbc` does not support it with this driver.

## 7. Grant permissions for the automated tests

`python manage.py test` runs against a real, disposable SQL Server database
(`test_dpdo` by default) — **not** SQLite or a mock. Django creates that
database itself before the suite runs and drops it afterwards, which
requires the `DB_USER` login to hold the `dbcreator` server role. As
`sysadmin`/`sa`, run:

```sql
ALTER SERVER ROLE dbcreator ADD MEMBER actual_user_name;
```

Whoever creates a database in SQL Server automatically becomes its owner, so
once `test_dpdo` is created the same login already has full rights inside
it — no additional `GRANT` is needed there. `DPDO_API/test_runner.py` then
recreates the tables from `dpdo.sql` and the two stored procedures from
`stored_procedures.sql` inside `test_dpdo` right after Django creates it, so
the whole suite (including the winners/statistics endpoints) runs against
real T-SQL objects on the real engine — the production `dpdo` database
itself is never touched by the tests.

This is a separate permission from the `GRANT EXECUTE` in step 6, which
covers the real `dpdo` database used by `runserver`.

## 8. Run the server

```bash
python manage.py runserver
```

The API is then available under `http://127.0.0.1:8000/api/` (see
README.md for the endpoint details).

## 9. Run the automated tests

```bash
python manage.py test DPDO_API -v 2
```

All 19 tests run against real SQL Server (see step 7) — no SQLite, no
mocked stored procedures. `DatabaseConnectionTest` additionally opens its
own direct connection to the real `dpdo` database (using the exact
`.env` credentials) as a plain connectivity sanity check, separate from the
disposable `test_dpdo` database the rest of the suite uses.

Add `--keepdb` to reuse `test_dpdo` across runs instead of recreating it
every time (faster); the custom test runner re-creates any missing table or
procedure either way, and each test still runs inside a rolled-back
transaction, so leftover data never leaks between runs.
