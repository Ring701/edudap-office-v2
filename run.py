from app import create_app, db
from sqlalchemy import text
import os

app = create_app()

# --- FORCEFUL RESET BUTTON ---
@app.route('/reset-database-now')
def reset_database_now():
    with app.app_context():
        # This raw SQL forces the tables to delete even if they are linked
        try:
            db.session.execute(text('DROP TABLE IF EXISTS quotation CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS alembic_version CASCADE'))
            db.session.commit()
        except Exception as e:
            return f"Error: {str(e)}"
        
        # Build fresh tables
        db.create_all()
        
    return "SUCCESS: Database has been reset. You can now go to /register"
# -----------------------------

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
