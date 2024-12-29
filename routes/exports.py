from flask import Blueprint, Response, jsonify, request
from utils.database import DatabaseHandler
import pandas as pd
from io import BytesIO
from utils.weekly_summary import (
    calculate_exercise_categories,
    calculate_isolated_muscles_stats,
    calculate_weekly_summary
)

exports_bp = Blueprint('exports', __name__)

@exports_bp.route("/export_to_excel")
def export_to_excel():
    """Export all data to Excel."""
    try:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Export User Selection
            user_selection_query = """
            SELECT us.*, e.primary_muscle_group, e.secondary_muscle_group
            FROM user_selection us
            LEFT JOIN exercises e ON us.exercise = e.exercise_name
            """
            with DatabaseHandler() as db:
                user_selection = pd.DataFrame(db.fetch_all(user_selection_query))
            if not user_selection.empty:
                user_selection.to_excel(writer, sheet_name='Workout Plan', index=False)

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

        output.seek(0)
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=workout_tracker_summary.xlsx"},
        )
    except Exception as e:
        print(f"Error exporting to Excel: {e}")
        return jsonify({"error": "Failed to export to Excel"}), 500

@exports_bp.route("/export_to_workout_log", methods=["POST"])
def export_to_workout_log():
    """Export current workout plan to workout log."""
    try:
        query = """
        SELECT id, routine, exercise, sets, min_rep_range, max_rep_range, 
               rir, rpe, weight
        FROM user_selection
        """
        
        insert_query = """
        INSERT INTO workout_log (
            workout_plan_id, routine, exercise, planned_sets, planned_min_reps,
            planned_max_reps, planned_rir, planned_rpe, planned_weight, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        with DatabaseHandler() as db:
            workout_plan = db.fetch_all(query)
            
            if not workout_plan:
                return jsonify({"message": "No exercises to export"}), 400
                
            for exercise in workout_plan:
                params = (
                    exercise["id"], exercise["routine"], exercise["exercise"],
                    exercise["sets"], exercise["min_rep_range"], exercise["max_rep_range"],
                    exercise["rir"], exercise["rpe"], exercise["weight"]
                )
                db.execute_query(insert_query, params)
            
        return jsonify({"message": "Workout plan exported successfully"}), 200
            
    except Exception as e:
        print(f"Error exporting workout plan: {e}")
        return jsonify({"error": "Failed to export workout plan"}), 500 

@exports_bp.route("/export_summary", methods=["POST"])
def export_summary():
    """Export summary data based on specified parameters."""
    try:
        params = request.get_json()
        method = params.get('method', 'Total')
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Export Weekly Summary
            weekly_data = calculate_weekly_summary(method)
            if weekly_data:
                pd.DataFrame(weekly_data).to_excel(
                    writer, 
                    sheet_name='Weekly Summary',
                    index=False
                )
            
            # Export Categories
            categories = calculate_exercise_categories()
            if categories:
                pd.DataFrame(categories).to_excel(
                    writer,
                    sheet_name='Categories',
                    index=False
                )
                
        output.seek(0)
        return Response(
            output,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment;filename=workout_summary.xlsx"}
        )
    except Exception as e:
        print(f"Error exporting summary: {e}")
        return jsonify({"error": "Failed to export summary"}), 500 