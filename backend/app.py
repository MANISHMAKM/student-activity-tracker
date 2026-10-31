import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # React runs on a different port, so we need CORS

DB_NAME = "activities.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # lets us use row["name"] instead of row[1]
    return conn


def create_table():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            activity TEXT NOT NULL,
            hours REAL NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def clean_number(value):
    # show 2 instead of 2.0, but keep 1.5 as it is
    value = round(value, 2)
    if value == int(value):
        return int(value)
    return value


def row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "activity": row["activity"],
        "hours": clean_number(row["hours"]),
    }


def validate_activity(data):
    """Check the data sent by the user. Returns a dict of errors (empty if all good)."""
    errors = {}

    if not isinstance(data, dict):
        errors["body"] = "Send a JSON object with name, activity and hours."
        return errors

    name = data.get("name")
    activity = data.get("activity")
    hours = data.get("hours")

    if not isinstance(name, str) or name.strip() == "":
        errors["name"] = "Name is required."
    elif len(name.strip()) > 100:
        errors["name"] = "Name must be 100 characters or less."

    if not isinstance(activity, str) or activity.strip() == "":
        errors["activity"] = "Activity is required."
    elif len(activity.strip()) > 200:
        errors["activity"] = "Activity must be 200 characters or less."

    # True/False are also numbers in Python, so we block them separately
    if isinstance(hours, bool) or not isinstance(hours, (int, float)):
        errors["hours"] = "Hours must be a number."
    elif hours <= 0:
        errors["hours"] = "Hours must be greater than 0."
    elif hours > 24:
        errors["hours"] = "Hours cannot be more than 24."

    return errors


@app.route("/")
def home():
    return jsonify({"message": "Student Activity Tracker API is running"})


# POST /activities -> add a new activity
@app.route("/activities", methods=["POST"])
def add_activity():
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    errors = validate_activity(data)
    if errors:
        return jsonify({"error": "Validation failed.", "details": errors}), 400

    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO activities (name, activity, hours) VALUES (?, ?, ?)",
        (data["name"].strip(), data["activity"].strip(), data["hours"]),
    )
    conn.commit()
    new_row = conn.execute(
        "SELECT * FROM activities WHERE id = ?", (cursor.lastrowid,)
    ).fetchone()
    conn.close()

    return jsonify(row_to_dict(new_row)), 201


# GET /activities -> get all activities (latest first)
@app.route("/activities", methods=["GET"])
def get_activities():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM activities ORDER BY id DESC").fetchall()
    conn.close()

    return jsonify([row_to_dict(row) for row in rows]), 200


# GET /summary -> total entries, total hours, most active user
@app.route("/summary", methods=["GET"])
def get_summary():
    conn = get_connection()

    totals = conn.execute(
        "SELECT COUNT(*) AS entries, COALESCE(SUM(hours), 0) AS hours FROM activities"
    ).fetchone()

    # the most active user is the one with the most total hours
    top_user = conn.execute(
        """
        SELECT MIN(name) AS name, SUM(hours) AS total_hours
        FROM activities
        GROUP BY LOWER(name)
        ORDER BY total_hours DESC, LOWER(name) ASC
        LIMIT 1
        """
    ).fetchone()
    conn.close()

    summary = {
        "total_entries": totals["entries"],
        "total_hours": clean_number(totals["hours"]),
        "most_active_user": None,
        "most_active_user_hours": 0,
    }
    if top_user is not None:
        summary["most_active_user"] = top_user["name"]
        summary["most_active_user_hours"] = clean_number(top_user["total_hours"])

    return jsonify(summary), 200


# DELETE /activities/<id> -> delete one activity (bonus)
@app.route("/activities/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    conn = get_connection()
    cursor = conn.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
    conn.commit()
    conn.close()

    if cursor.rowcount == 0:
        return jsonify({"error": "Activity not found."}), 404

    return jsonify({"message": "Activity deleted.", "id": activity_id}), 200


# Error handlers, so the API always replies with JSON (not HTML pages)
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found."}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed."}), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Something went wrong on the server."}), 500


if __name__ == "__main__":
    create_table()
    app.run(debug=True, port=5000)
