from flask import Flask, render_template

app = Flask(__name__)

# Definizione del contenuto HTML della pagina di benvenuto

# Definizione della rotta principale ("/")
@app.route('/')
def home():
    """
    Questa funzione viene eseguita quando un utente visita la home page.
    """
    return render_template('index.html')

# Per l'homepage, potresti aggiungere un link alla dashboard dopo il login
@app.route('/')
def index():
    # Se l'utente è loggato, reindirizzalo alla dashboard
    # if utente_loggato():
    #     return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Qui potresti recuperare i dati dal database, ad esempio:
    # numero_associazioni = len(Associazione.query.all())
    # richieste_in_attesa = len(Richiesta.query.filter_by(status='in_attesa').all())

    # E passarli al template
    return render_template('dashboard.html')


if __name__ == '__main__':
    # Esecuzione dell'applicazione Flask in modalità debug
    # debug=True permette il ricaricamento automatico del server a ogni modifica
    app.run(debug=True)

Da qua

# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# --- 1. Configurazione di Base dell'Applicazione ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# --- 2. Configurazione della Connessione al Database ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'rimborsi.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# --- 3. Inizializzazione dell'Oggetto Database ---
db = SQLAlchemy(app)



# --- MODELLI DEL DATABASE ---
# Qui definiamo la struttura delle nostre tabelle. Ogni classe rappresenta una tabella.

# Tabella associativa per la relazione Molti-a-Molti tra Utente e Organizzazione
# Un compilatore può essere associato a più organizzazioni.
associazione_utente_organizzazione = db.Table('associazione_utente_organizzazione',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('organizzazione_id', db.Integer, db.ForeignKey('organizzazione.id'), primary_key=True)
)

class User(db.Model):
    """ Modello per gli utenti del sistema (Amministratore, Compilatore, Istruttore) """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False) # La password non va mai salvata in chiaro!
    role = db.Column(db.String(20), nullable=False) # Es. 'amministratore', 'compilatore', 'istruttore'
    
    # Relazione Molti-a-Molti con Organizzazione
    organizzazioni = db.relationship('Organizzazione', secondary=associazione_utente_organizzazione,
                                     back_populates='utenti_compilatori')

class Organizzazione(db.Model):
    """ Anagrafica delle organizzazioni di volontariato """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    acronimo = db.Column(db.String(20))
    codice_interno = db.Column(db.String(20), unique=True)
    indirizzo = db.Column(db.String(200))

    # Relazioni (lato "uno" di una relazione uno-a-molti)
    mezzi = db.relationship('MezzoAttrezzatura', backref='organizzazione', lazy=True)
    richieste = db.relationship('Richiesta', backref='organizzazione', lazy=True)
    utenti_compilatori = db.relationship('User', secondary=associazione_utente_organizzazione,
                                         back_populates='organizzazioni')

class MezzoAttrezzatura(db.Model):
    """ Registro dei mezzi e delle attrezzature di ogni organizzazione """
    id = db.Column(db.Integer, primary_key=True)
    tipologia = db.Column(db.String(1), nullable=False) # 'A': Mezzo, 'B': Attrezzatura
    targa_inventario = db.Column(db.String(50), unique=True, nullable=False)
    descrizione = db.Column(db.String(200))
    organizzazione_id = db.Column(db.Integer, db.ForeignKey('organizzazione.id'), nullable=False)

class Evento(db.Model):
    """ Descrive l'evento (emergenza, esercitazione, etc.) """
    id = db.Column(db.Integer, primary_key=True)
    protocollo_attivazione = db.Column(db.String(50), unique=True)
    nome = db.Column(db.String(150), nullable=False)
    tipologia = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D', 'E'
    data_inizio = db.Column(db.Date)
    data_fine = db.Column(db.Date)
    descrizione = db.Column(db.Text)
    richieste = db.relationship('Richiesta', backref='evento', lazy=True)

class Richiesta(db.Model):
    """ Contenitore principale della richiesta di rimborso """
    id = db.Column(db.Integer, primary_key=True)
    stato = db.Column(db.String(1), default='A', nullable=False) # 'A': bozza, 'B': trasmessa, 'C': istruita
    esito = db.Column(db.String(1)) # 'A': Approvata, 'B': parzialmente, 'C': respinta
    attivita_svolta = db.Column(db.Text)
    data_inizio_attivita = db.Column(db.Date)
    data_fine_attivita = db.Column(db.Date)
    numero_volontari_coinvolti = db.Column(db.Integer)
    data_creazione = db.Column(db.DateTime, default=datetime.utcnow)
    data_invio = db.Column(db.DateTime)
    data_fine_istruttoria = db.Column(db.DateTime)
    
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)
    organizzazione_id = db.Column(db.Integer, db.ForeignKey('organizzazione.id'), nullable=False)
    
    spese = db.relationship('Spesa', backref='richiesta', lazy=True, cascade="all, delete-orphan")

class Spesa(db.Model):
    """ Singola voce di costo all'interno di una richiesta """
    id = db.Column(db.Integer, primary_key=True)
    data_spesa = db.Column(db.Date, nullable=False)
    categoria = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D', 'E'
    descrizione_spesa = db.Column(db.String(250))
    importo_richiesto = db.Column(db.Float, nullable=False)
    importo_approvato = db.Column(db.Float)
    note_istruttoria = db.Column(db.Text)
    
    richiesta_id = db.Column(db.Integer, db.ForeignKey('richiesta.id'), nullable=False)
    
    documenti = db.relationship('DocumentoSpesa', backref='spesa', lazy=True, cascade="all, delete-orphan")
    impiego = db.relationship('ImpiegoMezzoAttrezzatura', backref='spesa', uselist=False, cascade="all, delete-orphan")

class DocumentoSpesa(db.Model):
    """ Dettagli del giustificativo di spesa (scontrino, fattura, etc.) """
    id = db.Column(db.Integer, primary_key=True)
    data_documento = db.Column(db.Date, nullable=False)
    fornitore = db.Column(db.String(150))
    importo_documento = db.Column(db.Float, nullable=False)
    tipo_documento = db.Column(db.String(50)) # "Giustificativo", "AttestazioneDanno", "Autorizzazione"
    
    spesa_id = db.Column(db.Integer, db.ForeignKey('spesa.id'), nullable=False)

class ImpiegoMezzoAttrezzatura(db.Model):
    """ Dettaglio dell'utilizzo di un mezzo/attrezzatura per una spesa """
    id = db.Column(db.Integer, primary_key=True)
    localita_impiego = db.Column(db.String(200))
    data_ora_inizio_impiego = db.Column(db.DateTime)
    data_ora_fine_impiego = db.Column(db.DateTime)
    km_partenza = db.Column(db.Float)
    km_arrivo = db.Column(db.Float)
    
    @property
    def km_totali(self):
        if self.km_partenza is not None and self.km_arrivo is not None:
            return self.km_arrivo - self.km_partenza
        return 0

    mezzo_attrezzatura_id = db.Column(db.Integer, db.ForeignKey('mezzo_attrezzatura.id'), nullable=False)
    spesa_id = db.Column(db.Integer, db.ForeignKey('spesa.id'), unique=True, nullable=False)

# --- Rotta di Esempio per Test ---
@app.route('/')
def index():
    return "<h1>Applicazione Rimborsi</h1><p>I modelli del database sono stati caricati!</p>"

# --- Esecuzione dell'Applicazione e Creazione del Database ---
if __name__ == '__main__':
    with app.app_context():
        # Questo comando crea il file 'rimborsi.db' e tutte le tabelle definite sopra.
        db.create_all()
        print("Database 'rimborsi.db' e tutte le tabelle sono stati creati con successo.")

    app.run(debug=True)
