from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from rimborsi.models import Evento, db, Richiesta, UserMixin 
from datetime import datetime
from .forms import EventoForm             # Importa il form dalla cartella corrente


# 1. Crea il nuovo Blueprint 'istruttoria'
istruttoria_bp = Blueprint('istruttoria', __name__, template_folder='templates', 
                           url_prefix='/istruttoria')

    
# Gestione Eventi

@istruttoria_bp.route('/gestione_eventi')
@login_required
def gestione_eventi():
    eventi = Evento.query.order_by(Evento.data_inizio.desc()).all()
    return render_template('istruttoria/gestione_eventi.html', eventi=eventi)

# Modifica eventi

@istruttoria_bp.route('/modifica_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def modifica_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    form = EventoForm(obj=evento)
    if form.validate_on_submit():
        form.populate_obj(evento)
        db.session.commit()
        flash('Evento modificato con successo!', 'success')
        return redirect(url_for('istruttoria.gestione_eventi'))
    return render_template('istruttoria/crea_modifica_evento.html', form=form, evento=evento)


# Cancella evento

@istruttoria_bp.route('/cancella_evento/<int:evento_id>', methods=['POST'])
@login_required
def cancella_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento cancellato con successo!', 'success')
    return redirect(url_for('istruttoria.gestione_eventi'))

# Crea evento

@istruttoria_bp.route('/crea_evento', methods=['GET', 'POST'])
@login_required
def crea_evento():
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento()
        form.populate_obj(evento)
        db.session.add(evento)
        db.session.commit()
        flash('Evento creato con successo!', 'success')
        return redirect(url_for('istruttoria.gestione_eventi'))
    return render_template('istruttoria/crea_modifica_evento.html', form=form)

# Gestione istruttoria

@istruttoria_bp.route('/dettaglio/<int:richiesta_id>')
@login_required
def dettaglio_istruttoria(richiesta_id):
    """
    Pagina di lavoro principale per l'istruttore per una specifica richiesta.
    """
    # Verifica che l'utente sia un istruttore (misura di sicurezza)
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))

    richiesta = Richiesta.query.get_or_404(richiesta_id)
    # Per ora passiamo solo la richiesta, il template navigherà le relazioni
    return render_template('istruttoria/dettaglio_istruttoria.html', richiesta=richiesta)

# Rotta per il salvataggio dell'istruttoria

@istruttoria_bp.route('/<int:richiesta_id>/salva', methods=['POST'])
@login_required
def salva_istruttoria(richiesta_id):
    """
    Salva tutti i dati inseriti dall'istruttore nella pagina di dettaglio.
    """
    # Verifica che l'utente sia un istruttore
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))

    richiesta = Richiesta.query.get_or_404(richiesta_id)

    # 1. Itera attraverso ogni spesa della richiesta
    for spesa in richiesta.spese:
        # Recupera l'importo approvato dal form
        importo_str = request.form.get(f"importo_approvato_{spesa.id}")
        spesa.importo_approvato = float(importo_str) if importo_str else None

        # Recupera le note per la spesa dal form
        spesa.note_istruttoria = request.form.get(f"note_spesa_{spesa.id}")

        # 2. Per ogni spesa, itera attraverso i suoi documenti
        for doc in spesa.documenti:
            # La checkbox, se spuntata, sarà presente in request.form
            doc.verificato = f"verificato_{doc.id}" in request.form
            
            # Recupera le note per il documento
            doc.note_istruttore = request.form.get(f"note_documento_{doc.id}")

    # 3. Salva tutte le modifiche nel database in un'unica operazione
    try:
        db.session.commit()
        flash("Progressi dell'istruttoria salvati con successo.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Errore durante il salvataggio: {e}", "danger")

    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))


@istruttoria_bp.route('/<int:richiesta_id>/controllo')
@login_required
def controlla_istruttoria(richiesta_id):
    """Esegue i controlli e mostra la pagina di riepilogo per la conclusione."""
    # ... (la logica di controllo che avevamo definito) ...
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    # Esempio di controllo:
    if not richiesta.spese:
        flash('Errore: Impossibile concludere un\'istruttoria senza spese.', 'danger')
        return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))
    totale_richiesto = sum(spesa.importo_richiesto for spesa in richiesta.spese)
    # Gestisce il caso in cui alcuni importi approvati siano ancora vuoti (None)
    totale_approvato = sum(spesa.importo_approvato or 0 for spesa in richiesta.spese)

    # Passiamo i totali e la richiesta al template
    return render_template('istruttoria/riepilogo_conclusione.html', 
                           richiesta=richiesta,
                           totale_richiesto=totale_richiesto,
                           totale_approvato=totale_approvato)
     
    
@istruttoria_bp.route('/<int:richiesta_id>/concludi', methods=['POST'])
@login_required
def concludi_istruttoria(richiesta_id):
    """Finalizza l'istruttoria, cambia stato e salva il protocollo."""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Aggiorna i campi della richiesta (qui recupererai i dati dal form di riepilogo)
    richiesta.stato = 'C'  # Stato: Istruita
    richiesta.esito = request.form.get('esito')
    richiesta.note_istruttoria = request.form.get('note_istruttoria')
    richiesta.data_fine_istruttoria = datetime.utcnow()
    richiesta.protocollo_istruttoria = f"ISTR-{datetime.utcnow().strftime('%Y%m%d')}-{richiesta.id}"
    
    db.session.commit()
    
    flash(f"Istruttoria conclusa con successo! Protocollo: {richiesta.protocollo_istruttoria}", 'success')
    return redirect(url_for('main.dashboard'))
