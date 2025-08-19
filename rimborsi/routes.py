
# Rotte 
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .forms import LoginForm, EventoForm
from .models import User, Richiesta, Evento, db, DocumentoSpesa, Organizzazione


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
        # Query per trovare utenti con ruolo "compilatore" non associati a nessuna organizzazione
        utenti_da_associare = User.query.filter_by(role='compilatore').filter(~User.organizzazioni.any()).all()
        
        # Carica anche tutte le organizzazioni per il form di associazione
        organizzazioni = db.session.query(db.func.distinct(Organizzazione.id), Organizzazione.nome).all()
        
        template_data['utenti_da_associare'] = utenti_da_associare
        template_data['organizzazioni'] = organizzazioni
    
    # Passiamo i dati al template. Il template userà 'current_user' e i dati specifici.
    return render_template('main/dashboard.html', **template_data)

# Gestione Eventi

@main.route('/gestione_eventi')
@login_required
def gestione_eventi():
    eventi = Evento.query.order_by(Evento.data_inizio.desc()).all()
    return render_template('gestione_eventi.html', eventi=eventi)

# Modifica eventi

@main.route('/modifica_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def modifica_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    form = EventoForm(obj=evento)
    if form.validate_on_submit():
        form.populate_obj(evento)
        db.session.commit()
        flash('Evento modificato con successo!', 'success')
        return redirect(url_for('main.gestione_eventi'))
    return render_template('crea_modifica_evento.html', form=form, evento=evento)


# Cancella evento

@main.route('/cancella_evento/<int:evento_id>', methods=['POST'])
@login_required
def cancella_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento cancellato con successo!', 'success')
    return redirect(url_for('main.gestione_eventi'))

@main.route('/crea_evento', methods=['GET', 'POST'])
@login_required
def crea_evento():
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento()
        form.populate_obj(evento)
        db.session.add(evento)
        db.session.commit()
        flash('Evento creato con successo!', 'success')
        return redirect(url_for('main.gestione_eventi'))
    return render_template('crea_modifica_evento.html', form=form)

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

@main.route('/associa_utente/<int:user_id>', methods=['GET', 'POST'])
@login_required
def associa_utente(user_id):
    """Gestisce l'associazione di un utente a una o più organizzazioni."""
    # Verifica che l'utente corrente sia un amministratore
    if current_user.role != 'amministratore':
        flash('Solo gli amministratori possono associare utenti alle organizzazioni.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Trova l'utente da associare
    utente = User.query.get_or_404(user_id)
    
    # Verifica che l'utente sia un compilatore
    if utente.role != 'compilatore':
        flash('Solo gli utenti con ruolo "compilatore" possono essere associati alle organizzazioni.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Carica tutte le organizzazioni disponibili
    organizzazioni = Organizzazione.query.all()
    
    # Gestisci il form di associazione
    if request.method == 'POST':
        # Prendi gli ID delle organizzazioni selezionate dal form
        org_ids = request.form.getlist('organizzazioni')
        
        if not org_ids:
            flash('Seleziona almeno un\'organizzazione.', 'warning')
            return render_template('main/associa_utente.html', utente=utente, organizzazioni=organizzazioni)
        
        # Trova le organizzazioni selezionate
        orgs_selezionate = Organizzazione.query.filter(Organizzazione.id.in_(org_ids)).all()
        
        # Associa l'utente alle organizzazioni
        utente.organizzazioni = orgs_selezionate
        
        # Salva le modifiche
        db.session.commit()
        
        flash(f'Utente {utente.email} associato a {len(orgs_selezionate)} organizzazioni.', 'success')
        return redirect(url_for('main.dashboard'))
    
    # Mostra il form di associazione
    return render_template('main/associa_utente.html', utente=utente, organizzazioni=organizzazioni)
