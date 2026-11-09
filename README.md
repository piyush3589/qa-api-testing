# API Test Automation (Python + Pytest)

Automated REST API test suite for the public [JSONPlaceholder](https://jsonplaceholder.typicode.com) API.
Built to show practical QA automation skills: Pytest, `requests`, parametrized tests, JSON-schema
contract checks, negative testing, an offline mock server and CI with GitHub Actions.

## What is covered

| Area | Examples |
|---|---|
| **GET** | list sizes, single resource, unique IDs, filtering with query params, nested routes (`/posts/1/comments`) |
| **POST / PUT / PATCH / DELETE** | status codes, response body, partial vs full update |
| **Negative cases** | missing IDs (404), non-numeric ID, filters with no match (empty list), update on missing resource |
| **Contract testing** | every response validated against JSON Schemas (`schemas.py`) |
| **Consistency** | nested route equals query route, all posts of a user reference that user |

35 tests across `tests/test_posts.py`, `tests/test_users.py`, `tests/test_comments.py`.

## Project structure

```
conftest.py          # fixtures: base_url, shared requests session (with timeout)
schemas.py           # JSON Schemas for post / comment / user
tests/               # test modules
mock_server/server.py# offline stand-in for the API (stdlib only)
.github/workflows/   # CI: runs the suite on every push
```

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

pytest                      # against the live JSONPlaceholder API
pytest --mock               # offline, against the bundled mock server
pytest --base-url https://your-api.example.com
pytest --mock --html=report.html --self-contained-html   # HTML report
pytest -k "posts and not delete"                         # run a subset
```

## Design notes

- **Mock mode** keeps CI fast and stable (no dependency on a third-party server). The live run is for
  checking the real API.
- **JSONPlaceholder does not persist writes** and does not validate input. Tests for POST/PUT/PATCH/DELETE
  assert the documented fake responses, and `test_create_post_with_empty_body_still_gets_id` documents
  the missing validation on purpose.
- Add a new endpoint test by adding a function in `tests/` and, if needed, a schema in `schemas.py`.

## Possible next steps

- Playwright UI test for a demo site
- Allure reports
- Run the suite against a staging URL via the `BASE_URL` environment variable
