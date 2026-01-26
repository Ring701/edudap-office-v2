from run import app
from app import db
with app.app_context():
    db.drop_all()
    db.create_all()
    print("DATABASE RESET SUCCESSFUL")