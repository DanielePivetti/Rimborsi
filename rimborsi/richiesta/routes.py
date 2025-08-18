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
    form = DocumentoSpesaForm() # Form per aggiungere nuovi documenti
    return render_template('richiesta/lista_documenti.html', spesa=spesa, form=form)

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

        nuovo_doc = DocumentoSpesa(
            spesa_id=spesa.id,
            tipo_documento=form.tipo_documento.data,
            data_documento=form.data_documento.data,
            fornitore=form.fornitore.data,
            importo_documento=form.importo_documento.data,
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

