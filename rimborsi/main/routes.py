# Rotte 
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from rimborsi.models import User, Richiesta, Evento, db

main = Blueprint('main', __name__, template_folder='templates')

# Prima pagina dove si atterra
@main.route('/dashboard')
@login_required # Solo gli utenti loggati possono vedere la dashboard
def dashboard():
    # Ora la variabile 'current_user' è l'utente reale che ha fatto il login.
    # Carichiamo i dati dal database in base al suo ruolo.
    
    # Prepariamo un dizionario per passare i dati al template
    template_data = {}

    if current_user.role == 'istruttore':
        # Esempio di query reale: conta le richieste trasmesse
        richieste_da_istruire = Richiesta.query.filter_by(stato='B').all()
        richieste_istruite = Richiesta.query.filter_by(stato='C').all()

        
        template_data['richieste_da_istruire'] = richieste_da_istruire
        template_data['richieste_istruite'] = richieste_istruite
        template_data['conteggio_da_istruire'] = len(richieste_da_istruire)
        template_data['conteggio_istruite'] = len(richieste_istruite)

       
    elif current_user.role == 'compilatore':
        # Recuperiamo l'organizzazione dell'utente
        organizzazione_utente = current_user.organizzazioni[0] if current_user.organizzazioni else None
        
        richieste_in_bozza = []
        if organizzazione_utente:
            # Query per trovare le richieste in bozza di quella organizzazione
            richieste_in_bozza = Richiesta.query.filter_by(
                stato='A', 
                organizzazione_id=organizzazione_utente.id
            ).order_by(Richiesta.data_creazione.desc()).all()
           # Query per le richieste in istruttoria (stato 'B')
            richieste_in_istruttoria = Richiesta.query.filter_by(
                stato='B',
                organizzazione_id=organizzazione_utente.id
            ).order_by(Richiesta.data_invio.desc()).all()

        # Passiamo le liste di richieste al template
        template_data['richieste_in_bozza'] = richieste_in_bozza
        template_data['richieste_in_istruttoria'] = richieste_in_istruttoria

    elif current_user.role == 'amministratore':
        # Query per trovare utenti non associati a nessuna organizzazione
        utenti_da_associare = User.query.filter(User.organizzazioni == None).all()
        template_data['utenti_da_associare'] = utenti_da_associare
    
    # Passiamo i dati al template. Il template userà 'current_user' e i dati specifici.
    return render_template('main/dashboard.html', **template_data)

# Gestione Eventi

@main.route('/crea_richiesta')
def crea_richiesta():
    return "Pagina crea richiesta (placeholder)"

@main.route('/dettaglio_richiesta/<int:richiesta_id>')
def dettaglio_richiesta(richiesta_id):
    return f"Dettaglio richiesta {richiesta_id} (placeholder)"

@main.route('/modifica_richiesta/<int:richiesta_id>')
def modifica_richiesta(richiesta_id):
    return f"Modifica richiesta {richiesta_id} (placeholder)"

@main.route('/associa_utente/<int:user_id>')
def associa_utente(user_id):
    return f"Associa utente {user_id} (placeholder)"
