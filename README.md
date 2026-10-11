# Inventory Management System — Security-Hardened (Python + MySQL)

Role-based inventory system for a prepared-meals supply chain (manufacturers, suppliers, viewers), built on MySQL triggers and stored procedures: lot numbering, 90-day expiry enforcement, batch costing, transitive recall tracing and ingredient-incompatibility checks.

This fork adds a **security-hardening pass**: password authentication with lockout, database-enforced least privilege per role, an append-only audit trail, removal of injection and `eval` risks, and a test suite that checks all of it against a real database.

## Background
Originally a team project for NC State CSC 540 (Database Management Systems). Team: Sameeksha Keshav, Bestin Lalu, Cole Sauerbrei, Arnav Yennam.
The security hardening, tests, Docker setup and threat model in this repository are my own additions.

## Security changes (summary)
Full before/after analysis: [`docs/threat-model.md`](docs/threat-model.md).

| Area | Before | After |
|---|---|---|
| Login | user ID only, no password | bcrypt passwords, lockout after 5 failures, no user enumeration, every attempt audited |
| Unknown role | fell through to Viewer access | denied (fail closed) |
| Database account | app ran as MySQL `root` | 4 least-privilege accounts. Roles can only `EXECUTE` their own procedures and `SELECT` the tables they read, with **no direct writes** |
| Injection / code execution | f-string SQL helper; `eval()` on database values | removed. A test blocks `eval`/`exec` |
| Secrets | root password in `config.yaml` | environment variables / gitignored `.env` |
| Accountability | none | append-only `Audit_Log` via triggers (who, which DB account, what changed) |
| Startup | every launch wiped and re-seeded the database | setup is a separate `manage.py init-db` command |
| Portability | broken on Linux (table-name case, expired seed dates) | fixed |

## How least privilege works
```
login ──► inv_auth          SELECT login columns of User · UPDATE lockout columns · INSERT Audit_Log
            │ verified role
            ▼
 MANUFACTURER ──► inv_manufacturer   EXECUTE 7 procedures · SELECT 8 tables
 SUPPLIER     ──► inv_supplier       EXECUTE 4 procedures · SELECT 3 tables
 VIEWER       ──► inv_viewer         EXECUTE 8 procedures · SELECT 4 tables
                         │
                         ▼
            stored procedures (SQL SECURITY DEFINER) ──► tables + business-rule triggers
                                                    └──► audit triggers ──► Audit_Log (append-only)
```
The grants live in [`src/security/privileges.py`](src/security/privileges.py). A test derives each role's procedures and tables from the view → service → repository call graph and fails if the grants drift from what the screens actually use.

## Running

### Docker (MySQL 8.4)
```bash
cp .env.example .env                      # change every password
docker compose up -d db
docker compose run --rm app python src/manage.py init-db
docker compose run --rm app               # log in
docker compose run --rm app python -m pytest -q   # tests (they reset the database)
```

### Local MySQL / MariaDB
```bash
pip install -r requirements.txt
cp .env.example .env                      # admin + app account passwords
cp config/config.example.yaml config/config.yaml
python src/manage.py init-db              # prints a random initial password per user (or set DEMO_USER_PASSWORD)
python src/app.py
```

### Admin commands
```bash
python src/manage.py set-password MFG001
python src/manage.py unlock MFG001
python src/manage.py audit --limit 20
```

## Tests
`python -m pytest -q`: 27 tests covering authentication and lockout, database privilege enforcement per role, audit logging, append-only audit trail, business rules through procedures, the grants/call-graph match, and the no-`eval` rule. They run against a real database and **reset it**, so use a test instance.

Tested on MySQL 8.4 (Docker) and MariaDB 10.11: all 27 tests pass on both.

## Features (original system)
- **Manufacturer:** define products and recipes, create product batches (consumes ingredient lots, checks expiry and incompatibilities, computes cost), reports (on-hand, nearly out of stock, almost expired), recall tracing.
- **Supplier:** define atomic/compound ingredients and formulations, manage supplied ingredients, create ingredient batches (90-day minimum shelf life).
- **Viewer:** browse products, flattened ingredient lists, product incompatibility comparison, supplier spend, batch unit cost.

## Layout
```
data/                 schema, procedures, business-rule triggers, audit triggers, seed data
src/app.py            CLI entry point (login, then role menu)
src/manage.py         admin: init-db, set-password, unlock, audit
src/security/         password hashing, per-role grants
src/service/LoginService.py   authentication + lockout
tests/                integration and static security tests
docs/threat-model.md  STRIDE before/after, remaining risks
```

## Roadmap
- [x] Password authentication, lockout, fail-closed roles
- [x] Least-privilege database accounts; no direct table writes
- [x] Append-only audit log
- [x] Remove f-string SQL and `eval`; secrets out of config
- [x] Docker Compose, test suite, threat model
- [ ] Row-level ownership checks inside procedures (see remaining risks)
- [ ] Indexes + `EXPLAIN` before/after on report queries
