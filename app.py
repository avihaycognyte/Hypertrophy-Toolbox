from flask import Flask
from utils import initialize_database
from routes.workout_log import workout_log_bp
from routes.weekly_summary import weekly_summary_bp
from routes.session_summary import session_summary_bp
from routes.exports import exports_bp
from routes.filters import filters_bp
from routes.workout_plan import workout_plan_bp
from routes.main import main_bp
from datetime import datetime

app = Flask(__name__)

# Initialize the database
initialize_database()

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(workout_log_bp)
app.register_blueprint(weekly_summary_bp)
app.register_blueprint(session_summary_bp)
app.register_blueprint(exports_bp)
app.register_blueprint(filters_bp)
app.register_blueprint(workout_plan_bp)

@app.template_filter('datetime')
def format_datetime(value, format='%d-%m-%Y'):
    if value and value != 'None':
        try:
            if isinstance(value, str):
                # Parse the date string (assuming it's in ISO format)
                date_obj = datetime.strptime(value, '%Y-%m-%d')
            else:
                date_obj = value
            return date_obj.strftime(format)
        except (ValueError, TypeError):
            return value
    return ''

if __name__ == "__main__":
    app.run(debug=True)
