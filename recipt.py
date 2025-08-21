import json
import pyodbc
import math
import logging


logging.basicConfig(
    filename="recipe_insert_log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def clean_number(value, as_float=False, force_int=False):
    
    try:
        if value is None:
            return None
        if isinstance(value, float) and math.isnan(value):
            return None
        if isinstance(value, str):
            val = value.strip().lower().replace("&", "").replace(" ", "")
            if val in ["nan", "null", "none", "", "n/a"]:
                return None
            try:
                num = float(val)
                if force_int:  # for SQL INT columns
                    return int(num)
                return num if as_float else int(num)
            except ValueError:
                return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            if force_int:
                return int(value)
            return value if as_float else int(value)
        return None
    except Exception:
        return None

def insert_data():
    file_path = r"D:\US_recipes.json"

    # Load JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        recipes = json.load(f)

    # Connect to SQL Server
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        r"SERVER=LAPTOP-9ESPNM04\SQLExpress;"
        "DATABASE=Recipesdatabse;"
        "Trusted_Connection=yes;"
    )
    cursor = conn.cursor()

    for key, rec in recipes.items():
        cuisine = rec.get("cuisine")
        title = rec.get("title")
        rating = clean_number(rec.get("rating"), as_float=True)          
        prep_time = clean_number(rec.get("prep_time"), force_int=True)    
        cook_time = clean_number(rec.get("cook_time"), force_int=True)   
        total_time = clean_number(rec.get("total_time"), force_int=True) 
        description = rec.get("description")
        nutrients = json.dumps(rec.get("nutrients"), ensure_ascii=False) 
        serves = rec.get("serves") 

        try:
            cursor.execute("""
                INSERT INTO Recipes (
                    cuisine, title, rating, prep_time, cook_time, total_time, description, nutrients, serves
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cuisine, title, rating, prep_time, cook_time, total_time, description, nutrients, serves))

            logging.info(f"Inserted recipe {key}: {title}")

        except Exception as e:
            logging.error(f"Failed to insert recipe {key}: {e}\nData: {rec}")

    conn.commit()
    conn.close()
    print(" Data insertion complete )")

if __name__ == "__main__":
    insert_data()
