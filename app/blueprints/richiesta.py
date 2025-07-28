from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
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
from app.models.mezzo import Mezzo
from app.forms.richiesta_forms import (
    RichiestaBaseForm, 
    SpesaCarburanteForm, SpesaPedaggiForm, SpesaRipristinoForm,
    SpesaVittoForm, SpesaViaggiForm, SpesaAltroForm,
    DocumentoSpesaForm
)
from app.forms.impiego_mezzo_form import ImpiegoMezzoForm
from app.utils.decorators import admin_required, istruttore_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime, time

richiesta_bp = Blueprint('richiesta', __name__, url_prefix='/richieste')

# Reindirizzamento dalle vecchie route alla nuova interfaccia
@richiesta_bp.route('/<int:richiesta_id>/spese/documenti/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa_documenti(richiesta_id):
    """Reindirizza alla nuova interfaccia di gestione spese"""
    return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta_id))

@richiesta_bp.route('/spese/modifica/<int:spesa_id>', methods=['GET', 'POST'])
@login_required
def modifica_spesa(spesa_id):
    """Reindirizza alla nuova interfaccia di gestione spese"""
    # Ottieni la richiesta associata alla spesa
    spesa = Spesa.query.get_or_404(spesa_id)
    return redirect(url_for('spesa.gestione_spese', richiesta_id=spesa.richiesta_id))

@richiesta_bp.route('/spese/elimina/<int:spesa_id>', methods=['POST'])
@login_required
def elimina_spesa(spesa_id):
    """Elimina una spesa"""
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta_id = spesa.richiesta_id
    
    # Verifica dei permessi
    if not (current_user.id == spesa.richiesta.user_id or current_user.is_admin()):
        flash('Non hai i permessi per eliminare questa spesa.', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Verifica che la richiesta sia in stato "in attesa"
    if spesa.richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Non è possibile eliminare una spesa di una richiesta che non è in attesa.', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    try:
        # Elimina i documenti associati
        for documento in spesa.documenti:
            db.session.delete(documento)
        
        # Elimina la spesa
        db.session.delete(spesa)
        db.session.commit()
        flash('Spesa eliminata con successo', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Errore durante l'eliminazione della spesa: {str(e)}", exc_info=True)
        flash(f'Errore durante l\'eliminazione della spesa: {str(e)}', 'danger')
    
    return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))

@richiesta_bp.route('/')
@login_required
def lista_richieste():
    """Visualizza la lista delle richieste di rimborso"""
    # Gli amministratori vedono tutte le richieste
    if current_user.is_admin():
        richieste = Richiesta.query.all()
    # Gli istruttori vedono le richieste in attesa
    elif current_user.is_istruttore():
        richieste = Richiesta.query.filter_by(stato=StatoRichiesta.IN_ATTESA).all()
    # Gli utenti normali vedono solo le proprie richieste
    else:
        richieste = Richiesta.query.filter_by(user_id=current_user.id).all()
        
    return render_template('richieste/lista_richieste.html', richieste=richieste)

@richiesta_bp.route('/nuova', methods=['GET', 'POST'])
@login_required
def nuova_richiesta():
    """Crea una nuova richiesta di rimborso"""
    form = RichiestaBaseForm()
    
    # Popola le scelte delle ODV in base al ruolo dell'utente
    if current_user.is_admin() or current_user.is_istruttore():
        # Admin e istruttori possono vedere tutte le organizzazioni
        form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in Odv.query.all()]
    else:
        # I compilatori possono vedere solo le organizzazioni a cui sono associati
        form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in current_user.organizzazioni.all()]
        
        # Se l'utente non ha organizzazioni associate, mostra un messaggio
        if not form.odv_id.choices:
            flash('Non hai organizzazioni associate al tuo account. Contatta un amministratore.', 'warning')
            return redirect(url_for('richiesta.lista_richieste'))
    
    # Popola le scelte degli eventi
    form.evento_id.choices = [(e.id, f"{e.nome} ({e.data_inizio.strftime('%d/%m/%Y')} - {e.data_fine.strftime('%d/%m/%Y')})") 
                            for e in Evento.query.all()]
    
    if form.validate_on_submit():
        try:
            # Log dei dati del form
            current_app.logger.info(f"Form data: {form.data}")
            
            # Converti date.date in datetime.datetime se necessario
            data_inizio = form.data_inizio_attivita.data
            data_fine = form.data_fine_attivita.data
            
            # Se sono oggetti date, convertili in datetime
            if hasattr(data_inizio, 'year') and not hasattr(data_inizio, 'hour'):
                data_inizio = datetime.combine(data_inizio, datetime.min.time())
            
            if hasattr(data_fine, 'year') and not hasattr(data_fine, 'hour'):
                data_fine = datetime.combine(data_fine, datetime.min.time())
            
            richiesta = Richiesta(
                user_id=current_user.id,
                odv_id=form.odv_id.data,
                evento_id=form.evento_id.data,
                note_richiedente=form.note_richiedente.data,
                stato=StatoRichiesta.IN_ATTESA,
                # Aggiunti nuovi campi
                attivita_svolta=form.attivita_svolta.data,
                data_inizio_attivita=data_inizio,
                data_fine_attivita=data_fine,
                volontari_impiegati=form.volontari_impiegati.data
            )
            
            # Log dell'oggetto richiesta
            current_app.logger.info(f"Richiesta object: {richiesta.__dict__}")
            
            db.session.add(richiesta)
            db.session.commit()
            
            flash('Richiesta di rimborso creata con successo. Ora aggiungi le spese.', 'success')
            return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante il salvataggio della richiesta: {str(e)}', 'danger')
            current_app.logger.error(f"Errore durante il salvataggio della richiesta: {str(e)}", exc_info=True)
            return render_template('richieste/form_richiesta.html', form=form, title='Nuova Richiesta di Rimborso')
    
    return render_template('richieste/form_richiesta.html', form=form, title='Nuova Richiesta di Rimborso')

@richiesta_bp.route('/<int:id>')
@login_required
def dettaglio_richiesta(id):
    """Visualizza i dettagli di una richiesta di rimborso"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che l'utente possa accedere a questa richiesta
    if not current_user.is_admin() and not current_user.is_istruttore() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di visualizzare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Ottieni gli impieghi mezzi associati alla richiesta
    impieghi_mezzi = ImpiegoMezzo.query.filter_by(richiesta_id=id).all()
    
    # Form per aggiungere un nuovo impiego mezzo
    impiego_mezzo_form = ImpiegoMezzoForm()
    
    # Popola le scelte dei mezzi disponibili
    mezzi = Mezzo.query.filter_by(odv_id=richiesta.odv_id).all()
    impiego_mezzo_form.mezzo_id.choices = [(m.id, f"{m.targa_inventario} - {m.tipologia.value}") for m in mezzi]
    
    # Prepara il form per la modifica se la richiesta è in attesa
    form = None
    if richiesta.stato == StatoRichiesta.IN_ATTESA and (current_user.is_admin() or richiesta.user_id == current_user.id):
        form = RichiestaBaseForm(obj=richiesta)
        
        # Popola le scelte delle ODV in base al ruolo dell'utente
        if current_user.is_admin() or current_user.is_istruttore():
            # Admin e istruttori possono vedere tutte le organizzazioni
            form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in Odv.query.all()]
        else:
            # I compilatori possono vedere solo le organizzazioni a cui sono associati
            form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in current_user.organizzazioni.all()]
        
        # Popola le scelte degli eventi
        form.evento_id.choices = [(e.id, f"{e.nome} ({e.data_inizio.strftime('%d/%m/%Y')} - {e.data_fine.strftime('%d/%m/%Y')})") 
                                for e in Evento.query.all()]
    
    return render_template('richieste/dettaglio_richiesta.html', 
                           richiesta=richiesta, 
                           impieghi_mezzi=impieghi_mezzi,
                           impiego_mezzo_form=impiego_mezzo_form,
                           form=form,
                           title='Dettaglio Richiesta di Rimborso')

@richiesta_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_richiesta(id):
    """Modifica una richiesta di rimborso esistente"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che l'utente possa modificare questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere modifiche se la richiesta è già stata approvata o rifiutata
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile modificare una richiesta già approvata o rifiutata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    form = RichiestaBaseForm(obj=richiesta)
    
    # Popola le scelte delle ODV in base al ruolo dell'utente
    if current_user.is_admin() or current_user.is_istruttore():
        # Admin e istruttori possono vedere tutte le organizzazioni
        form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in Odv.query.all()]
    else:
        # I compilatori possono vedere solo le organizzazioni a cui sono associati
        form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in current_user.organizzazioni.all()]
        
        # Se l'utente non ha organizzazioni associate, mantenere almeno quella attuale
        if not form.odv_id.choices:
            odv_attuale = Odv.query.get(richiesta.odv_id)
            form.odv_id.choices = [(odv_attuale.id, f"{odv_attuale.nome} ({odv_attuale.acronimo})")]
    
    # Popola le scelte degli eventi
    form.evento_id.choices = [(e.id, f"{e.nome} ({e.data_inizio.strftime('%d/%m/%Y')} - {e.data_fine.strftime('%d/%m/%Y')})") 
                            for e in Evento.query.all()]
    
    if form.validate_on_submit():
        # Verifica che l'utente possa selezionare questa ODV
        if not current_user.is_admin() and not current_user.is_istruttore():
            odv_ids = [o.id for o in current_user.organizzazioni.all()]
            if form.odv_id.data not in odv_ids and form.odv_id.data != richiesta.odv_id:
                flash('Non hai il permesso di selezionare questa organizzazione', 'danger')
                return redirect(url_for('richiesta.modifica_richiesta', id=richiesta.id))
        
        try:
            # Log dei dati del form
            current_app.logger.info(f"Form data (modifica): {form.data}")
            
            # Salva lo stato attuale dell'oggetto per debug
            current_app.logger.info(f"Richiesta prima di populate_obj: {richiesta.__dict__}")
            
            # Converti date.date in datetime.datetime se necessario
            data_inizio = form.data_inizio_attivita.data
            data_fine = form.data_fine_attivita.data
            
            # Se sono oggetti date, convertili in datetime
            if hasattr(data_inizio, 'year') and not hasattr(data_inizio, 'hour'):
                form.data_inizio_attivita.data = datetime.combine(data_inizio, time())
            
            if hasattr(data_fine, 'year') and not hasattr(data_fine, 'hour'):
                form.data_fine_attivita.data = datetime.combine(data_fine, time())
            
            form.populate_obj(richiesta)
            
            # Salva lo stato aggiornato dell'oggetto per debug
            current_app.logger.info(f"Richiesta dopo populate_obj: {richiesta.__dict__}")
            
            db.session.commit()
            
            flash('Richiesta di rimborso aggiornata con successo', 'success')
            return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Errore durante l\'aggiornamento della richiesta: {str(e)}', 'danger')
            current_app.logger.error(f"Errore durante l'aggiornamento della richiesta: {str(e)}", exc_info=True)
            return render_template('richieste/form_richiesta.html', form=form, title='Modifica Richiesta di Rimborso')
    
    return render_template('richieste/form_richiesta.html', form=form, title='Modifica Richiesta di Rimborso')

@richiesta_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
def elimina_richiesta(id):
    """Elimina una richiesta di rimborso"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che l'utente possa eliminare questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di eliminare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere l'eliminazione se la richiesta è già stata approvata
    if richiesta.stato == StatoRichiesta.APPROVATA and not current_user.is_admin():
        flash('Non è possibile eliminare una richiesta già approvata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    db.session.delete(richiesta)
    db.session.commit()
    
    flash('Richiesta di rimborso eliminata con successo', 'success')
    return redirect(url_for('richiesta.lista_richieste'))

@richiesta_bp.route('/spese/<int:spesa_id>/giustificativo/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_giustificativo(spesa_id):
    """Aggiunge un giustificativo a una spesa"""
    spesa = Spesa.query.get_or_404(spesa_id)
    richiesta = Richiesta.query.get_or_404(spesa.richiesta_id)
    
    # Verifica che l'utente possa aggiungere giustificativi a questa spesa
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di aggiungere giustificativi a questa spesa', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Non permettere aggiunte se la richiesta è già stata approvata o rifiutata
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile aggiungere giustificativi a una richiesta già approvata o rifiutata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    form = DocumentoSpesaForm()
    
    if form.validate_on_submit():
        # Salva il file
        file = form.file.data
        filename = secure_filename(file.filename)
        # Genera un nome file univoco
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        
        # Crea la cartella se non esiste
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'documenti')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salva il file
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        # Crea il documento
        documento = DocumentoSpesa(
            spesa_id=spesa_id,
            tipo=TipoDocumento[form.tipo.data],
            numero=form.numero.data,
            data=form.data.data,
            descrizione=form.descrizione.data,
            file_path=os.path.join('documenti', new_filename)
        )
        
        db.session.add(documento)
        db.session.commit()
        
        flash('Documento aggiunto con successo', 'success')
        
        # Offri la possibilità di aggiungere un'altra spesa
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    return render_template(
        'richieste/form_documento_spesa.html', 
        form=form, 
        spesa=spesa,
        richiesta=richiesta,
        title='Aggiungi Documento'
    )

@richiesta_bp.route('/<int:id>/approva', methods=['POST'])
@login_required
@istruttore_required
def approva_richiesta(id):
    """Approva una richiesta di rimborso"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che la richiesta sia in attesa
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Questa richiesta è già stata processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    # Aggiorna lo stato della richiesta
    richiesta.stato = StatoRichiesta.APPROVATA
    richiesta.approvato_da = current_user.id
    richiesta.data_approvazione = datetime.utcnow()
    
    # Aggiorna gli importi approvati per ogni spesa (in questo caso, approva tutti gli importi richiesti)
    for spesa in richiesta.spese:
        spesa.importo_approvato = spesa.importo_richiesto
    
    # Aggiorna le note dell'istruttore se presenti
    note_istruttore = request.form.get('note_istruttore')
    if note_istruttore:
        richiesta.note_istruttore = note_istruttore
    
    db.session.commit()
    
    flash('Richiesta approvata con successo', 'success')
    return redirect(url_for('richiesta.lista_richieste'))

@richiesta_bp.route('/<int:id>/rifiuta', methods=['POST'])
@login_required
@istruttore_required
def rifiuta_richiesta(id):
    """Rifiuta una richiesta di rimborso"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che la richiesta sia in attesa
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Questa richiesta è già stata processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    # Aggiorna lo stato della richiesta
    richiesta.stato = StatoRichiesta.RIFIUTATA
    richiesta.approvato_da = current_user.id
    richiesta.data_approvazione = datetime.utcnow()
    
    # Aggiorna le note dell'istruttore (obbligatorie in caso di rifiuto)
    note_istruttore = request.form.get('note_istruttore')
    if not note_istruttore:
        flash('Per rifiutare una richiesta è necessario fornire una motivazione', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    richiesta.note_istruttore = note_istruttore
    
    db.session.commit()
    
    flash('Richiesta rifiutata con successo', 'success')
    return redirect(url_for('richiesta.lista_richieste'))

@richiesta_bp.route('/<int:id>/approva-parzialmente', methods=['POST'])
@login_required
@istruttore_required
def approva_parzialmente_richiesta(id):
    """Approva parzialmente una richiesta di rimborso"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che la richiesta sia in attesa
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Questa richiesta è già stata processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    # Aggiorna lo stato della richiesta
    richiesta.stato = StatoRichiesta.PARZIALMENTE_APPROVATA
    richiesta.approvato_da = current_user.id
    richiesta.data_approvazione = datetime.utcnow()
    
    # Aggiorna gli importi approvati per ogni spesa
    for spesa in richiesta.spese:
        importo_approvato = request.form.get(f'importo_approvato_{spesa.id}')
        if importo_approvato:
            spesa.importo_approvato = float(importo_approvato)
        else:
            spesa.importo_approvato = 0  # Se non specificato, assume 0
    
    # Aggiorna le note dell'istruttore
    note_istruttore = request.form.get('note_istruttore')
    if note_istruttore:
        richiesta.note_istruttore = note_istruttore
    
    db.session.commit()
    
    flash('Richiesta approvata parzialmente con successo', 'success')
    return redirect(url_for('richiesta.lista_richieste'))

@richiesta_bp.route('/<int:richiesta_id>/impiego-mezzo/aggiungi', methods=['POST'])
@login_required
def aggiungi_impiego_mezzo(richiesta_id):
    """Aggiunge un nuovo impiego mezzo a una richiesta"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'utente possa modificare questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Verifica che la richiesta sia in stato "in attesa"
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Non è possibile modificare una richiesta che non è in attesa', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    form = ImpiegoMezzoForm()
    
    # Popola le scelte dei mezzi disponibili
    mezzi = Mezzo.query.filter_by(odv_id=richiesta.odv_id).all()
    form.mezzo_id.choices = [(m.id, f"{m.targa_inventario} - {m.tipologia.value}") for m in mezzi]
    
    if form.validate_on_submit():
        try:
            # Crea un nuovo impiego mezzo
            impiego_mezzo = ImpiegoMezzo(
                mezzo_id=form.mezzo_id.data,
                evento_id=richiesta.evento_id,
                richiesta_id=richiesta_id,
                conducente=form.conducente.data,
                localita=form.localita.data,
                data_inizio=form.data_inizio.data,
                data_fine=form.data_fine.data,
                km_partenza=form.km_partenza.data,
                km_arrivo=form.km_arrivo.data,
                note=form.note.data
            )
            
            db.session.add(impiego_mezzo)
            db.session.commit()
            flash('Impiego mezzo aggiunto con successo', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Errore durante l'aggiunta dell'impiego mezzo: {str(e)}", exc_info=True)
            flash(f'Errore durante l\'aggiunta dell\'impiego mezzo: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Errore nel campo {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))

@richiesta_bp.route('/<int:id>/inoltra', methods=['GET', 'POST'])
@login_required
def inoltra_richiesta(id):
    """Inoltra una richiesta di rimborso per l'approvazione"""
    richiesta = Richiesta.query.get_or_404(id)
    
    # Verifica che l'utente possa modificare questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di inoltrare questa richiesta', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    # Verifica che la richiesta sia in stato "in attesa"
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Non è possibile inoltrare una richiesta che non è in attesa', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    # Verifica che ci siano spese registrate
    if not richiesta.spese:
        flash('Non puoi inoltrare una richiesta senza spese registrate', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=id))
    
    try:
        # Qui in futuro potrebbe essere aggiunto uno stato "INOLTRATA" 
        # Per ora lasciamo IN_ATTESA perché è quello che gestisce l'interfaccia
        
        # Segnaliamo solo che la richiesta è stata inoltrata, senza memorizzare la data
        db.session.commit()
        flash('Richiesta inoltrata con successo', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Errore durante l'inoltro della richiesta: {str(e)}", exc_info=True)
        flash(f'Errore durante l\'inoltro della richiesta: {str(e)}', 'danger')
    
    return redirect(url_for('richiesta.dettaglio_richiesta', id=id))

@richiesta_bp.route('/<int:richiesta_id>/impiego-mezzo/<int:impiego_id>/elimina', methods=['POST'])
@login_required
def elimina_impiego_mezzo(richiesta_id, impiego_id):
    """Elimina un impiego mezzo"""
    impiego_mezzo = ImpiegoMezzo.query.get_or_404(impiego_id)
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica che l'impiego mezzo appartenga alla richiesta
    if impiego_mezzo.richiesta_id != richiesta_id:
        flash('Impiego mezzo non associato a questa richiesta', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Verifica che l'utente possa modificare questa richiesta
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Verifica che la richiesta sia in stato "in attesa"
    if richiesta.stato != StatoRichiesta.IN_ATTESA:
        flash('Non è possibile modificare una richiesta che non è in attesa', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    try:
        db.session.delete(impiego_mezzo)
        db.session.commit()
        flash('Impiego mezzo eliminato con successo', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Errore durante l'eliminazione dell'impiego mezzo: {str(e)}", exc_info=True)
        flash(f'Errore durante l\'eliminazione dell\'impiego mezzo: {str(e)}', 'danger')
    
    return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
