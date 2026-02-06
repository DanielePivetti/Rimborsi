from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from rimborsi.models import db, Evento, Richiesta, Organizzazione, Spesa, MezzoAttrezzatura, ImpiegoMezzoAttrezzatura, DocumentoSpesa, Comunicazione, StatoRichiesta
from .forms import RichiestaForm, SpesaForm, ImpiegoMezzoForm, DocumentoSpesaForm
import os
from flask import send_from_directory, abort # import sicuro per i file
from werkzeug.utils import secure_filename
from flask import current_app # Importa current_app per accedere alla configurazione



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

# Rotta di Modifica Richiesta
@richiesta_bp.route('/<int:richiesta_id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_richiesta(richiesta_id):
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    form = RichiestaForm(obj=richiesta)

    if form.validate_on_submit():
        # Aggiorna i campi della richiesta con i dati del form
        richiesta.attivita_svolta = form.attivita_svolta.data
        richiesta.data_inizio_attivita = form.data_inizio_attivita.data
        richiesta.data_fine_attivita = form.data_fine_attivita.data
        richiesta.numero_volontari_coinvolti = form.numero_volontari_coinvolti.data

        db.session.commit()
        flash('Richiesta modificata con successo!', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    return render_template('richiesta/crea_richiesta.html',
                           form=form,
                           richiesta=richiesta,
                           titolo="Modifica Richiesta",
                           statoRichiesta=StatoRichiesta,
                           action_url=url_for('richiesta.modifica_richiesta', richiesta_id=richiesta.id),
                           StatoRichiesta=StatoRichiesta
    )

# Rotta di cancellazione della richiesta
@richiesta_bp.route('/<int:richiesta_id>/cancella', methods=['POST'])
@login_required
def cancella_richiesta(richiesta_id):
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    # Controllo per verificare se ci soono spese o impieghi associati
    if richiesta.spese or richiesta.impieghi:
        flash('Non puoi cancellare la richiesta se ci sono spese o impieghi associati.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))
    db.session.delete(richiesta)
    db.session.commit()
    flash('Richiesta cancellata con successo.', 'success')
    return redirect(url_for('main.dashboard'))

 # Rotta per il dettaglio della richiesta
 
@richiesta_bp.route('/dettaglio/<int:richiesta_id>')
@login_required
def dettaglio_richiesta(richiesta_id):
    """
    Mostra la pagina di dettaglio (il "tavolo da lavoro") per una richiesta in bozza.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # In futuro, qui aggiungeremo le query per caricare spese, mezzi, etc.

    # Corretto: renderizziamo un template invece di reindirizzare alla stessa route
    comunicazioni = Comunicazione.query.filter_by(richiesta_id=richiesta.id).order_by(Comunicazione.data_transazione.desc()).all()
    return render_template(
        'richiesta/dettaglio_richiesta.html',
        richiesta=richiesta,
        comunicazioni=comunicazioni,
        statoRichiesta=StatoRichiesta,
        StatoRichiesta=StatoRichiesta
    )

# Rotta per Impiego Mezzo

@richiesta_bp.route('/<int:richiesta_id>/impieghi/crea', methods=['GET', 'POST'])
@login_required
def crea_impiego(richiesta_id):
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    form = ImpiegoMezzoForm(organizzazione_id=richiesta.organizzazione_id)
    
    if form.validate_on_submit():
        # Creazione istanza vuota
        nuovo_impiego = ImpiegoMezzoAttrezzatura()
        nuovo_impiego.richiesta_id = richiesta.id
        nuovo_impiego.mezzo_attrezzatura_id = form.mezzo_attrezzatura.data.id
        nuovo_impiego.localita_impiego = form.localita_impiego.data
        nuovo_impiego.data_ora_inizio_impiego = form.data_ora_inizio_impiego.data
        nuovo_impiego.data_ora_fine_impiego = form.data_ora_fine_impiego.data
        nuovo_impiego.km_partenza = form.km_partenza.data
        nuovo_impiego.km_arrivo = form.km_arrivo.data
        db.session.add(nuovo_impiego)
        db.session.commit()
        flash('Impiego mezzo salvato con successo.', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    return render_template('richiesta/crea_modifica_impiego.html',
                           form=form, richiesta=richiesta, titolo="Aggiungi Impiego")

#   Rotta 'modifica_impiego' 

@richiesta_bp.route('/<int:richiesta_id>/impieghi/<int:impiego_id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_impiego(richiesta_id, impiego_id):
    # Recupera l'impiego specifico da modificare o restituisce un errore 404
    impiego = ImpiegoMezzoAttrezzatura.query.get_or_404(impiego_id)
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Popola il form con i dati dell'oggetto 'impiego' esistente
    form = ImpiegoMezzoForm(obj=impiego, organizzazione_id=richiesta.organizzazione_id)
    
    if form.validate_on_submit():
        # Invece di creare una nuova istanza, aggiorniamo l'oggetto 'impiego'
        # recuperato all'inizio con i nuovi dati validati del form.
        impiego.mezzo_attrezzatura_id = form.mezzo_attrezzatura.data.id
        impiego.localita_impiego = form.localita_impiego.data
        impiego.data_ora_inizio_impiego = form.data_ora_inizio_impiego.data
        impiego.data_ora_fine_impiego = form.data_ora_fine_impiego.data
        impiego.km_partenza = form.km_partenza.data
        impiego.km_arrivo = form.km_arrivo.data
        
        # Non serve fare db.session.add(), perché l'oggetto è già tracciato da SQLAlchemy
        db.session.commit()
        
        flash('Impiego mezzo modificato con successo.', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    # Per la richiesta GET, il form sarà già popolato con i dati esistenti
    return render_template('richiesta/crea_modifica_impiego.html',
                           form=form,
                           richiesta=richiesta,
                           titolo="Modifica Impiego",
                           impiego=impiego) # Passiamo anche l'impiego al template
 
# 
# Rotta cancella_impiego

@richiesta_bp.route('/<int:richiesta_id>/impieghi/<int:impiego_id>/cancella', methods=['POST'])
@login_required
def cancella_impiego(richiesta_id, impiego_id):
    impiego = ImpiegoMezzoAttrezzatura.query.get_or_404(impiego_id)

    # Il controllo ora funziona perché 'impiego.spese' esiste grazie alla relazione.
    # .count() è disponibile grazie a lazy='dynamic'.
    if impiego.spese.count() > 0:
        flash('Non puoi cancellare questo impiego perché è associato a una o più spese.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta_id))

    db.session.delete(impiego)
    db.session.commit()
    
    flash('Impiego mezzo cancellato con successo.', 'success')
    return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta_id))# Rotte per le spese

# Rotta per spesa

@richiesta_bp.route('/<int:richiesta_id>/spese/crea', methods=['GET', 'POST'])
@login_required
def crea_spesa(richiesta_id):
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    form = SpesaForm(richiesta_id=richiesta_id)

    if form.validate_on_submit():
        nuova_spesa = Spesa(
            richiesta_id=richiesta.id,
            categoria=form.categoria.data,
            data_spesa=form.data_spesa.data,
            descrizione_spesa=form.descrizione_spesa.data,
            importo_richiesto=form.importo_richiesto.data
        )
        db.session.add(nuova_spesa)
        db.session.commit() # Salviamo prima la spesa per ottenere un ID

        # Se è stato selezionato un impiego, lo colleghiamo alla spesa appena creata
        impiego_selezionato = form.impiego.data
        if impiego_selezionato:
            impiego_selezionato.spesa_id = nuova_spesa.id
            db.session.commit() # Salviamo l'aggiornamento dell'impiego
        
        flash('Spesa aggiunta con successo!', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    return render_template('richiesta/crea_modifica_spesa.html',
                           form=form, richiesta=richiesta, titolo="Aggiungi Nuova Spesa")

# Aggiungeremo 'modifica_spesa' e 'cancella_spesa' quando serviranno

@richiesta_bp.route('/<int:richiesta_id>/spese/<int:spesa_id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_spesa(richiesta_id, spesa_id):
    # Recupera gli oggetti esistenti o restituisce un errore 404
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Popola il form con i dati della spesa esistente
    form = SpesaForm(obj=spesa, richiesta_id=richiesta_id)

    if form.validate_on_submit():
        # Aggiorna l'oggetto 'spesa' con i nuovi dati del form
        spesa.categoria = form.categoria.data
        spesa.data_spesa = form.data_spesa.data
        spesa.descrizione_spesa = form.descrizione_spesa.data
        spesa.importo_richiesto = form.importo_richiesto.data
        
        # Gestisce il collegamento con l'impiego
        impiego_selezionato = form.impiego.data
        if impiego_selezionato:
            # Associa la spesa all'impiego selezionato
            spesa.impiego_id = impiego_selezionato.id
        else:
            # Rimuove l'associazione se nessun impiego è selezionato
            spesa.impiego_id = None
            
        db.session.commit()
        flash('Spesa modificata con successo!', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    # Al primo caricamento (GET), il template mostrerà il form pre-compilato
    return render_template('richiesta/crea_modifica_spesa.html',
                           form=form,
                           richiesta=richiesta,
                           titolo="Modifica Spesa")

# ... Cancella spesa 

@richiesta_bp.route('/<int:richiesta_id>/spese/<int:spesa_id>/cancella', methods=['POST'])
@login_required
def cancella_spesa(richiesta_id, spesa_id):
    spesa = Spesa.query.get_or_404(spesa_id)

    # --- CONTROLLO DOCUMENTI ALLEGATI ---
    # Grazie alla relazione 'documenti' nel modello Spesa, possiamo verificare
    # se la lista di documenti associati non è vuota.
    if spesa.documenti:
        flash('Non puoi cancellare la spesa perché ha dei documenti allegati. Rimuovi prima i documenti.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta_id))

    # Se non ci sono documenti, procedi con la cancellazione
    db.session.delete(spesa)
    db.session.commit()
    
    flash('Spesa cancellata con successo.', 'success')
    return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta_id))



# Rotta per la pagina di gestione dei documenti di una spesa

@richiesta_bp.route('/spese/<int:spesa_id>/documenti', methods=['GET'])
@login_required
def lista_documenti(spesa_id):
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = spesa.richiesta  # Accedi alla richiesta associata a questa spesa
    form = DocumentoSpesaForm() # Form per aggiungere nuovi documenti
    return render_template('richiesta/lista_documenti.html', 
                           spesa=spesa, form=form, richiesta=richiesta,
                           StatoRichiesta=StatoRichiesta)


# ... (le altre rotte) ...

@richiesta_bp.route('/spese/<int:spesa_id>/documenti/crea', methods=['POST'])
@login_required
def crea_documento(spesa_id):
    spesa = Spesa.query.get_or_404(spesa_id)
    form = DocumentoSpesaForm()
    TIPI_SENZA_IMPORTO = ['C', 'D']
    if form.validate_on_submit():
        nome_file_salvato = None
        # Controlla se un file è stato caricato
        if form.allegato.data:
            file = form.allegato.data
            # Rendi il nome del file sicuro
            nome_file_sicuro = secure_filename(file.filename)
            # Crea la directory uploads se non esiste
            uploads_dir = os.path.join(current_app.instance_path, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            # Crea un percorso unico per evitare sovrascritture
            percorso_salvataggio = os.path.join(uploads_dir, nome_file_sicuro)
            file.save(percorso_salvataggio)
            nome_file_salvato = nome_file_sicuro

        # --- Fallback lato backend per importo_documento ---
        tipo_doc = form.tipo_documento.data
        importo = form.importo_documento.data
        if tipo_doc in TIPI_SENZA_IMPORTO:
            importo = 0.00
        elif importo is None:
            importo = 0.00
        nuovo_doc = DocumentoSpesa(
            spesa_id=spesa.id,
            tipo_documento=tipo_doc,
            data_documento=form.data_documento.data,
            fornitore=form.fornitore.data,
            importo_documento=importo,
            nome_file=nome_file_salvato # Salva il nome del file nel DB
        )
        db.session.add(nuovo_doc)
        db.session.commit()
        flash('Documento aggiunto con successo.', 'success')
    else:
        flash('Errore nella compilazione del form.', 'danger')
        
    return redirect(url_for('richiesta.lista_documenti', spesa_id=spesa_id))

# Rotta per modificare un documento

@richiesta_bp.route('/spese/<int:spesa_id>/documenti/<int:documento_id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_documento(spesa_id, documento_id):
    # Recupera gli oggetti esistenti o restituisce un errore 404
    spesa = Spesa.query.get_or_404(spesa_id)
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    richiesta = spesa.richiesta  # <-- aggiungi questa riga
   
        # Pre-compila il form con i dati del documento esistente
    form = DocumentoSpesaForm(obj=documento)
    TIPI_SENZA_IMPORTO = ['C', 'D']
    if form.validate_on_submit():
        # Aggiorna i dati del documento con quelli inviati dal form
        documento.tipo_documento = form.tipo_documento.data
        documento.data_documento = form.data_documento.data
        documento.fornitore = form.fornitore.data
        
        # Gestisce l'aggiornamento del file, se ne viene caricato uno nuovo
        if form.allegato.data:
            file = form.allegato.data
            nome_file_sicuro = secure_filename(file.filename)
            # (Opzionale ma consigliato: qui potresti voler cancellare il vecchio file dal server)
            # Crea la directory uploads se non esiste
            uploads_dir = os.path.join(current_app.instance_path, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            percorso_salvataggio = os.path.join(uploads_dir, nome_file_sicuro)
            file.save(percorso_salvataggio)
            documento.nome_file = nome_file_sicuro

        # Applica la stessa logica di controllo per l'importo
        importo = form.importo_documento.data
        if documento.tipo_documento in TIPI_SENZA_IMPORTO:
            importo = 0.00
        elif importo is None:
            importo = 0.00
        documento.importo_documento = importo

        db.session.commit()
        flash('Documento modificato con successo.', 'success')
        # Reindirizza alla lista dei documenti della spesa
        return redirect(url_for('richiesta.lista_documenti', spesa_id=spesa.id))

    # Per le richieste GET, mostra il form pre-compilato con i dati attuali
    # Se la validazione POST fallisce, mostra il form con gli errori
    return render_template('richiesta/modifica_documento.html', 
                           form=form, 
                           spesa=spesa, 
                           documento=documento,
                           richiesta=richiesta,
                           StatoRichiesta=StatoRichiesta,
                           titolo="Modifica Documento")


# Rotta per cancellare un documento
@richiesta_bp.route('/documenti/cancella/<int:documento_id>', methods=['POST'])
@login_required
def cancella_documento(documento_id):
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    spesa_id = documento.spesa_id # Salvo l'ID per il redirect
    db.session.delete(documento)
    db.session.commit()
    flash('Documento cancellato con successo.', 'info')
    return redirect(url_for('richiesta.lista_documenti', spesa_id=spesa_id))

# Rotta per il controllo finale

# In rimborsi/richieste/routes.py

@richiesta_bp.route('/<int:richiesta_id>/controllo')
@login_required
def controlla_richiesta(richiesta_id):
    """
    Esegue i controlli finali prima della trasmissione e mostra la pagina di riepilogo.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)

    # Controllo 1: La richiesta deve avere almeno una spesa.
    if not richiesta.spese:
        flash('Errore: Impossibile trasmettere una richiesta senza spese.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    # Controllo 2: Ogni spesa deve avere almeno uno scontrino ('A') o una fattura ('B').
    for spesa in richiesta.spese:
        ha_giustificativo = any(doc.tipo_documento in ['A', 'B'] for doc in spesa.documenti)
        if not ha_giustificativo:
            flash(f"Errore: La spesa '{spesa.descrizione_spesa}' non ha uno scontrino o una fattura.", 'danger')
            return redirect(url_for('richiesta.dettaglio_richiesta', richiesta_id=richiesta.id))

    # Se tutti i controlli sono superati, mostra la pagina di riepilogo.
    return render_template('richiesta/riepilogo_controllo.html', 
                           richiesta=richiesta,
                           StatoRichiesta=StatoRichiesta)

# In rimborsi/richieste/routes.py
from datetime import datetime

# Rotta per la trasmissione della richiesta

@richiesta_bp.route('/<int:richiesta_id>/trasmetti', methods=['POST'])
@login_required
def trasmetti_richiesta(richiesta_id):
    """
    Gestisce la trasmissione e la ritrasmissione di una richiesta,
    preservando la data del primo invio.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)

    # Controlla se è la prima trasmissione verificando se la data_invio è vuota
    is_first_transmission = not richiesta.data_invio

    if is_first_transmission:
        # È il primo invio: imposta data e protocollo originali
        richiesta.data_invio = datetime.utcnow()
        richiesta.protocollo_invio = f"{datetime.utcnow().strftime('%Y%m%d')}-{richiesta.id}"
        
        descrizione_log = 'Prima trasmissione della richiesta'
        protocollo_per_log = richiesta.protocollo_invio
    else:
        # È una ritrasmissione: non modificare data_invio e protocollo_invio originali.
        # Genera un nuovo protocollo solo per questo evento di log.
        descrizione_log = 'Ritrasmissione a seguito di richiesta integrazione'
        protocollo_per_log = f"RE-TRAS-{datetime.utcnow().strftime('%Y%m%d')}-{richiesta.id}"

    # Aggiorna lo stato della richiesta (avviene in entrambi i casi)
    richiesta.stato = StatoRichiesta.IN_ISTRUTTORIA

    # Crea il record di log con la descrizione e il protocollo corretti
    comunicazione = Comunicazione(
        richiesta_id=richiesta.id,
        utente=current_user,
        data_transazione=datetime.utcnow(),
        protocollo=protocollo_per_log,
        stato_precedente= StatoRichiesta.BOZZA.value,
        stato_successore= StatoRichiesta.IN_ISTRUTTORIA.value,
        descrizione=descrizione_log
    )

    db.session.add(comunicazione)
    db.session.commit()
    
    flash(f"Richiesta trasmessa con successo! Protocollo di riferimento: {richiesta.protocollo_invio}", 'success')
    return redirect(url_for('main.dashboard'))


# Rotta per il download dei documenti
@richiesta_bp.route('/documenti/<int:documento_id>/download')
@login_required
def download_documento(documento_id):
    """Permette il download sicuro dei documenti."""
    from flask import send_from_directory, abort

    documento = DocumentoSpesa.query.get_or_404(documento_id)

    # Verifica che l'utente abbia accesso a questo documento
    spesa = documento.spesa
    richiesta = spesa.richiesta
    # Solo gli utenti autorizzati possono accedere
    if current_user.role not in ['admin', 'istruttore']:
        # Prendi tutti gli ID delle organizzazioni dell'utente
        user_org_ids = [org.id for org in current_user.organizzazioni]
        if richiesta.organizzazione.id not in user_org_ids:
            abort(403)  # Forbidden

    if not documento.nome_file:
        flash("Nessun file disponibile per questo documento.", "warning")
        return redirect(url_for('richiesta.lista_documenti', spesa_id=spesa.id))

    # Il percorso della directory uploads nell'instance folder
    uploads_dir = os.path.join(current_app.instance_path, 'uploads')

    # Invia il file al client
    return send_from_directory(uploads_dir, documento.nome_file, as_attachment=True)



# Rotta per visualizzare il log delle comunicazioni
@richiesta_bp.route('/<int:richiesta_id>/comunicazioni')
@login_required
def visualizza_comunicazioni(richiesta_id):
    """
    Visualizza lo storico delle comunicazioni per una richiesta.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'utente sia autorizzato a vedere questa richiesta
    if current_user.role != 'compilatore' and current_user.id != richiesta.user_id:
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))
    
    comunicazioni = Comunicazione.query.filter_by(richiesta_id=richiesta.id).order_by(Comunicazione.data_transazione.desc()).all()
    
    return render_template('main/comunicazioni.html', 
                          richiesta=richiesta,
                          comunicazioni=comunicazioni,
                          view_from="richiesta",  # Variabile per adattare l'interfaccia
                          StatoRichiesta=StatoRichiesta)