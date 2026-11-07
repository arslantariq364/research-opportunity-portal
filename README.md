# Research Opportunity Portal

A Flask application for creating, listing, updating, closing, and deleting university research opportunities. The project has a small frontend dashboard and a REST API backed by SQLAlchemy.

## Repository layout

- `backend/`: Flask application, models, routes, validation, and dependency file.
- `frontend/`: HTML, CSS, and JavaScript dashboard.
- `database/schema.sql`: MySQL schema.
- `postman/`: Postman collection and usage notes.
- `tests/`: backend, frontend, and collection-runner tests.

## Local setup

The application is configured for MySQL through the variables in `.env.example`.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp .env.example .env
python backend/app.py
```

Open `http://127.0.0.1:5000/portal` after configuring a reachable MySQL database and applying `database/schema.sql`.

## Tests

Run the Python tests with:

```bash
python -m pytest tests -v
```

The frontend regression and Postman runner scripts have additional browser/collection requirements. Test counts and results can change; run the commands above for the current status.
