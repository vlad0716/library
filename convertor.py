import sqlite3
import json
import pandas as pd

# Load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Create SQLite database and table
def create_table(conn, table_name, columns):
    cursor = conn.cursor()
    columns_with_types = ', '.join([f"{col} TEXT" for col in columns])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_with_types});")
    conn.commit()

# Insert JSON data into table
def insert_data(conn, table_name, data):
    cursor = conn.cursor()
    cols = ', '.join(data[0].keys())
    placeholders = ', '.join(['?' for _ in data[0].keys()])
    cursor.executemany(f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})", 
                       [tuple(item.values()) for item in data])
    conn.commit()

def main():
    json_file_path = 'authors.json'  # Path to your JSON file
    db_file_path = 'db.sqlite3'      # Path to your SQLite database file
    table_name = 'books_author'       # Name of the table

    # Load JSON data
    data = load_json(json_file_path)

    # Connect to SQLite database
    conn = sqlite3.connect(db_file_path)

    # Create table
    if isinstance(data, list) and len(data) > 0:
        columns = data[0].keys()  # Assuming all dicts have the same keys
        create_table(conn, table_name, columns)

        # Insert data into table
        insert_data(conn, table_name, data)
    else:
        print('JSON data is not in expected list of dictionaries format.')

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()