# app.py
from flask import Flask, render_template
import os
from datetime import datetime
from models import db  # Importa l'oggetto db dal nostro nuovo file

# --- 1. Configurazione di Base dell'Applicazione ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# --- 2. Configurazione della Connessione al Database ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rimborsi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. Inizializzazione dell'Oggetto Database con l'app Flask ---
db.init_app(app)

# --- 4. Definizione delle Rotte ---

@app.route('/')
def index():
    # In una vera app, qui ci sarebbe il login o una landing page.
    # Per ora, diamo istruzioni per il test.
    return render_template('index.html')


# --- ROUTE PLACEHOLDER DOPO LA CREAZIONE DI app ---
@app.route('/gestione_eventi')
def gestione_eventi():
    return "Pagina gestione eventi (placeholder)"

@app.route('/crea_evento')
def crea_evento():
    return "Pagina crea evento (placeholder)"

@app.route('/dettaglio_richiesta/<int:richiesta_id>')
def dettaglio_richiesta(richiesta_id):
    return f"Dettaglio richiesta {richiesta_id} (placeholder)"

@app.route('/crea_richiesta')
def crea_richiesta():
    return "Crea nuova richiesta (placeholder)"

@app.route('/modifica_richiesta/<int:richiesta_id>')
def modifica_richiesta(richiesta_id):
    return f"Modifica richiesta {richiesta_id} (placeholder)"

@app.route('/gestione_organizzazioni')
def gestione_organizzazioni():
    return "Gestione organizzazioni (placeholder)"

@app.route('/gestione_mezzi')
def gestione_mezzi():
    return "Gestione mezzi (placeholder)"

@app.route('/associa_utente/<int:user_id>')
def associa_utente(user_id):
    return f"Associa utente {user_id} (placeholder)"




class MockUser:
    def __init__(self, username, role):
        self.username = username
        self.role = role

@app.route('/dashboard/<role>')
def dashboard(role):
    mock_user = MockUser(username=f'{role}_test', role=role)
    context = {"current_user": mock_user, "role": role}
    # Passa sempre le variabili richieste dal template come liste vuote
    if role == "istruttore":
        context["richieste_da_istruire"] = []
    if role == "compilatore":
        context["richieste_in_bozza"] = []
    if role == "amministratore":
        context["utenti_da_associare"] = []
    return render_template('dashboard.html', **context)


if __name__ == '__main__':
    with app.app_context():
        # Questo comando usa l'oggetto db importato da models.py
        # e crea le tabelle se non esistono.
        db.create_all()
        print("Database 'rimborsi.db' e tabelle controllati/creati con successo.")

    app.run(debug=True)