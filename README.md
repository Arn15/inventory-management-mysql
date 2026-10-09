# Inventory Management System (Python + MySQL)

Role-based inventory system for a prepared-meals supply chain (manufacturers, suppliers, viewers), built on MySQL triggers, stored procedures and views: lot numbering, expiry enforcement, batch costing, transitive recall tracing and ingredient-incompatibility checks.

> **Status:** being extended with a security-hardening pass. See planned work.

## Background
Originally a team project for NC State CSC 540 (Database Management Systems). Team: Sameeksha Keshav, Bestin Lalu, Cole Sauerbrei, Arnav Yennam.
This repository is my independent copy and extension of that work.

## Planned work (this repo)
- [ ] Real authentication: password column, argon2/bcrypt hashing, lockout after failed attempts
- [ ] Least-privilege MySQL users per role (no `root`); EXECUTE on procedures + only required tables
- [ ] Whitelist dynamic table names in `DBUtils`; confirm all queries are parameterized
- [ ] Audit-log triggers on batch, inventory and recall changes
- [ ] Credentials from environment variables; Docker Compose for one-command setup
- [ ] pytest tests for triggers and procedures (expiry rule, recall trace)
- [ ] Indexes + `EXPLAIN` before/after on report queries
- [ ] Threat model (before vs. after) in `docs/`

## Setup
```bash
pip install -r requirements.txt
cp config/config.example.yaml config/config.yaml   # fill in DB settings
python src/app.py
```
