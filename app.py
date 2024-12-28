import sqlite3
from io import BytesIO
from flask import Flask, render_template, request, jsonify, redirect, Response, url_for
import pandas as pd
from utils import (
    initialize_database,
    get_exercises,
    add_exercise,
    get_user_selection,
    calculate_weekly_summary,
    get_workout_logs,
    calculate_exercise_categories,
    calculate_isolated_muscles_stats,
)
from utils.session_summary import calculate_session_summary
from utils.database import DatabaseHandler
from utils.volume_classifier import (
    get_volume_class, 
    get_volume_label, 
    get_volume_tooltip,
    get_category_tooltip,
    get_subcategory_tooltip
)

app = Flask(__name__)

# Initialize the database
initialize_database()

# Define standard filter names
FILTER_MAPPING = {
    "Primary Muscle Group": "primary_muscle_group",
    "Secondary Muscle Group": "secondary_muscle_group",
    "Tertiary Muscle Group": "tertiary_muscle_group",
    "Advanced Isolated Muscles": "advanced_isolated_muscles",
    "Force": "force",
    "Equipment": "equipment",
    "Mechanic": "mechanic",
    "Utility": "utility",
    "Grips": "grips",
    "Stabilizers": "stabilizers",
    "Synergists": "synergists",
    "Difficulty": "difficulty"
}

@app.route("/")
def index():
    """
    Hypertrophy Toolbox main page.
    """
    return render_template("welcome.html")

def fetch_unique_values(column):
    """Fetch unique values for a specified column from the exercises table."""
    query = f"SELECT DISTINCT {column} FROM exercises WHERE {column} IS NOT NULL ORDER BY {column} ASC"
    try:
        with DatabaseHandler() as db:
            results = db.fetch_all(query, None)
            # Handle both dictionary and tuple results
            if results and isinstance(results[0], dict):
                return [row[column] for row in results if row[column]]
            else:
                return [row[0] for row in results if row[0]]
    except Exception as e:
        print(f"Error fetching unique values for {column}: {e}")
        return []

@app.route("/filter_exercises", methods=["POST"])
def filter_exercises():
    try:
        filters = request.get_json()
        print(f"DEBUG: Received filters: {filters}")

        # Convert frontend names to database column names using our standard mapping
        sanitized_filters = {}
        for key, value in filters.items():
            db_field = FILTER_MAPPING.get(key)
            if db_field and value:
                sanitized_filters[db_field] = value

        print(f"DEBUG: Sanitized filters: {sanitized_filters}")
        exercise_names = get_exercises(filters=sanitized_filters)
        print(f"DEBUG: Found {len(exercise_names)} matching exercises")

        return jsonify(exercise_names)
    except Exception as e:
        print(f"Error in filter_exercises: {e}")
        return jsonify({"error": str(e)}), 500
    

def get_routine_options():
    """Return the structured routine options with clear hierarchy."""
    return {
        "Gym": {
            "Full Body": {
                "name": "Full Body",
                "description": "Train all major muscle groups in each session",
                "routines": ["Fullbody1", "Fullbody2", "Fullbody3"]
            },
            "Split Programs": {
                "4 Week Split": {
                    "name": "4 Week Split",
                    "description": "Rotating 4-week program for maximum variety",
                    "routines": ["A1", "B1", "A2", "B2"]
                },
                "Push Pull Legs": {
                    "name": "Push, Pull, Legs",
                    "description": "Classic 6-day split focusing on movement patterns",
                    "routines": ["Push1", "Pull1", "Legs1", "Push2", "Pull2", "Legs2"]
                },
                "Upper Lower": {
                    "name": "Upper Lower",
                    "description": "4-day split targeting upper and lower body",
                    "routines": ["Upper1", "Lower1", "Upper2", "Lower2"]
                }
            },
            "Basic Splits": {
                "2 Days Split": {
                    "name": "2 Days Split",
                    "description": "Simple alternating workout pattern",
                    "routines": ["A", "B"]
                },
                "3 Days Split": {
                    "name": "3 Days Split",
                    "description": "Three-way split for balanced training",
                    "routines": ["A", "B", "C"]
                }
            }
        },
        "Home Workout": {
            "Full Body": {
                "name": "Full Body",
                "description": "Complete body workout with minimal equipment",
                "routines": ["Fullbody1", "Fullbody2", "Fullbody3"]
            },
            "Split Programs": {
                "4 Week Split": {
                    "name": "4 Week Split",
                    "description": "Home-adapted 4-week rotation",
                    "routines": ["A1", "B1", "A2", "B2"]
                },
                "Push Pull Legs": {
                    "name": "Push, Pull, Legs",
                    "description": "Bodyweight and minimal equipment PPL",
                    "routines": ["Push1", "Pull1", "Legs1", "Push2", "Pull2", "Legs2"]
                },
                "Upper Lower": {
                    "name": "Upper Lower",
                    "description": "Home-based upper/lower split",
                    "routines": ["Upper1", "Lower1", "Upper2", "Lower2"]
                }
            },
            "Basic Splits": {
                "2 Days Split": {
                    "name": "2 Days Split",
                    "description": "Simple home workout alternation",
                    "routines": ["A", "B"]
                },
                "3 Days Split": {
                    "name": "3 Days Split",
                    "description": "Three-way home training split",
                    "routines": ["A", "B", "C"]
                }
            }
        }
    }

@app.route("/workout_plan")
def workout_plan():
    try:
        exercises = get_exercises() or []
        user_selection = get_user_selection() or []

        # Initialize filters using the standard mapping
        filters = {
            display_name: fetch_unique_values(db_column) or []
            for display_name, db_column in FILTER_MAPPING.items()
        }

        return render_template(
            "workout_plan.html",
            exercises=exercises,
            user_selection=user_selection,
            filters=filters,
            routineOptions=get_routine_options(),
            enumerate=enumerate
        )
    except Exception as e:
        print(f"Error in workout_plan: {e}")
        return render_template("error.html", message="Unable to load workout plan."), 500


@app.route("/get_workout_plan")
def get_workout_plan():
    """Fetch the current workout plan."""
    try:
        query = """
        SELECT 
            us.id, us.routine, us.exercise, us.sets, 
            us.min_rep_range, us.max_rep_range, us.rir, us.weight,
            e.primary_muscle_group, e.secondary_muscle_group, 
            e.tertiary_muscle_group, e.advanced_isolated_muscles,
            e.utility, e.grips, e.stabilizers, e.synergists
        FROM user_selection us
        LEFT JOIN exercises e ON us.exercise = e.exercise_name
        ORDER BY us.routine, us.exercise
        """
        
        with DatabaseHandler() as db:
            results = db.fetch_all(query)
            return jsonify(results)
            
    except Exception as e:
        print(f"Error fetching workout plan: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/add_exercise", methods=["POST"])
def add_exercise():
    try:
        data = request.get_json()
        print("DEBUG: Received data:", data)
        
        # Validate required fields
        required_fields = ["exercise", "routine", "sets", "min_rep_range", "max_rep_range", "weight"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            print(f"DEBUG: Missing fields: {missing_fields}")
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        exercise = data["exercise"]
        routine = data["routine"]
        sets = int(data["sets"])
        min_rep_range = int(data["min_rep_range"])
        max_rep_range = int(data["max_rep_range"])
        rir = int(data.get("rir", 0))
        weight = float(data["weight"])

        # Validate data types and ranges
        if not all(isinstance(x, (int, float)) for x in [sets, min_rep_range, max_rep_range, rir, weight]):
            return jsonify({"error": "Invalid numeric values provided"}), 400

        try:
            with DatabaseHandler() as db:
                db.execute_query(
                    """
                    INSERT INTO user_selection 
                    (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, 
                    (routine, exercise, sets, min_rep_range, max_rep_range, rir, weight)
                )
                
                new_id = db.cursor.lastrowid
                print(f"DEBUG: Successfully added exercise with ID: {new_id}")
                
                # Fetch the complete exercise details
                details_query = """
                SELECT 
                    us.id, us.routine, us.exercise, us.sets, 
                    us.min_rep_range, us.max_rep_range, us.rir, us.weight,
                    e.primary_muscle_group, e.secondary_muscle_group, 
                    e.tertiary_muscle_group, e.advanced_isolated_muscles, e.utility,
                    e.grips, e.stabilizers, e.synergists
                FROM user_selection us
                JOIN exercises e ON us.exercise = e.exercise_name
                WHERE us.id = ?
                """
                exercise_details = db.fetch_one(details_query, (new_id,))
                
                if not exercise_details:
                    raise Exception("Failed to fetch newly added exercise details")
                
                return jsonify({
                    "message": "Exercise added successfully",
                    "data": [exercise_details]
                }), 200

        except sqlite3.Error as e:
            print(f"DEBUG: Database error: {str(e)}")
            if "UNIQUE constraint failed" in str(e):
                return jsonify({"error": "This exact exercise configuration already exists"}), 400
            return jsonify({"error": "Failed to add exercise to database"}), 500

    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)}")
        return jsonify({"error": f"Failed to add exercise: {str(e)}"}), 500

@app.route("/remove_exercise", methods=["POST"])
def remove_exercise():
    try:
        data = request.get_json()
        print(f"DEBUG: Received data for remove_exercise: {data}")

        exercise_id = data.get("id")
        if not exercise_id or not str(exercise_id).isdigit():
            return jsonify({"message": "Invalid exercise ID"}), 400

        query = "DELETE FROM user_selection WHERE id = ?"
        with DatabaseHandler() as db_handler:
            db_handler.execute_query(query, (int(exercise_id),))

        print(f"DEBUG: Deleted exercise with ID = {exercise_id}")
        return jsonify({"message": "Exercise removed successfully"}), 200
    except Exception as e:
        print(f"Error in remove_exercise: {e}")
        return jsonify({"error": "Unable to remove exercise"}), 500

@app.route("/weekly_summary", methods=["GET"])
def weekly_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_weekly_summary(method)
        category_results = calculate_exercise_categories()
        isolated_muscles_stats = calculate_isolated_muscles_stats()
        
        if request.headers.get("Accept") == "application/json":
            return jsonify({
                "weekly_summary": results,
                "categories": category_results,
                "isolated_muscles": isolated_muscles_stats
            })
        
        return render_template(
            "weekly_summary.html",
            page_title="Weekly Summary",
            weekly_summary=results,
            categories=category_results,
            isolated_muscles=isolated_muscles_stats,
            get_volume_class=get_volume_class,
            get_volume_label=get_volume_label,
            get_volume_tooltip=get_volume_tooltip,
            get_category_tooltip=get_category_tooltip,
            get_subcategory_tooltip=get_subcategory_tooltip
        )
    except Exception as e:
        print(f"Error in weekly_summary: {e}")
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Unable to fetch weekly summary"}), 500
        return render_template("error.html", message="Unable to load weekly summary."), 500

@app.route("/session_summary", methods=["GET"])
def session_summary():
    method = request.args.get("method", "Total")
    try:
        results = calculate_session_summary(method)
        category_results = calculate_exercise_categories()
        isolated_muscles_stats = calculate_isolated_muscles_stats()
        
        if request.headers.get("Accept") == "application/json":
            return jsonify({
                "session_summary": results,
                "categories": category_results,
                "isolated_muscles": isolated_muscles_stats
            })
        
        return render_template(
            "session_summary.html",
            session_summary=results,
            categories=category_results,
            isolated_muscles=isolated_muscles_stats,
            get_volume_class=get_volume_class,
            get_volume_label=get_volume_label,
            get_volume_tooltip=get_volume_tooltip,
            get_category_tooltip=get_category_tooltip,
            get_subcategory_tooltip=get_subcategory_tooltip
        )
    except Exception as e:
        print(f"Error in session_summary: {e}")
        if request.headers.get("Accept") == "application/json":
            return jsonify({"error": "Unable to fetch session summary"}), 500
        return render_template("error.html", message="Unable to load session summary."), 500

@app.route("/export_to_excel")
def export_to_excel():
    """Export all data to Excel."""
    try:
        # Create a BytesIO object to store the Excel file
        output = BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Export Workout Plan
            workout_plan_query = """
            SELECT 
                us.routine, us.exercise, us.sets, 
                us.min_rep_range, us.max_rep_range, us.rir, us.weight,
                e.primary_muscle_group, e.secondary_muscle_group, 
                e.tertiary_muscle_group, e.advanced_isolated_muscles,
                e.utility, e.grips, e.stabilizers, e.synergists
            FROM user_selection us
            JOIN exercises e ON us.exercise = e.exercise_name
            ORDER BY us.routine, us.exercise
            """
            with DatabaseHandler() as db:
                workout_plan = pd.DataFrame(db.fetch_all(workout_plan_query))
            if not workout_plan.empty:
                workout_plan.to_excel(writer, sheet_name='Workout Plan', index=False)

            # Export Weekly Summary
            weekly_summary = pd.DataFrame(calculate_weekly_summary())
            if not weekly_summary.empty:
                weekly_summary.to_excel(writer, sheet_name='Weekly Summary', index=False)

            # Export Session Summary
            session_summary = pd.DataFrame(calculate_session_summary())
            if not session_summary.empty:
                session_summary.to_excel(writer, sheet_name='Session Summary', index=False)

            # Export Workout Log
            workout_log_query = """
            SELECT * FROM workout_log 
            ORDER BY routine, exercise
            """
            with DatabaseHandler() as db:
                workout_log = pd.DataFrame(db.fetch_all(workout_log_query))
            if not workout_log.empty:
                workout_log.to_excel(writer, sheet_name='Workout Log', index=False)

            # Export Categories Summary
            categories = pd.DataFrame(calculate_exercise_categories())
            if not categories.empty:
                categories.to_excel(writer, sheet_name='Categories', index=False)

            # Export Isolated Muscles Stats
            isolated_muscles = pd.DataFrame(calculate_isolated_muscles_stats())
            if not isolated_muscles.empty:
                isolated_muscles.to_excel(writer, sheet_name='Isolated Muscles', index=False)

        # Set response headers
        output.seek(0)
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=workout_tracker_summary.xlsx"},
        )
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({"error": "Failed to export to Excel"}), 500

@app.route("/workout_log")
def workout_log():
    """Render the workout log page."""
    try:
        workout_logs = get_workout_logs()
        return render_template(
            "workout_log.html",
            page_title="Workout Log",
            workout_logs=workout_logs,
            enumerate=enumerate,
        )
    except Exception as e:
        print(f"Error in workout_log: {e}")
        return render_template("error.html", message="Unable to load workout log."), 500

@app.route("/export_to_workout_log", methods=["POST"])
def export_to_workout_log():
    """Export workout plan to workout log."""
    try:
        with DatabaseHandler() as db:
            # Get current workout plan
            plan_query = """
            SELECT 
                us.id, us.routine, us.exercise, us.sets, 
                us.min_rep_range, us.max_rep_range, us.rir, us.weight
            FROM user_selection us
            """
            workout_plan = db.fetch_all(plan_query)

            # Insert each exercise into workout log
            insert_query = """
            INSERT INTO workout_log (
                workout_plan_id, routine, exercise, planned_sets,
                planned_min_reps, planned_max_reps, planned_rir, planned_weight
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            for exercise in workout_plan:
                db.execute_query(
                    insert_query,
                    (
                        exercise["id"],
                        exercise["routine"],
                        exercise["exercise"],
                        exercise["sets"],
                        exercise["min_rep_range"],
                        exercise["max_rep_range"],
                        exercise["rir"],
                        exercise["weight"]
                    )
                )

        return jsonify({"message": "Workout plan exported to log successfully"}), 200
    except Exception as e:
        print(f"Error exporting to workout log: {e}")
        return jsonify({"error": "Failed to export workout plan"}), 500

@app.route("/update_workout_log", methods=["POST"])
def update_workout_log():
    """Update workout log entry."""
    try:
        data = request.get_json()
        log_id = data.get("id")
        updates = data.get("updates", {})

        valid_fields = {
            "scored_weight", "scored_min_reps", 
            "scored_max_reps", "last_progression_date"
        }

        # Filter out invalid fields
        valid_updates = {k: v for k, v in updates.items() if k in valid_fields}

        if not valid_updates:
            return jsonify({"message": "No valid fields to update"}), 400

        # Build update query
        set_clause = ", ".join(f"{k} = ?" for k in valid_updates.keys())
        query = f"UPDATE workout_log SET {set_clause} WHERE id = ?"
        
        # Prepare parameters
        params = list(valid_updates.values()) + [log_id]

        with DatabaseHandler() as db:
            db.execute_query(query, params)

        return jsonify({"message": "Workout log updated successfully"}), 200
    except Exception as e:
        print(f"Error updating workout log: {e}")
        return jsonify({"error": "Failed to update workout log"}), 500

@app.route("/get_exercise_details/<int:exercise_id>")
def get_exercise_details(exercise_id):
    query = """
    SELECT
        us.id, us.routine, us.exercise, us.sets,
        us.min_rep_range, us.max_rep_range, us.rir, us.weight,
        e.primary_muscle_group, e.secondary_muscle_group,
        e.tertiary_muscle_group, e.advanced_isolated_muscles, e.utility,
        e.grips, e.stabilizers, e.synergists
    FROM user_selection us
    JOIN exercises e ON us.exercise = e.exercise_name
    WHERE us.id = ?
    """

@app.route("/get_all_exercises")
def get_all_exercises():
    """Get all exercises without any filters."""
    try:
        with DatabaseHandler() as db:
            query = "SELECT exercise_name FROM exercises ORDER BY exercise_name"
            results = db.fetch_all(query)
            exercises = [result['exercise_name'] for result in results]
            return jsonify(exercises)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delete_workout_log', methods=['POST'])
def delete_workout_log():
    try:
        data = request.get_json()
        log_id = data.get('id')
        
        if not log_id:
            return jsonify({"error": "No log ID provided"}), 400
        
        with DatabaseHandler() as db:
            query = "DELETE FROM workout_log WHERE id = ?"
            db.execute_query(query, (log_id,))
            
        return jsonify({"message": "Log entry deleted successfully"}), 200
        
    except Exception as e:
        print(f"Error deleting workout log: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
