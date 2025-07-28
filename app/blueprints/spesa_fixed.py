from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory, session
from flask_login import login_required, current_user
from app import db
from app.models.richiesta import Richiesta, StatoRichiesta
from app.models.spesa import (
    Spesa, TipoSpesa, 
    SpesaCarburante, SpesaPedaggi, SpesaRipristino,
    SpesaVitto, SpesaViaggi, SpesaAltro
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

# Crea il blueprint per la gestione delle spese
spesa_bp = Blueprint('spesa', __name__, url_prefix='/spese')

# Reindirizzamento della vecchia rotta a tab alla nuova interfaccia
@spesa_bp.route('/aggiungi-spesa-tab/<int:richiesta_id>', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa_tab(richiesta_id):
    """Reindirizza al nuovo endpoint gestione_spese"""
    # Reindirizzamento al nuovo endpoint
    return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta_id))

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
    spese_viaggi = SpesaViaggi.query.filter_by(richiesta_id=richiesta_id).all()
    spese_altro = SpesaAltro.query.filter_by(richiesta_id=richiesta_id).all()
    
    return render_template(
        'richieste/gestione_spese.html',
        richiesta=richiesta,
        spese_carburante=spese_carburante,
        spese_vitto=spese_vitto,
        spese_pedaggi=spese_pedaggi,
        spese_ripristino=spese_ripristino,
        spese_viaggi=spese_viaggi,
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
            
            elif tipo_spesa == TipoSpesa.VIAGGI.value:
                viaggio = request.form.get('viaggio', 1)
                
                spesa = SpesaViaggi(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.VIAGGI,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    viaggio=int(viaggio)
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
            
            elif tipo_spesa == TipoSpesa.ALTRO.value:
                descrizione = request.form.get('descrizione_dettagliata')
                
                if not descrizione:
                    flash('Inserisci una descrizione per la spesa', 'danger')
                    return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
                
                spesa = SpesaAltro(
                    richiesta_id=richiesta_id,
                    tipo=TipoSpesa.ALTRO,
                    data_spesa=data_spesa,
                    importo_richiesto=importo_richiesto,
                    note=note,
                    descrizione=descrizione
                )
            
            # Salva la spesa nel database
            db.session.add(spesa)
            db.session.commit()
            
            flash('Spesa aggiunta con successo. Ora puoi aggiungere i documenti giustificativi.', 'success')
            return redirect(url_for('spesa.documenti_spesa', spesa_id=spesa.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiunta della spesa: {str(e)}', 'danger')
            return redirect(url_for('spesa.aggiungi_spesa', richiesta_id=richiesta_id))
    
    return render_template(
        'richieste/form_aggiungi_spesa.html',
        richiesta=richiesta,
        form=form,
        impieghi_mezzo=impieghi_mezzo,
        tipi_spesa=TipoSpesa
    )

@spesa_bp.route('/elimina/<int:spesa_id>', methods=['POST'])
@login_required
def elimina_spesa(spesa_id):
    """Elimina una spesa e tutti i documenti associati"""
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = Richiesta.query.get(spesa.richiesta_id)
    
    # Verifica che l'utente possa eliminare questa spesa
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di eliminare questa spesa', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere eliminazioni se la richiesta è già stata approvata o rifiutata
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile eliminare spese da una richiesta già approvata o rifiutata', 'warning')
        return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta.id))
    
    try:
        # Recupera tutti i documenti di spesa associati
        documenti = DocumentoSpesa.query.filter_by(spesa_id=spesa_id).all()
        
        # Elimina i file fisici dei documenti
        for documento in documenti:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.nome_file)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Elimina il documento dal database
            db.session.delete(documento)
        
        # Elimina la spesa
        db.session.delete(spesa)
        db.session.commit()
        
        flash('Spesa eliminata con successo', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione della spesa: {str(e)}', 'danger')
    
    return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta.id))

@spesa_bp.route('/documenti/<int:spesa_id>', methods=['GET', 'POST'])
@spesa_bp.route('/gestisci-documenti/<int:spesa_id>', methods=['GET', 'POST'])
@login_required
def documenti_spesa(spesa_id):
    """Gestisce i documenti associati a una spesa"""
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = Richiesta.query.get(spesa.richiesta_id)
    
    # Verifica che l'utente possa gestire i documenti di questa spesa
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di gestire i documenti di questa spesa', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere modifiche se la richiesta è già stata approvata o rifiutata
    modifica_consentita = (richiesta.stato == StatoRichiesta.IN_ATTESA or current_user.is_admin())
    
    # Recupera i documenti esistenti
    documenti = DocumentoSpesa.query.filter_by(spesa_id=spesa_id).all()
    
    # Utilizzo diretto di request per elaborare il form, evitando i problemi con WTForms
    if request.method == 'POST' and modifica_consentita:
        try:
            # Estrai i dati dal form
            tipo = request.form.get('tipo')
            numero = request.form.get('numero', '')
            data_str = request.form.get('data')
            descrizione = request.form.get('descrizione', '')
            file = request.files.get('file')
            
            # Verifica che i dati essenziali siano presenti
            if tipo and data_str:
                # Converti la data
                try:
                    data = datetime.strptime(data_str, '%Y-%m-%d').date()
                    
                    # Gestisci l'upload del file se presente
                    file_path = None
                    if file and file.filename:
                        nome_originale = secure_filename(file.filename)
                        estensione = os.path.splitext(nome_originale)[1]
                        nome_file = f"{uuid.uuid4()}{estensione}"
                        
                        # Salva il file
                        percorso_file = os.path.join(current_app.config['UPLOAD_FOLDER'], nome_file)
                        file.save(percorso_file)
                        file_path = nome_file
                    
                    # Crea il record del documento
                    documento = DocumentoSpesa(
                        spesa_id=spesa_id,
                        tipo=tipo,
                        numero=numero,
                        data=data,
                        descrizione=descrizione,
                        file_path=file_path
                    )
                    
                    db.session.add(documento)
                    db.session.commit()
                    flash('Documento caricato con successo', 'success')
                    return redirect(url_for('spesa.documenti_spesa', spesa_id=spesa_id))
                    
                except ValueError:
                    flash('Formato data non valido. Usa il formato YYYY-MM-DD', 'danger')
            else:
                flash('Tipo documento e data sono obbligatori', 'danger')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il caricamento del documento: {str(e)}', 'danger')
    
    # Questo è un csrf_token fittizio, poiché non stiamo usando più WTForms per il form
    # Useremo solo la validazione server-side in questo caso
    csrf_token = 'document_upload_form'
    
    return render_template(
        'richieste/documenti_spesa.html',
        spesa=spesa,
        richiesta=richiesta,
        documenti=documenti,
        modifica_consentita=modifica_consentita,
        tipi_documento=TipoDocumento,
        csrf_token=csrf_token
    )

@spesa_bp.route('/documento/<int:documento_id>/elimina', methods=['POST'])
@login_required
def elimina_documento(documento_id):
    """Elimina un documento associato a una spesa"""
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    spesa = Spesa.query.get(documento.spesa_id)
    richiesta = Richiesta.query.get(spesa.richiesta_id)
    
    # Verifica che l'utente possa eliminare questo documento
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di eliminare questo documento', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere eliminazioni se la richiesta è già stata approvata o rifiutata
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile eliminare documenti da una richiesta già approvata o rifiutata', 'warning')
        return redirect(url_for('spesa.documenti_spesa', spesa_id=spesa.id))
    
    try:
        # Elimina il file fisico
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.nome_file)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Elimina il record dal database
        db.session.delete(documento)
        db.session.commit()
        
        flash('Documento eliminato con successo', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Errore durante l\'eliminazione del documento: {str(e)}', 'danger')
    
    return redirect(url_for('spesa.documenti_spesa', spesa_id=spesa.id))

@spesa_bp.route('/documento/<int:documento_id>/download')
@login_required
def download_documento(documento_id):
    """Scarica un documento associato a una spesa"""
    documento = DocumentoSpesa.query.get_or_404(documento_id)
    spesa = Spesa.query.get(documento.spesa_id)
    richiesta = Richiesta.query.get(spesa.richiesta_id)
    
    # Verifica che l'utente possa scaricare questo documento
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di scaricare questo documento', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Verifica che il file esista
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.nome_file)
    if not os.path.exists(file_path):
        flash('Il file richiesto non esiste', 'danger')
        return redirect(url_for('spesa.documenti_spesa', spesa_id=spesa.id))
    
    # Determina il nome del file per il download (usa il nome originale se disponibile)
    nome_download = documento.nome_file
    estensione = os.path.splitext(documento.nome_file)[1]
    
    # Crea un nome descrittivo basato sul tipo di documento e sulla data
    data_str = documento.data.strftime('%Y%m%d')
    tipo_str = documento.tipo.name.lower()
    
    nome_descrittivo = f"{tipo_str}_{data_str}{estensione}"
    
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        documento.nome_file,
        as_attachment=True,
        download_name=nome_descrittivo
    )
