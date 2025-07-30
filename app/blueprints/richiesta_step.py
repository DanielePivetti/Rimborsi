from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
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
from app.models.richiesta_log import RichiestaLog
from app.forms.richiesta_forms import (
    RichiestaBaseForm, 
    SpesaCarburanteForm, SpesaPedaggiForm, SpesaRipristinoForm,
    SpesaVittoForm, SpesaViaggiForm, SpesaAltroForm,
    DocumentoSpesaForm
)
from app.forms.impiego_mezzo_semplificato_form import ImpiegoMezzoSemplificatoForm
from app.utils.decorators import admin_required, istruttore_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime, time

richiesta_step_bp = Blueprint('richiesta_step', __name__, url_prefix='/richieste/steps')

# Step 1: Creazione/modifica dati base della richiesta
@richiesta_step_bp.route('/nuova', methods=['GET'])
@login_required
def nuova_richiesta():
    """Inizia la creazione di una nuova richiesta"""
    # Inizializza il form per i dati base
    form = RichiestaBaseForm()
    
    # Popola le scelte per le organizzazioni
    if current_user.is_admin():
        form.odv_id.choices = [(o.id, o.nome) for o in Odv.query.all()]
    else:
        form.odv_id.choices = [(o.id, o.nome) for o in current_user.organizzazioni]
    
    # Popola le scelte per gli eventi
    form.evento_id.choices = [(e.id, e.nome) for e in Evento.query.all()]
    
    return render_template(
        'richieste/form_richiesta_step.html',
        title='Nuova Richiesta',
        form_dati_base=form,
        active_step='dati_base',
        can_access_mezzi=False,
        can_access_spese=False,
        can_access_trasmissione=False
    )

@richiesta_step_bp.route('/step/<step>/<int:richiesta_id>', methods=['GET'])
@login_required
def modifica_richiesta_step(step, richiesta_id):
    """Modifica una richiesta esistente - accesso a uno step specifico"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica dei permessi
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Verifica dello stato
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile modificare una richiesta già trasmessa o processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Flag di accesso agli step
    can_access_mezzi = True
    can_access_spese = True
    can_access_trasmissione = True

    # Logica per abilitare/disabilitare la modifica
    richiesta_modificabile = richiesta.stato == StatoRichiesta.IN_LAVORAZIONE and (current_user.id == richiesta.user_id or current_user.is_admin())
    
    # Step 1: Dati base
    if step == 'dati_base':
        form = RichiestaBaseForm(obj=richiesta)
        
        # Popola le scelte per le organizzazioni
        if current_user.is_admin():
            form.odv_id.choices = [(o.id, o.nome) for o in Odv.query.all()]
        else:
            form.odv_id.choices = [(o.id, o.nome) for o in current_user.organizzazioni]
        
        # Popola le scelte per gli eventi
        form.evento_id.choices = [(e.id, e.nome) for e in Evento.query.all()]
        
        return render_template(
            'richieste/form_richiesta_step.html',
            title='Modifica Richiesta',
            form_dati_base=form,
            richiesta=richiesta,
            active_step='dati_base',
            can_access_mezzi=can_access_mezzi,
            can_access_spese=can_access_spese,
            can_access_trasmissione=can_access_trasmissione,
            richiesta_modificabile=richiesta_modificabile
        )
    
    # Step 2: Mezzi
    elif step == 'mezzi':
        form = ImpiegoMezzoSemplificatoForm()
        # Popola le scelte per i mezzi
        form.mezzo_id.choices = [(m.id, f"{m.nome} - {m.targa}") for m in Mezzo.query.all()]
        
        # Recupera i mezzi già associati alla richiesta
        mezzi_impiegati = ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()
        
        return render_template(
            'richieste/form_richiesta_step.html',
            title='Modifica Mezzi',
            form_mezzi=form,
            richiesta=richiesta,
            mezzi_impiegati=mezzi_impiegati,
            active_step='mezzi',
            can_access_mezzi=can_access_mezzi,
            can_access_spese=can_access_spese,
            can_access_trasmissione=can_access_trasmissione,
            richiesta_modificabile=richiesta_modificabile
        )
    
    # Step 3: Spese
    elif step == 'spese':
        # Recupera le spese già associate alla richiesta
        spese = Spesa.query.filter_by(richiesta_id=richiesta_id).all()
        
        return render_template(
            'richieste/form_richiesta_step.html',
            title='Gestione Spese',
            richiesta=richiesta,
            spese=spese,
            active_step='spese',
            can_access_mezzi=can_access_mezzi,
            can_access_spese=can_access_spese,
            can_access_trasmissione=can_access_trasmissione,
            richiesta_modificabile=richiesta_modificabile
        )
    
    # Step 4: Trasmissione
    elif step == 'trasmissione':
        # Recupera i dati per il riepilogo
        mezzi_impiegati = ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()
        spese = Spesa.query.filter_by(richiesta_id=richiesta_id).all()
        
        return render_template(
            'richieste/form_richiesta_step.html',
            title='Trasmetti Richiesta',
            richiesta=richiesta,
            mezzi_impiegati=mezzi_impiegati,
            spese=spese,
            active_step='trasmissione',
            can_access_mezzi=can_access_mezzi,
            can_access_spese=can_access_spese,
            can_access_trasmissione=can_access_trasmissione,
            richiesta_modificabile=richiesta_modificabile
        )
    
    # Step non valido
    else:
        flash('Step non valido', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))

@richiesta_step_bp.route('/salva/<step>', methods=['POST'])
@richiesta_step_bp.route('/salva/<step>/<int:richiesta_id>', methods=['POST'])
@login_required
def salva_richiesta_step(step, richiesta_id=None):
    """Salva i dati di uno step specifico"""
    
    # Step 1: Salvataggio dati base
    if step == 'dati_base':
        form = RichiestaBaseForm()
        
        # Popola le scelte per le organizzazioni e gli eventi
        if current_user.is_admin():
            form.odv_id.choices = [(o.id, o.nome) for o in Odv.query.all()]
        else:
            form.odv_id.choices = [(o.id, o.nome) for o in current_user.organizzazioni]
        
        form.evento_id.choices = [(e.id, e.nome) for e in Evento.query.all()]
        
        if form.validate_on_submit():
            # Modifica di una richiesta esistente
            if richiesta_id:
                richiesta = Richiesta.query.get_or_404(richiesta_id)
                
                # Verifica dei permessi
                if not current_user.is_admin() and richiesta.user_id != current_user.id:
                    flash('Non hai il permesso di modificare questa richiesta', 'danger')
                    return redirect(url_for('richiesta.lista_richieste'))
                
                # Verifica dello stato
                if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
                    flash('Non è possibile modificare una richiesta già trasmessa o processata', 'warning')
                    return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
                
                # Aggiorna i dati
                form.populate_obj(richiesta)
                db.session.commit()
                
                # Registra evento nel log
                log = RichiestaLog(
                    richiesta_id=richiesta.id,
                    # tipo_evento rimosso
                    utente_id=current_user.id,
                    descrizione="Aggiornamento dati della richiesta"
                )
                db.session.add(log)
                db.session.commit()
                
                flash('Richiesta aggiornata con successo', 'success')
            
            # Creazione di una nuova richiesta
            else:
                richiesta = Richiesta(
                    user_id=current_user.id,
                    stato=StatoRichiesta.IN_ATTESA,
                    data_richiesta=datetime.now().date()
                )
                form.populate_obj(richiesta)
                db.session.add(richiesta)
                db.session.commit()
                
                # Registra evento nel log
                log = RichiestaLog(
                    richiesta_id=richiesta.id,
                    # tipo_evento rimosso
                    utente_id=current_user.id,
                    descrizione="Creazione della richiesta"
                )
                db.session.add(log)
                db.session.commit()
                
                flash('Richiesta creata con successo', 'success')
                richiesta_id = richiesta.id
            
            # Reindirizza allo step successivo
            return redirect(url_for('richiesta.modifica_richiesta_step', step='mezzi', richiesta_id=richiesta_id))
        
        # In caso di errori nel form
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Errore nel campo {getattr(form, field).label.text}: {error}", 'danger')
        
        # Se è una modifica, torna al form con i dati precedenti
        if richiesta_id:
            return redirect(url_for('richiesta.modifica_richiesta_step', step='dati_base', richiesta_id=richiesta_id))
        else:
            return redirect(url_for('richiesta.nuova_richiesta'))

@richiesta_step_bp.route('/aggiungi-mezzo/<int:richiesta_id>', methods=['POST'])
@login_required
def aggiungi_mezzo(richiesta_id):
    """Aggiunge un mezzo impiegato alla richiesta"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica dei permessi
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Verifica dello stato
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile modificare una richiesta già trasmessa o processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    form = ImpiegoMezzoSemplificatoForm()
    form.mezzo_id.choices = [(m.id, f"{m.nome} - {m.targa}") for m in Mezzo.query.all()]
    
    if form.validate_on_submit():
        # Crea un nuovo impiego mezzo
        impiego_mezzo = ImpiegoMezzo(
            evento_id=richiesta.evento_id,
            mezzo_id=form.mezzo_id.data,
            data_utilizzo=form.data_utilizzo.data,
            km_percorsi=form.km_percorsi.data,
            note=form.note.data
        )
        
        db.session.add(impiego_mezzo)
        db.session.commit()
        
        # Registra evento nel log
        log = RichiestaLog(
            richiesta_id=richiesta.id,
            # tipo_evento rimosso
            utente_id=current_user.id,
            descrizione=f"Aggiunto mezzo {Mezzo.query.get(form.mezzo_id.data).nome}"
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Mezzo aggiunto con successo', 'success')
    else:
        # In caso di errori nel form
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Errore nel campo {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('richiesta.modifica_richiesta_step', step='mezzi', richiesta_id=richiesta_id))

@richiesta_step_bp.route('/modifica-mezzo/<int:richiesta_id>/<int:mezzo_id>', methods=['GET', 'POST'])
@login_required
def modifica_mezzo(richiesta_id, mezzo_id):
    """Modifica un mezzo impiegato"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    impiego_mezzo = ImpiegoMezzo.query.get_or_404(mezzo_id)
    
    # Verifica dei permessi
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Verifica dello stato
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile modificare una richiesta già trasmessa o processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    form = ImpiegoMezzoSemplificatoForm(obj=impiego_mezzo)
    form.mezzo_id.choices = [(m.id, f"{m.nome} - {m.targa}") for m in Mezzo.query.all()]
    
    if request.method == 'POST' and form.validate_on_submit():
        # Aggiorna i dati
        form.populate_obj(impiego_mezzo)
        db.session.commit()
        
        # Registra evento nel log
        log = RichiestaLog(
            richiesta_id=richiesta.id,
            # tipo_evento rimosso
            utente_id=current_user.id,
            descrizione=f"Modificato mezzo {impiego_mezzo.mezzo.nome}"
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Mezzo aggiornato con successo', 'success')
        return redirect(url_for('richiesta.modifica_richiesta_step', step='mezzi', richiesta_id=richiesta_id))
    
    return render_template(
        'richieste/form_modifica_mezzo.html',
        title='Modifica Mezzo',
        form=form,
        richiesta=richiesta,
        impiego_mezzo=impiego_mezzo
    )

@richiesta_step_bp.route('/elimina-mezzo/<int:richiesta_id>/<int:mezzo_id>', methods=['POST'])
@login_required
def elimina_mezzo(richiesta_id, mezzo_id):
    """Elimina un mezzo impiegato"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    impiego_mezzo = ImpiegoMezzo.query.get_or_404(mezzo_id)
    
    # Verifica dei permessi
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Verifica dello stato
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile modificare una richiesta già trasmessa o processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    nome_mezzo = impiego_mezzo.mezzo.nome
    
    db.session.delete(impiego_mezzo)
    db.session.commit()
    
    # Registra evento nel log
    log = RichiestaLog(
        richiesta_id=richiesta.id,
        # tipo_evento rimosso
        utente_id=current_user.id,
        descrizione=f"Eliminato mezzo {nome_mezzo}"
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Mezzo eliminato con successo', 'success')
    return redirect(url_for('richiesta.modifica_richiesta_step', step='mezzi', richiesta_id=richiesta_id))

@richiesta_step_bp.route('/trasmetti/<int:richiesta_id>', methods=['POST'])
@login_required
def trasmetti_richiesta(richiesta_id):
    """Completa una richiesta"""
    richiesta = Richiesta.query.get_or_404(richiesta_id)
    
    # Verifica dei permessi
    if not current_user.is_admin() and richiesta.user_id != current_user.id:
        flash('Non hai il permesso di modificare questa richiesta', 'danger')
        return redirect(url_for('richiesta.lista_richieste'))
    
    # Verifica dello stato (mantenuto semplice)
    if richiesta.stato != StatoRichiesta.IN_ATTESA and not current_user.is_admin():
        flash('Non è possibile modificare una richiesta già trasmessa o processata', 'warning')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
    
    # Verifica dichiarazioni
    dichiarazioni = request.form.getlist('dichiarazioni[]')
    if len(dichiarazioni) < 3:
        flash('È necessario confermare tutte le dichiarazioni per completare la richiesta', 'danger')
        return redirect(url_for('richiesta.modifica_richiesta_step', step='trasmissione', richiesta_id=richiesta_id))
    
    # Per ora non cambiamo lo stato, mantenendo solo IN_ATTESA
    # richiesta.stato = StatoRichiesta.TRASMESSA
    richiesta.data_trasmissione = datetime.now()
    db.session.commit()
    
    # Registra evento nel log
    log = RichiestaLog(
        richiesta_id=richiesta.id,
        # tipo_evento rimosso
        utente_id=current_user.id,
        descrizione="Richiesta completata"
    )
    db.session.add(log)
    db.session.commit()
    
    flash('Richiesta completata con successo', 'success')
    return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta_id))
