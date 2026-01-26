from app import create_app, db
import os

# Gunicorn looks for this exact 'app' variable name
app = create_app()

# --- TEMPORARY MAGIC RESET BUTTON ---
# This allows you to reset the DB by visiting the URL
@app.route('/reset-database-now')
def reset_database_now():
    with app.app_context():
        db.drop_all()
        db.create_all()
    return "SUCCESS: Database has been reset. You can now go to /register"
# ------------------------------------

if __name__ == "__main__":
    # Development mode
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
