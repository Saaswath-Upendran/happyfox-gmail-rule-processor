\# Gmail Rules Processor





Standalone Python scripts to:

1\) Authenticate to Gmail via OAuth and fetch Inbox emails

2\) Persist them to a relational DB (PostgreSQL by default)

3\) Process emails against JSON-configured rules (string and date predicates)

4\) Perform Gmail actions (mark read/unread, move/label) via REST API





\## Prereqs

\- Python 3.9+

\- PostgreSQL 13+

\- Google Cloud project with OAuth 2.0 Client ID (Desktop App); download `credentials.json`





\## Setup

```bash

python -m venv .venv \&\& source .venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

\# Put credentials.json in repo root or set GOOGLE\_CREDENTIALS\_PATH

createdb gmail\_rules # or use your own DB and update .env
