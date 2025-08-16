from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from rimborsi.models import db, Evento, Richiesta, Organizzazione
from .forms import RichiestaForm

richiesta_bp = Blueprint('richiesta', __name__, 
                         template_folder='templates',
                         url_prefix='/richiesta')

# La rotta 'seleziona_evento' non è più necessaria e può essere cancellata.

# --- NUOVA E UNICA ROTTA DI CREAZIONE ---
@richiesta_bp.route('/crea', methods=['GET', 'POST'])
@login_required
def crea_richiesta():
    """
    Mostra un unico form per selezionare l'evento e creare la richiesta.
    """
    form = RichiestaForm()
    
    if form.validate_on_submit():
        # L'evento viene preso direttamente dal form
        evento_selezionato = form.evento.data
        
        organizzazione_utente = current_user.organizzazioni[0] if current_user.organizzazioni else None
        if not organizzazione_utente:
            flash("Non sei associato a nessuna organizzazione. Contatta un amministratore.", "danger")
            return redirect(url_for('main.dashboard'))

        nuova_richiesta = Richiesta(
            # I dati vengono presi dal form
            attivita_svolta=form.attivita_svolta.data,
            data_inizio_attivita=form.data_inizio_attivita.data,
            data_fine_attivita=form.data_fine_attivita.data,
            numero_volontari_coinvolti=form.numero_volontari_coinvolti.data,
            # L'evento e l'organizzazione vengono associati
            evento_id=evento_selezionato.id,
            organizzazione_id=organizzazione_utente.id
        )
        
        db.session.add(nuova_richiesta)
        db.session.commit()
        
        flash('Richiesta creata con successo! Ora puoi aggiungere le spese.', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=nuova_richiesta.id)) # Placeholder per il futuro

    return render_template('richiesta/crea_richiesta.html',
                           form=form,
                           titolo="Crea Nuova Richiesta")
    

@richiesta_bp.route('/dettaglio/<int:richiesta_id>')
@login_required
def dettaglio_richiesta(richiesta_id):
    """
    Mostra la pagina di dettaglio (il "tavolo da lavoro") per una richiesta in bozza.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # In futuro, qui aggiungeremo le query per caricare spese, mezzi, etc.

    # Corretto: renderizziamo un template invece di reindirizzare alla stessa route
    return render_template('richiesta/dettaglio_richiesta.html', richiesta=richiesta)