from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models.richiesta import Richiesta, StatoRichiesta
from app.models.spesa import (
    Spesa, TipoSpesa, 
    SpesaCarburante, SpesaPedaggi, SpesaRipristino,
    SpesaVitto, SpesaParcheggio, SpesaAltro
)
from app.models.documento_spesa import DocumentoSpesa, TipoDocumento
from app.models.odv import Odv
from app.models.evento import Evento
from app.models.impiego_mezzo import ImpiegoMezzo
from app.forms.richiesta_forms import SpesaDocumentiForm, DocumentoSpesaForm
from app.utils.decorators import admin_required, istruttore_required
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, time

spesa_bp = Blueprint('spesa', __name__, url_prefix='/spese')

@spesa_bp.route('/richieste/<int:richiesta_id>/spese/documenti/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa_documenti(richiesta_id):
    """Aggiunge una nuova spesa con documenti a una richiesta di rimborso"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'utente possa aggiungere spese a questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di aggiungere spese a questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere aggiunte se la richiesta è già stata approvata o rifiutata
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile aggiungere spese a una richiesta già approvata o rifiutata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Scelta del tipo di spesa
    tipo_spesa = request.args.get('tipo', TipoSpesa.CARBURANTE.value)
    
    form = SpesaDocumentiForm()
    
    # Imposta il tipo di spesa come valore predefinito nel form
    form.tipo_spesa.data = tipo_spesa
    
    # Se il tipo di spesa richiede un impiego mezzo, popola le opzioni
    if tipo_spesa in [TipoSpesa.CARBURANTE.value, TipoSpesa.PEDAGGI.value, TipoSpesa.RIPRISTINO.value]:
        form.impiego_mezzo_id.choices = [
            (0, 'Seleziona un mezzo...'),
            *[(i.id, f"{i.mezzo.tipologia.value} {i.mezzo.targa_inventario} ({i.data_inizio.strftime('%d/%m/%Y')} - {i.data_fine.strftime('%d/%m/%Y')})")
              for i in ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()]
        ]
    
    if form.validate_on_submit():
        try:
            # Crea l'oggetto spesa appropriato in base al tipo
            if tipo_spesa == TipoSpesa.CARBURANTE.value:
                spesa = SpesaCarburante(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.CARBURANTE,
                    data_spesa=form.data_spesa.data,
                    importo_richiesto=form.importo_richiesto.data,
                    note=form.note.data,
                    impiego_mezzo_id=form.impiego_mezzo_id.data,
                    tipo_carburante=form.tipo_carburante.data,
                    litri=form.litri.data
                )
            elif tipo_spesa == TipoSpesa.PEDAGGI.value:
                spesa = SpesaPedaggi(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.PEDAGGI,
                    data_spesa=form.data_spesa.data,
                    importo_richiesto=form.importo_richiesto.data,
                    note=form.note.data,
                    impiego_mezzo_id=form.impiego_mezzo_id.data,
                    tratta=form.tratta.data
                )
            elif tipo_spesa == TipoSpesa.RIPRISTINO.value:
                spesa = SpesaRipristino(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.RIPRISTINO,
                    data_spesa=form.data_spesa.data,
                    importo_richiesto=form.importo_richiesto.data,
                    note=form.note.data,
                    impiego_mezzo_id=form.impiego_mezzo_id.data,
                    descrizione_intervento=form.descrizione_intervento.data
                )
            elif tipo_spesa == TipoSpesa.VITTO.value:
                spesa = SpesaVitto(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.VITTO,
                    data_spesa=form.data_spesa.data,
                    importo_richiesto=form.importo_richiesto.data,
                    note=form.note.data,
                    numero_pasti=form.numero_pasti.data
                )
            elif tipo_spesa == TipoSpesa.PARCHEGGIO.value:
                spesa = SpesaParcheggio(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.PARCHEGGIO,
                    data_spesa=form.data_spesa.data,
                    importo_richiesto=form.importo_richiesto.data,
                    note=form.note.data,
                    indirizzo=form.indirizzo.data,
                    durata_ore=form.durata_ore.data
                )
            else:  # TipoSpesa.ALTRO.value
                spesa = SpesaAltro(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.ALTRO,
                    data_spesa=form.data_spesa.data,
                    importo_richiesto=form.importo_richiesto.data,
                    note=form.note.data,
                    descrizione_dettagliata=form.descrizione_dettagliata.data
                )
            
            # Aggiungi la spesa
            db.session.add(spesa)
            db.session.flush()  # Per ottenere l'ID della spesa senza fare commit
            
            # Salva il documento principale (A, B o C)
            salva_documento(
                spesa_id=spesa.id,
                tipo=form.doc_tipo.data,
                numero=form.doc_numero.data,
                data=form.doc_data.data,
                descrizione=form.doc_descrizione.data,
                file=form.doc_file.data
            )
            
            # Per spese di tipo 04 (ripristino), salva anche il documento di tipo E (attestazione danno)
            if tipo_spesa == TipoSpesa.RIPRISTINO.value and form.attestazione_danno_file.data:
                salva_documento(
                    spesa_id=spesa.id,
                    tipo=TipoDocumento.ATTESTAZIONE_DANNO.value,
                    numero=None,
                    data=form.data_spesa.data,
                    descrizione="Attestazione danno per ripristino",
                    file=form.attestazione_danno_file.data
                )
            
            # Per spese di tipo 05 (parcheggio) e 06 (altro), salva anche il documento di tipo D (autorizzazione)
            if tipo_spesa in [TipoSpesa.PARCHEGGIO.value, TipoSpesa.ALTRO.value] and form.autorizzazione_file.data:
                salva_documento(
                    spesa_id=spesa.id,
                    tipo=TipoDocumento.AUTORIZZAZIONE.value,
                    numero=None,
                    data=form.data_spesa.data,
                    descrizione="Autorizzazione per spesa",
                    file=form.autorizzazione_file.data
                )
            
            # Commit delle modifiche
            db.session.commit()
            
            flash('Spesa viaggio aggiunta con successo!', 'success')
            return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Errore durante l'aggiunta della spesa: {str(e)}", exc_info=True)
            flash(f'Errore durante l\'aggiunta della spesa: {str(e)}', 'danger')
    
    return render_template(
        'richieste/form_spesa_documenti.html', 
        form=form, 
        richiesta=richiesta, 
        tipo_spesa=tipo_spesa,
        title='Aggiungi Spesa con Documenti'
    )

def salva_documento(spesa_id, tipo, numero, data, descrizione, file):
    """Funzione di utilità per salvare un documento spesa"""
    if not file:
        return None
        
    # Salva il file
    filename = secure_filename(file.filename)
    # Genera un nome file univoco
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{filename}"
    
    # Crea la cartella se non esiste
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documenti_spesa')
    os.makedirs(upload_dir, exist_ok=True)
    
    # Salva il file
    file_path = os.path.join(upload_dir, new_filename)
    file.save(file_path)
    
    # Crea il documento
    documento = DocumentoSpesa(
        spesa_id=spesa_id,
        tipo=tipo,
        numero=numero,
        data=data,
        descrizione=descrizione,
        file_path=os.path.join('documenti_spesa', new_filename)
    )
    
    db.session.add(documento)
    return documento

# NUOVE FUNZIONALITÀ

@spesa_bp.route('/aggiungi-spesa-tab/<int:richiesta_id>', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa_tab(richiesta_id):
    """Reindirizza al nuovo endpoint gestione_spese"""
    # Reindirizzamento al nuovo endpoint
    return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta_id))
                return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Si è verificato un errore: {str(e)}', 'danger')
        
        elif form_tipo == TipoSpesa.RIPRISTINO.value and manutenzione_form.validate_on_submit():
            try:
                # Crea spesa manutenzione
                spesa = SpesaRipristino(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.RIPRISTINO,
                    data_spesa=manutenzione_form.data_spesa.data,
                    importo_richiesto=manutenzione_form.importo_richiesto.data,
                    descrizione_intervento=manutenzione_form.descrizione_intervento.data,
                    note=manutenzione_form.note.data
                )
                db.session.add(spesa)
                db.session.commit()
                flash('Spesa manutenzione aggiunta con successo!', 'success')
                return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Si è verificato un errore: {str(e)}', 'danger')
        
        elif form_tipo == TipoSpesa.PARCHEGGIO.value and parcheggio_form.validate_on_submit():
            try:
                # Crea spesa viaggio
                spesa = SpesaParcheggio(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.PARCHEGGIO,
                    data_spesa=parcheggio_form.data_spesa.data,
                    importo_richiesto=parcheggio_form.importo_richiesto.data,
                    indirizzo=parcheggio_form.indirizzo.data,
                    durata_ore=parcheggio_form.durata_ore.data,
                    note=parcheggio_form.note.data
                )
                db.session.add(spesa)
                db.session.commit()
                flash('Spesa viaggio aggiunta con successo!', 'success')
                return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Si è verificato un errore: {str(e)}', 'danger')
        
        elif form_tipo == TipoSpesa.ALTRO.value and altra_spesa_form.validate_on_submit():
            try:
                # Crea altra spesa
                spesa = SpesaAltro(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.ALTRO,
                    data_spesa=altra_spesa_form.data_spesa.data,
                    importo_richiesto=altra_spesa_form.importo_richiesto.data,
                    descrizione_dettagliata=altra_spesa_form.descrizione_dettagliata.data,
                    note=altra_spesa_form.note.data
                )
                db.session.add(spesa)
                db.session.commit()
                flash('Altra spesa aggiunta con successo!', 'success')
                return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Si è verificato un errore: {str(e)}', 'danger')
        
        else:
            flash('Errore nella validazione del form. Controlla i dati inseriti.', 'danger')
    
    return render_template(
        'richieste/form_spesa_tab.html',
        richiesta=richiesta,
        form_01=carburante_form,
        form_02=pasto_form,
        form_03=pedaggio_form,
        form_04=manutenzione_form,
        form_05=parcheggio_form,
        form_06=altra_spesa_form,
        spese_carburante=spese_carburante,
        spese_vitto=spese_vitto,
        spese_pedaggi=spese_pedaggi,
        spese_ripristino=spese_ripristino,
        spese_parcheggio=spese_parcheggio,
        spese_altro=spese_altro,
        tipo_spesa=request.args.get('tipo', '01')
    )

@spesa_bp.route('/gestisci-documenti/<int:spesa_id>', methods=['GET', 'POST'])
@login_required
def gestisci_documenti(spesa_id):
    """Gestione documenti per una spesa"""
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = spesa.richiesta
    
    # Verifica dei permessi
    if not (current_user.id == richiesta.user_id or current_user.is_admin()):
        flash('Non hai i permessi per gestire i documenti di questa spesa.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    # Verifica che la richiesta sia in stato "in attesa"
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Non è possibile gestire i documenti di una richiesta che non è in attesa.', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    form = DocumentoSpesaForm()
    
    if form.validate_on_submit():
        try:
            # Salvataggio del file
            file = form.file.data
            filename = secure_filename(file.filename)
            # Generiamo un nome univoco per il file
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Assicuriamoci che la directory esista
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documenti_spesa', str(spesa_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # Salva il file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Crea nuovo documento
            documento = DocumentoSpesa(
                spesa_id=spesa_id,
                tipo=form.tipo.data,
                numero=form.numero.data,
                data=form.data.data,
                descrizione=form.descrizione.data,
                file_path=os.path.join('documenti_spesa', str(spesa_id), unique_filename)
            )
            
            db.session.add(documento)
            db.session.commit()
            
            flash('Documento aggiunto con successo!', 'success')
            return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Si è verificato un errore: {str(e)}', 'danger')
    
    return render_template(
        'richieste/documenti_spesa.html',
        form=form,
        spesa=spesa,
        documenti=spesa.documenti
    )

@spesa_bp.route('/elimina-documento/<int:documento_id>', methods=['POST'])
@login_required
def elimina_documento(documento_id):
    """Elimina un documento"""
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    spesa = documento.spesa
    richiesta = spesa.richiesta
    
    # Verifica dei permessi
    if not (current_user.id == richiesta.user_id or current_user.is_admin()):
        flash('Non hai i permessi per eliminare questo documento.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    # Verifica che la richiesta sia in stato "in attesa"
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Non è possibile eliminare documenti di una richiesta che non è in attesa.', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    try:
        # Elimina il file fisico
        if documento.file_path:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Elimina il record dal database
        db.session.delete(documento)
        db.session.commit()
        
        flash('Documento eliminato con successo!', 'success')
        return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))
    
    except Exception as e:
        db.session.rollback()
        flash(f'Si è verificato un errore durante l\'eliminazione: {str(e)}', 'danger')
        return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))

@spesa_bp.route('/download-documento/<int:documento_id>')
@login_required
def download_documento(documento_id):
    """Download di un documento"""
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    spesa = documento.spesa
    richiesta = spesa.richiesta
    
    # Verifica dei permessi (più permissiva per il download)
    if not (current_user.id == richiesta.user_id or current_user.is_admin() or current_user.is_istruttore()):
        flash('Non hai i permessi per scaricare questo documento.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    if not documento.file_path:
        flash('File non trovato.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    # Estrai il nome del file originale
    original_filename = os.path.basename(documento.file_path).split('_', 1)[1] if '_' in os.path.basename(documento.file_path) else os.path.basename(documento.file_path)
    
    directory = os.path.join(current_app.config['UPLOAD_FOLDER'], os.path.dirname(documento.file_path))
    filename = os.path.basename(documento.file_path)
    
    return send_from_directory(
        directory, 
        filename,
        as_attachment=True,
        download_name=original_filename
    )
