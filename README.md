# Student Activity Tracker

Mini full-stack project: **React (Vite) + Axios** frontend, **Flask + SQLite** backend.

## Run it

### 1. Backend (terminal 1)
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py                  # http://127.0.0.1:5000
```

### 2. Frontend (terminal 2)
```bash
cd frontend
npm install
npm run dev                    # http://localhost:5173
```

### 3. Tests (optional)
```bash
cd backend
python -m pytest -q
```

## API

| Method | URL | Description | Success |
|---|---|---|---|
| POST | `/activities` | Body: `{"name","activity","hours"}` | 201 + created record |
| GET | `/activities` | All activities, newest first | 200 + list |
| GET | `/summary` | `total_entries`, `total_hours`, `most_active_user` | 200 |
| DELETE | `/activities/<id>` | Delete one (bonus) | 200 / 404 |

Errors always return JSON: `400` validation (with per-field `details`), `404` not found,
`405` wrong method, `500` unexpected error.

Validation rules: `name` and `activity` must be non-empty strings; `hours` must be a
number greater than 0 and at most 24 (booleans and numeric strings are rejected).

## Design decisions (good for the interview)

- **Most active user** = student with the most *total hours* (names compared
  case-insensitively; ties broken alphabetically so the result is stable).
- **SQLite** (Python's built-in `sqlite3`) with parameterised queries, so there is no SQL injection risk.
- **Tests** swap `DB_NAME` for a temporary file, so they never touch your real data.
- **Validation twice**: in React for fast feedback, and in Flask because the server must never trust the client.
- **CORS** enabled with `flask-cors` because React (port 5173) and Flask (port 5000) are different origins.
- **React hooks**: `useState` for data/loading/error state, `useEffect` to load data once when the page opens.
- The list and summary are both reloaded after every add/delete so the screen always matches the database.

## Structure
```
backend/   app.py, requirements.txt, tests/test_api.py
frontend/  src/api.js (Axios calls), App.jsx, components/{ActivityForm,ActivityList,Summary}.jsx
```
