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
from app.forms.richiesta_forms import SpesaDocumentiForm, DocumentoSpesaForm, AggiungiSpesaForm
from app.utils.decorators import admin_required, istruttore_required
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, time

spesa_bp = Blueprint('spesa', __name__, url_prefix='/spese')

@spesa_bp.route('/richieste/<int:richiesta_id>/gestione', methods=['GET'])
@login_required
def gestione_spese(richiesta_id):
    """Visualizza e gestisce tutte le spese per una richiesta"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'utente possa visualizzare questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di visualizzare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Recupero delle spese esistenti per ogni categoria
    spese_carburante = SpesaCarburante.query.filter_by(richiesta_id=richiesta_id).all()
    spese_vitto = SpesaVitto.query.filter_by(richiesta_id=richiesta_id).all()
    spese_pedaggi = SpesaPedaggi.query.filter_by(richiesta_id=richiesta_id).all()
    spese_ripristino = SpesaRipristino.query.filter_by(richiesta_id=richiesta_id).all()
    spese_parcheggio = SpesaParcheggio.query.filter_by(richiesta_id=richiesta_id).all()
    spese_altro = SpesaAltro.query.filter_by(richiesta_id=richiesta_id).all()
    
    return render_template(
        'richieste/gestione_spese.html',
        richiesta=richiesta,
        spese_carburante=spese_carburante,
        spese_vitto=spese_vitto,
        spese_pedaggi=spese_pedaggi,
        spese_ripristino=spese_ripristino,
        spese_parcheggio=spese_parcheggio,
        spese_altro=spese_altro
    )

@spesa_bp.route('/richieste/<int:richiesta_id>/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa(richiesta_id):
    """Aggiunge una nuova spesa a una richiesta"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'utente possa aggiungere spese a questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di aggiungere spese a questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere aggiunte se la richiesta è già stata approvata o rifiutata
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile aggiungere spese a una richiesta già approvata o rifiutata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Recupera gli impieghi mezzo associati all'evento della richiesta
    impieghi_mezzo = ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()
    
    # Crea un form vuoto solo per la protezione CSRF
    form = AggiungiSpesaForm()
    
    if form.validate_on_submit():
        tipo_spesa = request.form.get('tipo_spesa')
        
        if not tipo_spesa:
            flash('Seleziona un tipo di spesa valido', 'danger')
            return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
        
        # Recupera i dati comuni a tutti i tipi di spesa
        data_spesa = request.form.get('data_spesa')
        importo_richiesto = request.form.get('importo_richiesto')
        note = request.form.get('note')
        
        try:
            data_spesa = datetime.strptime(data_spesa, '%Y-%m-%d').date()
            importo_richiesto = float(importo_richiesto)
            
            # Crea l'oggetto spesa appropriato in base al tipo
            if tipo_spesa == TipoSpesa.CARBURANTE.value:
                tipo_carburante = request.form.get('tipo_carburante')
                litri = request.form.get('litri')
                impiego_mezzo_id = request.form.get('impiego_mezzo_id')
                
                if not tipo_carburante:
                    flash('Seleziona un tipo di carburante', 'danger')
                    return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
                
                litri = float(litri) if litri else None
                impiego_mezzo_id = int(impiego_mezzo_id) if impiego_mezzo_id and impiego_mezzo_id != '0' else None
                
                spesa = SpesaCarburante(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.CARBURANTE,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    tipo_carburante=tipo_carburante,
                    litri=litri,
                    impiego_mezzo_id=impiego_mezzo_id
                )
            
            elif tipo_spesa == TipoSpesa.VITTO.value:
                numero_pasti = request.form.get('numero_pasti')
                
                if not numero_pasti:
                    flash('Inserisci il numero di pasti', 'danger')
                    return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
                
                numero_pasti = int(numero_pasti)
                
                spesa = SpesaVitto(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.VITTO,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    numero_pasti=numero_pasti
                )
            
            elif tipo_spesa == TipoSpesa.PEDAGGI.value:
                tratta = request.form.get('tratta')
                impiego_mezzo_id = request.form.get('impiego_mezzo_id')
                
                if not tratta:
                    flash('Inserisci la tratta del pedaggio', 'danger')
                    return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
                
                impiego_mezzo_id = int(impiego_mezzo_id) if impiego_mezzo_id and impiego_mezzo_id != '0' else None
                
                spesa = SpesaPedaggi(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.PEDAGGI,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    tratta=tratta,
                    impiego_mezzo_id=impiego_mezzo_id
                )
            
            elif tipo_spesa == TipoSpesa.RIPRISTINO.value:
                descrizione_intervento = request.form.get('descrizione_intervento')
                impiego_mezzo_id = request.form.get('impiego_mezzo_id')
                
                if not descrizione_intervento:
                    flash('Inserisci la descrizione dell\'intervento', 'danger')
                    return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
                
                impiego_mezzo_id = int(impiego_mezzo_id) if impiego_mezzo_id and impiego_mezzo_id != '0' else None
                
                spesa = SpesaRipristino(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.RIPRISTINO,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    descrizione_intervento=descrizione_intervento,
                    impiego_mezzo_id=impiego_mezzo_id
                )
            
            elif tipo_spesa == TipoSpesa.PARCHEGGIO.value:
                indirizzo = request.form.get('indirizzo')
                durata_ore = request.form.get('durata_ore')
                
                durata_ore = float(durata_ore) if durata_ore else None
                
                spesa = SpesaParcheggio(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.PARCHEGGIO,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    indirizzo=indirizzo,
                    durata_ore=durata_ore
                )
            
            elif tipo_spesa == TipoSpesa.ALTRO.value:
                descrizione_dettagliata = request.form.get('descrizione_dettagliata')
                
                if not descrizione_dettagliata:
                    flash('Inserisci una descrizione dettagliata', 'danger')
                    return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
                
                spesa = SpesaAltro(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.ALTRO,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    descrizione_dettagliata=descrizione_dettagliata
                )
            
            # Salva la spesa nel database
            db.session.add(spesa)
            db.session.commit()
            
            flash('Spesa aggiunta con successo! Ora puoi allegare i documenti.', 'success')
            return redirect(url_for('spesa.gestisci_documenti', spesa_id=spesa.id))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Errore durante l'aggiunta della spesa: {str(e)}", exc_info=True)
            flash(f'Errore durante l\'aggiunta della spesa: {str(e)}', 'danger')
    
    return render_template(
        'richieste/form_aggiungi_spesa.html',
        richiesta=richiesta,
        impieghi_mezzo=impieghi_mezzo,
        form=form
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
                tipo=TipoDocumento(form.tipo.data),  # Converti la stringa nell'oggetto enum
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
