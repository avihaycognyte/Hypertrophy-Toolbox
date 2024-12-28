from utils.config import DB_FILE
import sqlite3


class DatabaseHandler:
    """
    Handles low-level database operations with context management.
    """

    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.connection = sqlite3.connect(DB_FILE)
        self.connection.row_factory = sqlite3.Row  # Return results as dictionaries
        self.cursor = self.connection.cursor()
        self.connection.execute("PRAGMA journal_mode=WAL;")  # Enable Write-Ahead Logging (WAL) mode

    def execute_query(self, query, params=None):
        """
        Executes a query with optional parameters.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            print(f"Query executed successfully: {query} | Params: {params}")
        except sqlite3.Error as e:
            print(f"Database error during query execution: {e} | Query: {query} | Params: {params}")
            raise e

    def fetch_all(self, query, params=None):
        """
        Fetch all rows for a query.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: List of all rows fetched as dictionaries.
        """
        try:
            if not isinstance(params, (list, tuple)) and params is not None:
                params = [params]  # Convert single parameter to list
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            results = self.cursor.fetchall()
            return [dict(row) for row in results] if results else []
        except sqlite3.Error as e:
            print(f"Database error: {e} | Query: {query} | Params: {params}")
            raise e

    def fetch_one(self, query, params=None):
        """
        Fetch a single row for a query.
        :param query: SQL query to execute.
        :param params: Optional parameters for parameterized queries.
        :return: Single row fetched as a dictionary.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            result = self.cursor.fetchone()
            print(f"Fetch one successful: {query} | Params: {params}")
            return dict(result) if result else None
        except sqlite3.Error as e:
            print(f"Database fetch error: {e} | Query: {query} | Params: {params}")
            raise e

    def close(self):
        """
        Close the database connection.
        """
        self.connection.close()
        print("Database connection closed.")

    def __enter__(self):
        """
        Context management entry.
        :return: The instance itself for use in `with` statements.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context management exit.
        Automatically closes the database connection.
        """
        self.close()

    def get_exercise_details(self, exercise_name):
        query = """
        SELECT 
            primary_muscle_group,
            secondary_muscle_group,
            tertiary_muscle_group,
            advanced_isolated_muscles,
            utility,
            grips,
            stabilizers,
            synergists
        FROM exercises 
        WHERE exercise_name = ?
        """

def initialize_database():
    """Initialize the database with necessary tables."""
    schema_queries = [
        # Drop existing tables
        "DROP TABLE IF EXISTS user_selection;",
        "DROP TABLE IF EXISTS workout_log;",
        "DROP TABLE IF EXISTS exercises;",
        
        # Create exercises table
        """
        CREATE TABLE exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT UNIQUE NOT NULL,
            primary_muscle_group TEXT,
            secondary_muscle_group TEXT,
            tertiary_muscle_group TEXT,
            advanced_isolated_muscles TEXT,
            utility TEXT,
            grips TEXT,
            stabilizers TEXT,
            synergists TEXT,
            force TEXT,
            equipment TEXT,
            mechanic TEXT,
            difficulty TEXT
        );
        """,
        
        # Create user_selection table without UNIQUE constraint
        """
        CREATE TABLE user_selection (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            routine TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            min_rep_range INTEGER NOT NULL,
            max_rep_range INTEGER NOT NULL,
            rir INTEGER DEFAULT 0,
            weight REAL NOT NULL,
            FOREIGN KEY (exercise) REFERENCES exercises(exercise_name)
        );
        """
    ]

    with DatabaseHandler() as db_handler:
        for query in schema_queries:
            try:
                db_handler.execute_query(query)
                print(f"Schema created: {query}")
            except sqlite3.Error as e:
                print(f"Error creating schema: {e}")
                raise e
