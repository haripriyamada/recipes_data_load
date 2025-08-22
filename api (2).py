import json
import pyodbc
from flask import Flask, request, jsonify, send_from_directory
import os

# ---------------- DB CONFIG ----------------
DB_CONFIG = {
    "server": "LAPTOP-1PSD1NEO",
    "database": "recipe",
    "driver": "{ODBC Driver 17 for SQL Server}",
}

# ---------------- Connection ----------------
def get_connection():
    return pyodbc.connect(
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection=yes;"
    )

# ---------------- Flask App ----------------
app = Flask(__name__, static_folder="frontend")

# ---------- Serve Frontend ----------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)

# ---------- API Endpoint 1: Paginated Recipes ----------
@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    page = int(request.args.get("page", 1))
    limit = int(request.args.get("limit", 10))
    offset = (page - 1) * limit

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM recipe")
    total = cursor.fetchone()[0]

    cursor.execute("""
        SELECT id, title, cuisine, rating, prep_time, cook_time, total_time, description, nutrients, serves
        FROM recipe ORDER BY rating DESC
        OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
    """, (offset, limit))

    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "title": row.title,
            "cuisine": row.cuisine,
            "rating": row.rating,
            "prep_time": row.prep_time,
            "cook_time": row.cook_time,
            "total_time": row.total_time,
            "description": row.description,
            "nutrients": json.loads(row.nutrients) if row.nutrients else {},
            "serves": row.serves
        })

    return jsonify({"page": page, "limit": limit, "total": total, "data": data})

# ---------- API Endpoint 2: Search Recipes ----------
@app.route("/api/recipes/search", methods=["GET"])
def search_recipes():
    title = request.args.get("title")
    cuisine = request.args.get("cuisine")
    rating = request.args.get("rating")
    total_time = request.args.get("total_time")
    calories = request.args.get("calories")

    query = """SELECT id, title, cuisine, rating, prep_time, cook_time, total_time, description, nutrients, serves 
               FROM recipe WHERE 1=1"""
    params = []

    if title:
        query += " AND title LIKE ?"
        params.append(f"%{title}%")
    if cuisine:
        query += " AND cuisine LIKE ?"
        params.append(f"%{cuisine}%")
    if rating:
        op = rating[:2] if len(rating) > 1 and rating[1] in "=<>" else rating[0]
        val = float(rating[len(op):])
        query += f" AND rating {op} ?"
        params.append(val)
    if total_time:
        op = total_time[:2] if len(total_time) > 1 and total_time[1] in "=<>" else total_time[0]
        val = int(total_time[len(op):])
        query += f" AND total_time {op} ?"
        params.append(val)
    if calories:
        op = calories[:2] if len(calories) > 1 and calories[1] in "=<>" else calories[0]
        val = int(calories[len(op):])
        query += f" AND TRY_CAST(JSON_VALUE(nutrients, '$.calories') AS INT) {op} ?"
        params.append(val)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    data = []
    for row in rows:
        data.append({
            "id": row.id,
            "title": row.title,
            "cuisine": row.cuisine,
            "rating": row.rating,
            "prep_time": row.prep_time,
            "cook_time": row.cook_time,
            "total_time": row.total_time,
            "description": row.description,
            "nutrients": json.loads(row.nutrients) if row.nutrients else {},
            "serves": row.serves
        })

    return jsonify({"data": data})

# ---------------- Main Runner ----------------
if __name__ == "__main__":
    # Check frontend exists before running
    print("Looking for frontend at:", os.path.join(os.getcwd(), "frontend", "index.html"))
    app.run(debug=True, port=5000)
