# Importing configuration and utility modules
from .config import DB_FILE  # Path to the database file
from .database import DatabaseHandler  # Handles database operations
from .business_logic import BusinessLogic  # Main business logic for summaries
from .db_initializer import initialize_database  # Database initialization logic
from .exercise_manager import get_exercises, add_exercise  # Exercise-related operations
from .user_selection import get_user_selection  # Retrieve user selection data
from .weekly_summary import (
    calculate_weekly_summary,  # Logic for weekly summaries
    get_weekly_summary,        # Fetch stored weekly summary
    calculate_total_sets,       # Calculate total sets by muscle group
    calculate_exercise_categories,
    calculate_isolated_muscles_stats  # Add this line
)
from .session_summary import calculate_session_summary  # Per-session summary logic
from .volume_classifier import (
    get_volume_class,
    get_volume_label,
    get_volume_tooltip,
    get_category_tooltip,
    get_subcategory_tooltip
)
from .workout_log import get_workout_logs

# Defining the module's public interface
__all__ = [
    "DB_FILE",
    "DatabaseHandler",
    "BusinessLogic",
    "initialize_database",
    "get_exercises",
    "add_exercise",
    "get_user_selection",
    "calculate_weekly_summary",
    "get_weekly_summary",
    "calculate_total_sets",
    "calculate_session_summary",
    "get_workout_logs",
    "get_volume_class",
    "get_volume_label",
    "get_volume_tooltip",
    "get_category_tooltip",
    "get_subcategory_tooltip",
    "calculate_exercise_categories",
    "calculate_isolated_muscles_stats"  # Add this line
]

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
