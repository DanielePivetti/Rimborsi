"""
Script per aggiornare il database con la nuova tabella eventi
"""
from app import create_app, db
from app.models.evento import Evento
from sqlalchemy import inspect

def create_eventi_table():
    app = create_app()
    with app.app_context():
        # Crea la tabella eventi se non esiste
        inspector = inspect(db.engine)
        if 'eventi' not in inspector.get_table_names():
            db.create_all()
            print("Tabella 'eventi' creata con successo")
        else:
            print("La tabella 'eventi' esiste già")

if __name__ == "__main__":
    create_eventi_table()
