from app import db, create_app
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    print(inspector.get_table_names())
