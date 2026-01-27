from app import create_app, db
from sqlalchemy import text
import os

app = create_app()

# --- FORCEFUL RESET BUTTON ---
@app.route('/reset-database-now')
def reset_database_now():
    with app.app_context():
        try:
            # FIX: Added 'product_quote' to the delete list.
            # This is critical to removing the "1, 10, 11" garbage data.
            db.session.execute(text('DROP TABLE IF EXISTS product_quote CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS quotation CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS expense CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS attendance CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS leave CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS task CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS task_chat CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS to_do_alarm CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS "user" CASCADE'))
            db.session.execute(text('DROP TABLE IF EXISTS alembic_version CASCADE'))
            db.session.commit()
            
            # Rebuild clean tables
            db.create_all()
            return "SUCCESS: Database FULLY reset. Garbage data is gone. Go to /register"
        except Exception as e:
            return f"Error during reset: {str(e)}"

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
