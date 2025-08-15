
# Rotte 
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .forms import LoginForm
from .models import User, db, Richiesta


main = Blueprint('main', __name__)

# Prima pagina dove si atterra

@main.route('/')
def index():
    return render_template('index.html') # Assumendo tu abbia un index.html

# Rotte placeholder per Registrazione 
@main.route('/registrati')
def registrati():
    return "Pagina di registrazione (placeholder)"

@main.route('/login', methods=['GET', 'POST'])
def login():
    # Se l'utente è già loggato, lo mandiamo alla dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Cerca l'utente nel database tramite l'email
        user = User.query.filter_by(email=form.email.data).first()
        
        # Controlla se l'utente esiste e se la password è corretta
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Login non riuscito. Controlla email e password.', 'danger')
            
    return render_template('login.html', form=form)

# Rotte per il logout
@main.route('/logout')
@login_required # Solo gli utenti loggati possono fare logout
def logout():
    logout_user()
    flash('Sei stato disconnesso.', 'info')
    return redirect(url_for('main.index'))

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
        template_data['richieste_da_istruire'] = richieste_da_istruire
        
        # Dati per le card (da implementare con query più complesse)
        template_data['dati_istruttore'] = {
            'da_istruire': len(richieste_da_istruire),
            'lavorate_mese': 0, # Esempio
            'importo_approvato_mese': '0.00', # Esempio
            'eventi_attivi': 0 # Esempio
        }

    elif current_user.role == 'compilatore':
        # Query per le richieste dell'utente loggato
        # (da filtrare anche per organizzazione attiva in futuro)
        in_bozza = Richiesta.query.filter_by(stato='A').count() # Esempio semplificato
        in_attesa = Richiesta.query.filter_by(stato='B').count() # Esempio semplificato
        
        template_data['dati_compilatore'] = {
            'in_bozza_count': in_bozza,
            'in_attesa_count': in_attesa,
            'archivio_count': 0 # Esempio
        }
        template_data['richieste_in_bozza'] = Richiesta.query.filter_by(stato='A').all() # Esempio

    elif current_user.role == 'amministratore':
        # Query per trovare utenti non associati a nessuna organizzazione
        utenti_da_associare = User.query.filter(User.organizzazioni == None).all()
        template_data['utenti_da_associare'] = utenti_da_associare
    
    # Passiamo i dati al template. Il template userà 'current_user' e i dati specifici.
    return render_template('dashboard.html', **template_data)


# Placeholder routes
@main.route('/gestione_eventi')
def gestione_eventi():
    return "Pagina gestione eventi (placeholder)"

@main.route('/crea_evento')
def crea_evento():
    return "Pagina crea evento (placeholder)"

@main.route('/crea_richiesta')
def crea_richiesta():
    return "Pagina crea richiesta (placeholder)"

@main.route('/dettaglio_richiesta/<int:richiesta_id>')
def dettaglio_richiesta(richiesta_id):
    return f"Dettaglio richiesta {richiesta_id} (placeholder)"

@main.route('/modifica_richiesta/<int:richiesta_id>')
def modifica_richiesta(richiesta_id):
    return f"Modifica richiesta {richiesta_id} (placeholder)"

@main.route('/gestione_organizzazioni')
def gestione_organizzazioni():
    return "Gestione organizzazioni (placeholder)"

@main.route('/gestione_mezzi')
def gestione_mezzi():
    return "Gestione mezzi (placeholder)"

@main.route('/associa_utente/<int:user_id>')
def associa_utente(user_id):
    return f"Associa utente {user_id} (placeholder)"
