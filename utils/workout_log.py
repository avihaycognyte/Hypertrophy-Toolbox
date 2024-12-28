from .database import DatabaseHandler

def get_workout_logs():
    """Fetch all workout log entries."""
    query = """
    SELECT * FROM workout_log 
    ORDER BY routine, exercise
    """
    try:
        with DatabaseHandler() as db:
            return db.fetch_all(query)
    except Exception as e:
        print(f"Error fetching workout logs: {e}")
        return [] 