import database
import os
import sqlite3

# Use a temporary database for testing
database.DB_FILE = "test_id_sequence.db"

# Clean up previous test run
if os.path.exists(database.DB_FILE):
    os.remove(database.DB_FILE)

database.init_database()

print("Creating Problem 1...")
id1 = database.create_problem("Problem 1")
print(f"Problem 1 ID: {id1}")

print("Creating Problem 2...")
id2 = database.create_problem("Problem 2")
print(f"Problem 2 ID: {id2}")

print("Creating Problem 3...")
id3 = database.create_problem("Problem 3")
print(f"Problem 3 ID: {id3}")

print("Deleting Problem 3...")
with database.get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("DELETE FROM problems WHERE id = ?", (id3,))
    conn.commit()

print("Creating Problem 4 (Should be ID 3)...")
id4 = database.create_problem("Problem 4")
print(f"Problem 4 ID: {id4}")

if id4 == 3:
    print("SUCCESS: ID sequence logic works correctly.")
else:
    print(f"FAILURE: Expected ID 3, got {id4}")

# Clean up
if os.path.exists(database.DB_FILE):
    os.remove(database.DB_FILE)
