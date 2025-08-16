from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from rimborsi.models import db, Evento, Richiesta, Organizzazione
from .forms import RichiestaForm

richiesta_bp = Blueprint('richiesta', __name__, 
                         template_folder='templates',
                         url_prefix='/richiesta')

# --- ROTTA 1: SELEZIONE DELL'EVENTO ---

@richiesta_bp.route('/seleziona_evento')
@login_required
def seleziona_evento():
    """
    Mostra una lista di eventi attivi per cui è possibile creare una richiesta.
    """
    # Per ora, carichiamo tutti gli eventi. In futuro potremmo filtrarli (es. per data).
    eventi = Evento.query.order_by(Evento.data_inizio.desc()).all()
    return render_template('richiesta/seleziona_evento.html', eventi=eventi)

# --- ROTTA 2: CREAZIONE DELLA RICHIESTA ---

@richiesta_bp.route('/crea/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def crea_richiesta(evento_id):
    """
    Mostra il form per creare una nuova richiesta associata a un evento specifico.
    """
    evento_selezionato = Evento.query.get_or_404(evento_id)
    form = RichiestaForm()
    
    if form.validate_on_submit():
        # Assumiamo che il compilatore appartenga ad una sola organizzazione per ora
        # In futuro, qui andrà la logica per gestire multi-appartenenza
        organizzazione_utente = current_user.organizzazioni[0] if current_user.organizzazioni else None

        if not organizzazione_utente:
            flash("Non sei associato a nessuna organizzazione. Contatta un amministratore.", "danger")
            return redirect(url_for('main.dashboard'))

        nuova_richiesta = Richiesta(
            attivita_svolta=form.attivita_svolta.data,
            data_inizio_attivita=form.data_inizio_attivita.data,
            data_fine_attivita=form.data_fine_attivita.data,
            numero_volontari_coinvolti=form.numero_volontari_coinvolti.data,
            evento_id=evento_selezionato.id,
            organizzazione_id=organizzazione_utente.id
            # lo stato 'A' e la data_creazione sono gestiti in automatico dal model
        )
        
        db.session.add(nuova_richiesta)
        db.session.commit()
        
        flash('Dati generali della richiesta salvati con successo! Ora puoi aggiungere le spese.', 'success')
        # Reindirizza alla futura pagina di "dettaglio richiesta" (il nostro tavolo da lavoro)
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=nuova_richiesta.id))

    return render_template('richiesta/crea_richiesta.html',
                           form=form,
                           evento=evento_selezionato,
                           titolo=f"Crea Richiesta per l'Evento: {evento_selezionato.nome}")