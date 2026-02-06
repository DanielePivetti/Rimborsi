# Rotte 
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash
from rimborsi.models import User, Richiesta, Evento, db, Organizzazione, StatoRichiesta

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
        richieste_da_istruire = Richiesta.query.filter_by(stato=StatoRichiesta.IN_ISTRUTTORIA).all()
        richieste_istruite = Richiesta.query.filter_by(stato=StatoRichiesta.ISTRUITA).all()

        
        template_data['richieste_da_istruire'] = richieste_da_istruire
        template_data['richieste_istruite'] = richieste_istruite
        template_data['conteggio_da_istruire'] = len(richieste_da_istruire)
        template_data['conteggio_istruite'] = len(richieste_istruite)

       
    elif current_user.role == 'compilatore':
        # Recuperiamo l'organizzazione dell'utente
        organizzazione_utente = current_user.organizzazioni[0] if current_user.organizzazioni else None
        
        # Inizializziamo le liste vuote
        richieste_in_bozza = []
        richieste_in_istruttoria = []
        
        # CONTROLLO: Se il compilatore non ha organizzazioni associate
        if not organizzazione_utente:
            flash(
                'Non sei compilatore di nessuna organizzazione. '
                'Contatta l\'amministratore per farti associare ad un\'organizzazione.',
                'warning'
            )
            template_data['compilatore_senza_organizzazione'] = True
        else:
            # Query per trovare le richieste in bozza di quella organizzazione
            richieste_in_bozza = Richiesta.query.filter_by(
                stato=StatoRichiesta.BOZZA,
                organizzazione_id=organizzazione_utente.id
            ).order_by(Richiesta.data_creazione.desc()).all()
            
            # Query per le richieste in istruttoria (stato 'B')
            richieste_in_istruttoria = Richiesta.query.filter_by(
                stato=StatoRichiesta.IN_ISTRUTTORIA,
                organizzazione_id=organizzazione_utente.id
            ).order_by(Richiesta.data_invio.desc()).all()
            
            # Query per le richieste istruite (stato 'C')
            richieste_istruite = Richiesta.query.filter_by(
                stato=StatoRichiesta.ISTRUITA,
                organizzazione_id=organizzazione_utente.id
            ).order_by(Richiesta.data_invio.desc()).all()
            
            template_data['compilatore_senza_organizzazione'] = False
            
            # Passiamo le liste di richieste al template
            template_data['richieste_in_bozza'] = richieste_in_bozza
            template_data['richieste_in_istruttoria'] = richieste_in_istruttoria
            template_data['richieste_istruite'] = richieste_istruite

    elif current_user.role == 'amministratore':
        # Query per trovare utenti COMPILATORI non associati a nessuna organizzazione
        utenti_da_associare = User.query.filter(
            User.role == 'compilatore',
            ~User.organizzazioni.any()
        ).all()
        
        # Statistiche aggiuntive per l'amministratore
        totale_compilatori = User.query.filter(User.role == 'compilatore').count()
        compilatori_associati = User.query.filter(
            User.role == 'compilatore',
            User.organizzazioni.any()
        ).count()
        
        template_data['utenti_da_associare'] = utenti_da_associare
        template_data['totale_compilatori'] = totale_compilatori
        template_data['compilatori_associati'] = compilatori_associati
    
    # Passiamo i dati al template. Il template userà 'current_user' e i dati specifici.
    return render_template('main/dashboard.html', **template_data)

# ================================================================
# GESTIONE ASSOCIAZIONE UTENTI - SOLO PER AMMINISTRATORI
# ================================================================

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
