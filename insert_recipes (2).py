import json
import math
import numpy as np
import pandas as pd
import pyodbc

DB_CONFIG = {
    "server": "LAPTOP-1PSD1NEO",   # your local SQL Server instance
    "database": "recipe",          # your database name
    "driver": "{ODBC Driver 17 for SQL Server}",
}

JSON_FILE = r"D:\pavitra project\US_recipes.json"
BAD_RECORDS_FILE = r"D:\pavitra project\bad_records.csv"

def get_connection():
    return pyodbc.connect(
        f"DRIVER={DB_CONFIG['driver']};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection=yes;"
    )


def clean_numeric(val, as_int=False):
    """Clean numeric values, handle NaN/inf, cast if needed"""
    try:
        if val in (None, "", "null", "NaN", "nan"):
            return None
        num = float(val)
        if math.isnan(num) or math.isinf(num):
            return None
        return int(num) if as_int else num
    except:
        return None

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='recipe' AND xtype='U')
    CREATE TABLE recipe (
        id INT IDENTITY(1,1) PRIMARY KEY,
        cuisine NVARCHAR(255),
        title NVARCHAR(255),
        rating FLOAT NULL,
        prep_time INT NULL,
        cook_time INT NULL,
        total_time INT NULL,
        description NVARCHAR(MAX),
        nutrients NVARCHAR(MAX),
        serves NVARCHAR(100)
    )
    """)
    conn.commit()
    conn.close()

def insert_data():
    # Load JSON into pandas DataFrame
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient="index")

    total_json_records = len(df)
    print(f" JSON contains {total_json_records} records.")

    
    df["rating"] = df["rating"].apply(lambda x: clean_numeric(x, as_int=False))
    df["prep_time"] = df["prep_time"].apply(lambda x: clean_numeric(x, as_int=True))
    df["cook_time"] = df["cook_time"].apply(lambda x: clean_numeric(x, as_int=True))
    df["total_time"] = df["total_time"].apply(lambda x: clean_numeric(x, as_int=True))

    
    df["nutrients"] = df["nutrients"].apply(
        lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, dict) else "{}"
    )

    
    df = df.replace({np.nan: None})

    
    valid_cols = [
        "cuisine", "title", "rating", "prep_time", "cook_time",
        "total_time", "description", "nutrients", "serves"
    ]
    df = df[valid_cols]

    
    records = [tuple(row) for row in df.to_numpy()]

    conn = get_connection()
    cursor = conn.cursor()
    cursor.fast_executemany = True

    inserted = 0
    bad_rows = []

    for i, row in enumerate(records):
        try:
            cursor.execute("""
                INSERT INTO recipe (cuisine, title, rating, prep_time, cook_time, total_time, description, nutrients, serves)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, row)
            inserted += 1
        except Exception as e:
            print(f" Error inserting record index={i}: {e}")
            bad_rows.append(dict(zip(valid_cols, row)))

    conn.commit()
    conn.close()

    print(f" Inserted {inserted} records into DB.")
    print(f" Failed records: {len(bad_rows)}")

    # Save failed records to CSV
    if bad_rows:
        pd.DataFrame(bad_rows).to_csv(BAD_RECORDS_FILE, index=False, encoding="utf-8")
        print(f" Bad records saved to {BAD_RECORDS_FILE}")


if __name__ == "__main__":
    init_db()
    insert_data()

