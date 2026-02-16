from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from rimborsi.models import Evento, db, Richiesta, Spesa, DocumentoSpesa, Comunicazione, StatoRichiesta 
from datetime import datetime
from .forms import EventoForm, IntegrazioneRequestForm


# 1. Crea il nuovo Blueprint 'istruttoria'
istruttoria_bp = Blueprint('istruttoria', __name__, template_folder='templates', 
                           url_prefix='/istruttoria')

    
# Gestione Eventi

@istruttoria_bp.route('/gestione_eventi')
@login_required
def gestione_eventi():
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    eventi = Evento.query.order_by(Evento.data_inizio.desc()).all()
    return render_template('istruttoria/gestione_eventi.html', eventi=eventi)

# Modifica eventi

@istruttoria_bp.route('/modifica_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def modifica_evento(evento_id):
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
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
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento cancellato con successo!', 'success')
    return redirect(url_for('istruttoria.gestione_eventi'))

# Crea evento

@istruttoria_bp.route('/crea_evento', methods=['GET', 'POST'])
@login_required
def crea_evento():
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
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
    form = IntegrazioneRequestForm()  # crea il form
    # Per ora passiamo solo la richiesta, il template navigherà le relazioni
    return render_template('istruttoria/dettaglio_istruttoria.html', 
                           richiesta=richiesta, form=form, StatoRichiesta=StatoRichiesta)

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

    # Itera attraverso ogni spesa e ricalcola importo_approvato dai documenti
    for spesa in richiesta.spese:
        # Recupera le note per la spesa dal form
        spesa.note_istruttoria = request.form.get(f"note_spesa_{spesa.id}")
        # L'importo approvato viene ora calcolato dalla somma dei documenti
        spesa.importo_approvato = spesa.importo_approvato_calcolato

    # Salva tutte le modifiche nel database
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
    
    if not richiesta.spese:
        flash('Errore: Impossibile concludere un\'istruttoria senza spese.', 'danger')
        return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))
    
    # Ricalcola importo_approvato di ogni spesa dalla somma dei documenti
    for spesa in richiesta.spese:
        spesa.importo_approvato = spesa.importo_approvato_calcolato
    db.session.commit()

    # Controlla documenti non ancora verificati
    spese_non_verificate = [s for s in richiesta.spese if not s.tutti_documenti_verificati]
    if spese_non_verificate:
        flash(f'Attenzione: {len(spese_non_verificate)} spesa/e hanno documenti non ancora verificati.', 'warning')

    totale_richiesto = sum(spesa.importo_richiesto for spesa in richiesta.spese)
    totale_approvato = sum(spesa.importo_approvato or 0 for spesa in richiesta.spese)

    # Riepilogo per tipologia di spesa
    riepilogo_tipologia = {}
    for spesa in richiesta.spese:
        cat = spesa.categoria_display
        if cat not in riepilogo_tipologia:
            riepilogo_tipologia[cat] = {'richiesto': 0, 'approvato': 0}
        riepilogo_tipologia[cat]['richiesto'] += spesa.importo_richiesto or 0
        riepilogo_tipologia[cat]['approvato'] += spesa.importo_approvato or 0

    return render_template('istruttoria/riepilogo_conclusione.html', 
                           richiesta=richiesta,
                           StatoRichiesta=StatoRichiesta,
                           totale_richiesto=totale_richiesto,
                           totale_approvato=totale_approvato,
                           riepilogo_tipologia=riepilogo_tipologia)

# Rotta per la richiesta di integrazione
@istruttoria_bp.route('/<int:richiesta_id>/richiedi_integrazione', methods=['GET', 'POST'])
@login_required
def richiedi_integrazione(richiesta_id):
    richiesta = Richiesta.query.get_or_404(richiesta_id)
     # ==> AGGIUNTA: Controllo di sicurezza sullo stato
    if richiesta.stato != StatoRichiesta.IN_ISTRUTTORIA:
        flash("Azione non permessa: la richiesta non è in stato di istruttoria.", "danger")
        return redirect(url_for('main.dashboard'))

    form = IntegrazioneRequestForm()

    if form.validate_on_submit():
        # Cambia lo stato della richiesta da 'B' a 'A'
        richiesta.stato = StatoRichiesta.BOZZA

        comunicazione = Comunicazione(richiesta_id=richiesta.id)
        comunicazione.utente = current_user
        comunicazione.data_transazione = datetime.utcnow()
        protocollo = f"INT-{datetime.utcnow().strftime('%Y%m%d')}-{richiesta.id}"
        comunicazione.protocollo = protocollo
        comunicazione.stato_precedente = StatoRichiesta.IN_ISTRUTTORIA.value
        comunicazione.stato_successore = StatoRichiesta.BOZZA.value
        comunicazione.descrizione = form.motivazione.data

        db.session.add(comunicazione)
        db.session.commit()
        flash("Richiesta di integrazione inviata con successo, con protocollo: " + protocollo, "success")
        return redirect(url_for('main.dashboard'))
    
    # Form non valido
    return render_template('istruttoria/_modal_richiesta_integrazione.html', richiesta=richiesta, 
                           StatoRichiesta=StatoRichiesta, form=form)

# Rotta per la conclusione dell'istruttoria

@istruttoria_bp.route('/<int:richiesta_id>/concludi', methods=['POST'])
@login_required
def concludi_istruttoria(richiesta_id):
    """Finalizza l'istruttoria, cambia stato e salva il protocollo."""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    # ==> AGGIUNTA: Controllo di sicurezza sullo stato
    if richiesta.stato != StatoRichiesta.IN_ISTRUTTORIA: # Stato 'In Istruttoria'
        flash("Azione non permessa.", "danger")
        return redirect(url_for('main.dashboard'))
    
    # Aggiorna i campi della richiesta (qui recupererai i dati dal form di riepilogo)
    richiesta.stato = StatoRichiesta.ISTRUITA
    richiesta.esito = request.form.get('esito')
    richiesta.note_istruttoria = request.form.get('note_istruttoria')
    richiesta.data_fine_istruttoria = datetime.utcnow()
    richiesta.protocollo_istruttoria = f"ISTR-{datetime.utcnow().strftime('%Y%m%d')}-{richiesta.id}"

    # Aggiorna campi table Comunicazione

    comunicazione = Comunicazione(richiesta_id=richiesta.id)
    comunicazione.utente = current_user
    comunicazione.data_transazione = datetime.utcnow()
    comunicazione.protocollo = richiesta.protocollo_istruttoria
    comunicazione.stato_precedente = StatoRichiesta.IN_ISTRUTTORIA.value
    comunicazione.stato_successore = StatoRichiesta.ISTRUITA.value
    comunicazione.descrizione = f"Richiesta istruita con esito = {richiesta.esito}"

    db.session.add(comunicazione)

    db.session.commit()
    
    flash(f"Istruttoria conclusa con successo! Protocollo: {richiesta.protocollo_istruttoria}", 'success')
    return redirect(url_for('main.dashboard'))

# Salvataggio di tutti gli importi

# in rimborsi/istruttoria/routes.py

@istruttoria_bp.route('/<int:richiesta_id>/approva_tutti_importi', methods=['POST'])
@login_required
def approva_tutti_importi(richiesta_id):
    """Approva tutti i documenti di tutte le spese: conforme=True, importo_approvato=importo_documento."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    if richiesta.stato != StatoRichiesta.IN_ISTRUTTORIA:
        flash("Azione non permessa: la richiesta non è in stato di istruttoria.", "danger")
        return redirect(url_for('main.dashboard'))
    for spesa in richiesta.spese:
        for doc in spesa.documenti:
            doc.verificato = True
            doc.conforme = True
            doc.importo_approvato = doc.importo_documento
        spesa.importo_approvato = spesa.importo_approvato_calcolato
    db.session.commit()
    flash('Tutti i documenti di tutte le spese sono stati approvati.', 'success')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))

@istruttoria_bp.route('/<int:richiesta_id>/reset_importi', methods=['POST'])
@login_required
def reset_importi_approvati(richiesta_id):
    """Resetta tutti i campi di verifica documenti e importi approvati."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    if richiesta.stato != StatoRichiesta.IN_ISTRUTTORIA:
        flash("Azione non permessa: la richiesta non è in stato di istruttoria.", "danger")
        return redirect(url_for('main.dashboard'))
    for spesa in richiesta.spese:
        for doc in spesa.documenti:
            doc.verificato = False
            doc.conforme = None
            doc.importo_approvato = None
        spesa.importo_approvato = None
    db.session.commit()
    flash('Tutte le verifiche e gli importi approvati sono stati annullati.', 'info')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))

# in rimborsi/istruttoria/routes.py

# Reset per documenti spesa

@istruttoria_bp.route('/spese/<int:spesa_id>/verifica_tutti_documenti', methods=['POST'])
@login_required
def verifica_tutti_documenti(spesa_id):
    """Imposta 'verificato = True' per tutti i documenti di una spesa."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    spesa = Spesa.query.get_or_404(spesa_id)
    for doc in spesa.documenti:
        doc.verificato = True
    db.session.commit()
    flash(f"Tutti i documenti per la spesa #{spesa.id} sono stati contrassegnati come verificati.", 'success')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=spesa.richiesta_id))

# Annullo reset per documenti spesa

@istruttoria_bp.route('/spese/<int:spesa_id>/reset_verifica_documenti', methods=['POST'])
@login_required
def reset_verifica_documenti(spesa_id):
    """Resetta verificato, conforme e importo_approvato per tutti i documenti di una spesa."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    spesa = Spesa.query.get_or_404(spesa_id)
    for doc in spesa.documenti:
        doc.verificato = False
        doc.conforme = None
        doc.importo_approvato = None
    spesa.importo_approvato = None
    db.session.commit()
    flash(f"La verifica per i documenti della spesa #{spesa.id} è stata annullata.", 'info')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=spesa.richiesta_id))

# --- ROTTE SERVER-SIDE PER VERIFICA DOCUMENTI ---

@istruttoria_bp.route('/spese/<int:spesa_id>/salva_verifica', methods=['POST'])
@login_required
def salva_verifica_spesa(spesa_id):
    """Salva verificato, conforme, importo_approvato e note per tutti i documenti di una spesa.
    Ricalcola spesa.importo_approvato dalla somma dei documenti."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    
    spesa = Spesa.query.get_or_404(spesa_id)
    
    try:
        for doc in spesa.documenti:
            # Checkbox verificato: presente nel form = True
            doc.verificato = f"verificato_{doc.id}" in request.form
            
            # Select conforme: '', 'true', 'false' → None, True, False
            conforme_val = request.form.get(f"conforme_{doc.id}", '')
            if conforme_val == 'true':
                doc.conforme = True
            elif conforme_val == 'false':
                doc.conforme = False
            else:
                doc.conforme = None
            
            # Importo approvato del documento
            importo_str = request.form.get(f"importo_approvato_{doc.id}", '').strip()
            if importo_str:
                try:
                    doc.importo_approvato = float(importo_str.replace(',', '.'))
                except ValueError:
                    doc.importo_approvato = None
            else:
                doc.importo_approvato = None
            
            # Note istruttoria del documento
            doc.note_istruttoria = request.form.get(f"note_documento_{doc.id}", '').strip() or None
        
        # Ricalcola importo_approvato della spesa dalla somma dei documenti
        spesa.importo_approvato = spesa.importo_approvato_calcolato
        
        # Note istruttoria della spesa (opzionale, se presente nel form)
        note_spesa = request.form.get('note_spesa', '').strip()
        if note_spesa:
            spesa.note_istruttoria = note_spesa
        
        db.session.commit()
        flash(f"Verifica documenti della spesa #{spesa.id} salvata con successo.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Errore durante il salvataggio: {e}", "danger")
    
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=spesa.richiesta_id))


@istruttoria_bp.route('/spese/<int:spesa_id>/approva_tutti_documenti', methods=['POST'])
@login_required
def approva_tutti_documenti_spesa(spesa_id):
    """Approva tutti i documenti di una spesa: verificato=True, conforme=True, importo_approvato=importo_documento."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    
    spesa = Spesa.query.get_or_404(spesa_id)
    
    for doc in spesa.documenti:
        doc.verificato = True
        doc.conforme = True
        doc.importo_approvato = doc.importo_documento
    
    spesa.importo_approvato = spesa.importo_approvato_calcolato
    db.session.commit()
    flash(f"Tutti i documenti della spesa #{spesa.id} sono stati approvati.", 'success')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=spesa.richiesta_id))


@istruttoria_bp.route('/spese/<int:spesa_id>/reset_verifica', methods=['POST'])
@login_required
def reset_verifica_spesa(spesa_id):
    """Resetta tutti i campi di verifica documenti di una spesa."""
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    
    spesa = Spesa.query.get_or_404(spesa_id)
    
    for doc in spesa.documenti:
        doc.verificato = False
        doc.conforme = None
        doc.importo_approvato = None
        doc.note_istruttoria = None
    
    spesa.importo_approvato = None
    db.session.commit()
    flash(f"La verifica della spesa #{spesa.id} è stata resettata.", 'info')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=spesa.richiesta_id))

# Rotta per visualizzare il log delle comunicazioni

@istruttoria_bp.route('/<int:richiesta_id>/comunicazioni')
@login_required
def visualizza_comunicazioni(richiesta_id):
    # Verifica che l'utente sia un istruttore
    if current_user.role != 'istruttore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    comunicazioni = Comunicazione.query.filter_by(richiesta_id=richiesta.id).order_by(Comunicazione.data_transazione.desc()).all()
    
    return render_template('main/comunicazioni.html', 
                          richiesta=richiesta,
                          comunicazioni=comunicazioni,
                          view_from="istruttoria",  # Variabile per adattare l'interfaccia
                          StatoRichiesta=StatoRichiesta)


