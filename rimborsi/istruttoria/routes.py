from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from rimborsi.models import Evento, db, Richiesta, UserMixin, Spesa, DocumentoSpesa, Comunicazione, StatoRichiesta 
from datetime import datetime
from .forms import EventoForm, IntegrazioneRequestForm 
from werkzeug.utils import secure_filename # Importa il form dalla cartella corrente


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

    # 1. Itera attraverso ogni spesa della richiesta
    for spesa in richiesta.spese:
        # Recupera l'importo approvato dal form
        importo_str = request.form.get(f"importo_approvato_{spesa.id}")
        spesa.importo_approvato = float(importo_str) if importo_str else None

        # Recupera le note per la spesa dal form
        spesa.note_istruttoria = request.form.get(f"note_spesa_{spesa.id}")

        # Non gestiamo più i documenti qui, sono gestiti separatamente
        # nella rotta salva_documenti

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
                           StatoRichiesta=StatoRichiesta,
                           totale_richiesto=totale_richiesto,
                           totale_approvato=totale_approvato)

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
    """Imposta importo_approvato = importo_richiesto per tutte le spese."""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    for spesa in richiesta.spese:
        spesa.importo_approvato = spesa.importo_richiesto
    db.session.commit()
    flash('Tutti gli importi delle spese sono stati approvati massivamente.', 'success')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))

@istruttoria_bp.route('/<int:richiesta_id>/reset_importi', methods=['POST'])
@login_required
def reset_importi_approvati(richiesta_id):
    """Resetta importo_approvato a None per tutte le spese."""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    for spesa in richiesta.spese:
        spesa.importo_approvato = None
    db.session.commit()
    flash('L\'approvazione massiva degli importi è stata annullata.', 'info')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta.id))

# in rimborsi/istruttoria/routes.py

# Reset per documenti spesa

@istruttoria_bp.route('/spese/<int:spesa_id>/verifica_tutti_documenti', methods=['POST'])
@login_required
def verifica_tutti_documenti(spesa_id):
    """Imposta 'verificato = True' per tutti i documenti di una spesa."""
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
    """Imposta 'verificato = False' per tutti i documenti di una spesa."""
    spesa = Spesa.query.get_or_404(spesa_id)
    for doc in spesa.documenti:
        doc.verificato = False
    db.session.commit()
    flash(f"La verifica per i documenti della spesa #{spesa.id} è stata annullata.", 'info')
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=spesa.richiesta_id))

# Endpoint AJAX per salvare l'importo approvato di una singola spesa
@istruttoria_bp.route('/spese/<int:spesa_id>/salva-importo-approvato', methods=['POST'])
@login_required
def salva_importo_approvato(spesa_id):
    """Salva l'importo approvato di una spesa via AJAX."""
    from flask import jsonify
    
    if current_user.role != 'istruttore':
        return jsonify({'success': False, 'message': 'Accesso non autorizzato'}), 403
    
    spesa = Spesa.query.get_or_404(spesa_id)
    
    try:
        data = request.get_json()
        importo_approvato = data.get('importo_approvato')
        
        if importo_approvato is not None:
            spesa.importo_approvato = float(importo_approvato)
        else:
            spesa.importo_approvato = None
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Importo approvato salvato con successo'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Endpoint AJAX per salvare la verifica di un singolo documento
@istruttoria_bp.route('/documenti/<int:documento_id>/salva-verifica', methods=['POST'])
@login_required
def salva_verifica_documento(documento_id):
    """Salva la verifica e le note di un documento via AJAX."""
    from flask import jsonify
    
    if current_user.role != 'istruttore':
        return jsonify({'success': False, 'message': 'Accesso non autorizzato'}), 403
    
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    
    try:
        data = request.get_json()
        documento.verificato = data.get('verificato', False)
        documento.note_istruttore = data.get('note', '')
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Documento salvato con successo'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Nuovo endpoint per salvare le verifiche dei documenti separatamente
@istruttoria_bp.route('/spese/<int:spesa_id>/documenti/salva', methods=['POST'])
@login_required
def salva_documenti(spesa_id):
    """Salva solo le verifiche e le note dei documenti di una spesa."""
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta_id = request.args.get('richiesta_id', spesa.richiesta_id)
    
    # Elabora ogni documento della spesa
    for doc in spesa.documenti:
        # La checkbox, se spuntata, sarà presente in request.form
        doc.verificato = f"verificato_{doc.id}" in request.form
        
        # Recupera le note per il documento
        doc.note_istruttore = request.form.get(f"note_documento_{doc.id}")
    
    db.session.commit()
    flash(f"Verifiche documenti per la spesa #{spesa.id} salvate con successo.", 'success')
    
    # Redirect alla pagina di dettaglio dell'istruttoria
    return redirect(url_for('istruttoria.dettaglio_istruttoria', richiesta_id=richiesta_id))

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


