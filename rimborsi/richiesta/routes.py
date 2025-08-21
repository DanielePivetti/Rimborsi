from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from rimborsi.models import db, Evento, Richiesta, Organizzazione, Spesa, MezzoAttrezzatura, ImpiegoMezzoAttrezzatura, DocumentoSpesa
from .forms import RichiestaForm, SpesaForm, ImpiegoMezzoForm, DocumentoSpesaForm

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

# Aggiungeremo 'modifica_impiego' e 'cancella_impiego' quando serviranno
 


# Rotte per le spese

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

# In rimborsi/richieste/routes.py

# Assicurati di importare i modelli e form necessari
from rimborsi.models import Spesa, DocumentoSpesa
from .forms import DocumentoSpesaForm

# ... (le altre tue rotte) ...

# Rotta per la pagina di gestione dei documenti di una spesa
@richiesta_bp.route('/spese/<int:spesa_id>/documenti', methods=['GET'])
@login_required
def lista_documenti(spesa_id):
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = spesa.richiesta  # Accedi alla richiesta associata a questa spesa
    form = DocumentoSpesaForm() # Form per aggiungere nuovi documenti
    return render_template('richiesta/lista_documenti.html', spesa=spesa, form=form, richiesta=richiesta)

# Rotta per salvare un nuovo documento (chiamata dal form)
# in rimborsi/richieste/routes.py
import os
from werkzeug.utils import secure_filename
from flask import current_app # Importa current_app per accedere alla configurazione

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
            # Crea un percorso unico per evitare sovrascritture
            percorso_salvataggio = os.path.join(current_app.instance_path, 'uploads', nome_file_sicuro)
            file.save(percorso_salvataggio)
            nome_file_salvato = nome_file_sicuro

        # --- Fallback lato backend per importo_documento ---
        tipo_doc = form.tipo_documento.data
        importo = form.importo_documento.data
        if tipo_doc in TIPI_SENZA_IMPORTO:
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
    return render_template('richiesta/riepilogo_controllo.html', richiesta=richiesta)

# In rimborsi/richieste/routes.py
from datetime import datetime

# Rotta per la trasmissione della richiesta

@richiesta_bp.route('/<int:richiesta_id>/trasmetti', methods=['POST'])
@login_required
def trasmetti_richiesta(richiesta_id):
    """
    Finalizza la trasmissione della richiesta.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)

    # Aggiorna i campi della richiesta
    richiesta.stato = 'B'  # Stato: In Istruttoria
    richiesta.data_invio = datetime.utcnow()
    
    # Genera un numero di protocollo univoco (es. ANNO-MESE-GIORNO-ID)
    richiesta.protocollo_invio = f"{datetime.utcnow().strftime('%Y%m%d')}-{richiesta.id}"
    
    db.session.commit()
    
    flash(f"Richiesta trasmessa con successo! Numero di protocollo: {richiesta.protocollo_invio}", 'success')
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
    if current_user.role not in ['admin', 'istruttore'] and richiesta.organizzazione.id != current_user.organizzazione_id:
        abort(403)  # Forbidden
    
    if not documento.nome_file:
        flash("Nessun file disponibile per questo documento.", "warning")
        return redirect(url_for('richiesta.lista_documenti', spesa_id=spesa.id))
    
    # Il percorso della directory uploads nell'instance folder
    uploads_dir = os.path.join(current_app.instance_path, 'uploads')
    
    # Invia il file al client
    return send_from_directory(uploads_dir, documento.nome_file, as_attachment=True)