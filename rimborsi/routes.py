
# Rotte 
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .forms import LoginForm, EventoForm
from .models import User, Richiesta, Evento, db, DocumentoSpesa, Organizzazione
from .forms import TemporaryMezzoForm  # Aggiungi a import esistenti
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_from_directory, current_app



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

# ================================================================
# FINE DEL FILE - Gestione associazione utenti spostata in main/routes.py
# ================================================================
@richiesta_bp.route('/richiesta/<int:richiesta_id>/mezzo-temporaneo', methods=['GET', 'POST'])
@login_required
def crea_mezzo_temporaneo(richiesta_id):
    """Crea un mezzo temporaneo per la richiesta corrente"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'utente possa modificare questa richiesta
    if richiesta.organizzazione_id != current_user.organizzazioni[0].id:
        flash('Non hai i permessi per modificare questa richiesta.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = TemporaryMezzoForm()
    
    if form.validate_on_submit():
        # Salva documento autorizzazione
        file = form.authorization_document.data
        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        auth_docs_dir = os.path.join(current_app.instance_path, 'uploads', 'authorization_docs')
        os.makedirs(auth_docs_dir, exist_ok=True)
        filepath = os.path.join(auth_docs_dir, filename)
        file.save(filepath)
        
        # Crea mezzo temporaneo
        mezzo = MezzoAttrezzatura(
            tipologia=form.tipologia.data,
            targa_inventario=form.targa_inventario.data,
            descrizione=form.descrizione.data,
            organizzazione_id=current_user.organizzazioni[0].id,
            is_temporary=True,
            authorization_document=filename,
            authorizing_entity=form.authorizing_entity.data,
            authorization_date=form.authorization_date.data
        )
        
        db.session.add(mezzo)
        db.session.commit()
        
        flash('Mezzo temporaneo creato con successo!', 'success')
        return redirect(url_for('richiesta.crea_impiego', richiesta_id=richiesta_id))
    
    return render_template('richiesta/crea_mezzo_temporaneo.html', form=form, richiesta=richiesta)

@richiesta_bp.route('/download-authorization/<int:mezzo_id>')
@login_required 
def download_authorization(mezzo_id):
    """Download del documento di autorizzazione per mezzi temporanei"""
    mezzo = MezzoAttrezzatura.query.get_or_404(mezzo_id)
    
    # Verifica accesso (solo la stessa organizzazione)
    if mezzo.organizzazione_id != current_user.organizzazioni[0].id:
        flash('Accesso negato', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if not mezzo.is_temporary or not mezzo.authorization_document:
        flash('Documento non disponibile', 'danger')
        return redirect(url_for('main.dashboard'))
    
    auth_docs_dir = os.path.join(current_app.instance_path, 'uploads', 'authorization_docs')
    return send_from_directory(auth_docs_dir, mezzo.authorization_document, as_attachment=True)