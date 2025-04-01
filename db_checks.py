import sqlite3
from contextlib import contextmanager

# Database connection manager
@contextmanager
def get_db_connection():
    conn = sqlite3.connect("test_datas.db")
    conn.row_factory = sqlite3.Row  # Dictionary-like access
    try:
        yield conn
    finally:
        conn.close()

def initialize_database():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                test_id TEXT PRIMARY KEY,
                answers TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()



def add_test(test_id, answers):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO tests (test_id, answers, created_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (test_id.strip(), answers.strip().upper())
            )
            conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error adding test: {e}")
        return False

def get_test(test_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT answers FROM tests WHERE test_id=?",
                (test_id.strip(),)
            )
            result = cursor.fetchone()
            return result['answers'] if result else None
    except sqlite3.Error as e:
        print(f"Error getting test: {e}")
        return None

def delete_test(test_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM tests WHERE test_id=?",
                (test_id.strip(),)
            )
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting test: {e}")
        return False

def get_all_tests():
    """ Barcha testlarni ID va javoblari bilan olish """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT test_id, answers, created_at FROM tests order by created_at desc")
            results = cursor.fetchall()
            return [{"test_id": row["test_id"], "answers": row["answers"], "created_at": row["created_at"]} for row in results]
    except sqlite3.Error as e:
        print(f"Error fetching all tests: {e}")
        return []

# Initialize database when module is imported
initialize_database()