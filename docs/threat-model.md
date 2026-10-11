# Threat model: before and after the security hardening

**System:** a Python CLI used by manufacturers, suppliers and viewers to manage a prepared-meals supply chain, backed by MySQL (tables, triggers, stored procedures).

**Assets:** inventory and lot data (food-safety relevant: expiry, recalls, ingredient conflicts), supplier pricing, user accounts, and the audit trail.

**Actors:** legitimate users of each role; a user trying to act beyond their role; someone with access to a terminal running the app; someone who obtains a leaked config file or database credential.

## Findings in the original code and what changed

| # | Threat (STRIDE) | Before | After |
|---|---|---|---|
| 1 | **Spoofing**: log in as anyone | Login asked only for a user ID, with no password. Any ID gave that role's access. | bcrypt-hashed passwords (cost 12, min 12 chars). Users with no password set cannot log in. |
| 2 | **Spoofing / elevation**: unknown user | `ViewFactory` fell through to the Viewer menu for any unrecognised role, so a mistyped or invented ID still got read access. | Fail closed: unknown roles raise `PermissionError`. Login only returns a role for a verified user. |
| 3 | **Spoofing**: password guessing | Not applicable (no passwords). | 5 consecutive failures lock the account for 15 minutes. Locking is done in one atomic `UPDATE`. |
| 4 | **Information disclosure**: user enumeration | Not applicable. | Same message and similar timing for unknown user, wrong password and locked account (a dummy bcrypt check runs on the unknown-user path). |
| 5 | **Elevation of privilege**: database access | The app connected as MySQL `root`, so any bug in the app had full control of the server. | Four least-privilege accounts. `inv_auth` can only read login columns of `User`, update lockout columns and append to `Audit_Log`. Each role account has `EXECUTE` on only its menu's procedures and `SELECT` on only the tables its screens read. **No account can INSERT/UPDATE/DELETE any table directly**: writes go through stored procedures (SQL SECURITY DEFINER), which keep the business rules. |
| 6 | **Tampering**: SQL injection | Most queries were parameterised, but `DBUtils.get_data_from_table` built SQL from its table name and WHERE-clause arguments with f-strings. | Removed (it was unused), along with `process_order`, which called procedures that don't exist. |
| 7 | **Tampering / elevation**: code execution | `ProductBatchRepository` ran `eval()` on dates read from the database. This also corrupted the display (`2026-11-10` evaluated to `2005`). | Values used directly. A test fails the build if `eval`/`exec` appear anywhere in `src/`. |
| 8 | **Information disclosure**: secrets in config | The root password lived in `config/config.yaml`. | Passwords come only from environment variables or a gitignored `.env`. `config.yaml` holds only host, port and database name. |
| 9 | **Repudiation**: no record of who did what | None. | Append-only `Audit_Log`: triggers record every insert/update to inventory, products, recipes and supplier pricing, with the app user (`@app_user`) and the database account. The login flow records every success, failure and lockout. `UPDATE`/`DELETE` on the log are rejected by triggers, even for admins. |
| 10 | **Denial of service / integrity**: data wipe on start | Every app launch dropped and recreated all tables and reloaded seed data. | Schema setup moved to `python src/manage.py init-db`. The app never changes the schema. |
| 11 | **Integrity**: broken on Linux | The login query used `user` while the table is `User` (works only on case-insensitive macOS/Windows). Seed data had hard-coded dates that had expired, so the 90-day expiry trigger rejected it. | Table name fixed. Seed dates are relative to the setup date. |

## Verified by tests (`tests/`, run against a real MySQL/MariaDB)
- correct, wrong, unknown and password-less logins; lockout after 5 failures blocks even the correct password; success resets the counter; every attempt is audited
- each role can read its tables and run its procedures; no role can read `User` or `Audit_Log`, write any table, `DROP` anything, or run another role's procedures
- the login account cannot read names, change roles or overwrite password hashes
- a supplier's write is logged with `app_user = SUP020` and `db_account = inv_supplier@…`
- business rules still hold through the procedures (90-day ingredient expiry)
- `Audit_Log` rejects `UPDATE`/`DELETE` even from the admin account
- static check: the grants exactly match the procedures and tables each role's screens use (view → service → repository call graph), and no `eval`/`exec` in the source

## Remaining risks (not addressed)
- **Row-level authorisation:** a manufacturer account can call `CreateProductBatch` with another manufacturer's ID. The app always passes the logged-in user's own ID, but the database does not enforce ownership. A fix would pass `@app_user` into the procedures and check ownership there.
- **Admin account:** `manage.py` uses an admin account (root in Docker). Stored procedures run as their definer, so that account must keep existing. A dedicated schema-owner account would be tighter.
- **Transport:** TLS between app and database relies on the server's defaults (MySQL 8 enables TLS automatically). Not enforced with `REQUIRE SSL`.
- **Password reset** is admin-only (`manage.py set-password`). There's no self-service change or expiry.
- **Audit log** is append-only at the row level, but an admin can still `DROP` or `TRUNCATE` the table. Shipping logs off the database server would close that gap.
