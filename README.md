# RollForVibes
monorepo for daggerheart campaign utilities.

## Session attribute backend

`session-attribute-service` is a FastAPI + SQLAlchemy app that stores session metadata and per-session JSONB attributes in PostgreSQL. It provides:

- `POST /api/sessions`, `GET /api/sessions`, `GET /api/sessions/{id}` for session records.
- `GET /api/sessions/{id}/attributes`, `POST /api/sessions/{id}/attributes` for reading/upserting key/value pairs scoped to one session.

## Recording service

`recording-service` interfaces with the Google Docs + Drive APIs to create shared documents for session recordings. It offers:

- `POST /api/recordings` (input: `session_id`, `title`, optional `summary`) to produce a new document, set its permissions to `anyone with link`, and persist the doc metadata (`doc_id`, `doc_url`) in PostgreSQL.
- `GET /api/recordings` and `GET /api/recordings/session/{session_id}` to discover existing recording URLs.

## Running locally

`dockercompose.yml` now includes:

- `postgres` configured with database `rollforvibes` and credentials `rfv_user` / `rfv_pass`.
- `session-attribute-service` depending on `postgres` and listening on port `8000`.
- `recording-service` depending on `postgres`, listening on port `9000`, and expecting Google service account credentials.
- The existing `calendar-integration-service` and `frontend` services remain unchanged.

Before starting the stack, provide the following environment variables so each service can reach the database and the Docs API:

- `DATABASE_URL=postgresql://rfv_user:rfv_pass@postgres:5432/rollforvibes`
- `GOOGLE_SERVICE_ACCOUNT_FILE` (or `GOOGLE_SERVICE_ACCOUNT_INFO`) pointing to a Google service account key JSON that has `docs` and `drive` scopes. You can mount the credentials inside the container (for example, `- ./secrets/google-service-account.json:/run/secrets/google-service-account.json:ro`) and set `GOOGLE_SERVICE_ACCOUNT_FILE=/run/secrets/google-service-account.json`.

Then run:

```
docker compose up
```

The session attribute and recording services will create their tables on startup and begin talking to Postgres.
