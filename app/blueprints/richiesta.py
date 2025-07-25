from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.richiesta import Richiesta, StatoRichiesta
from app.models.spesa import (
    Spesa, TipoSpesa, 
    SpesaCarburante, SpesaPedaggi, SpesaRipristino,
    SpesaVitto, SpesaParcheggio, SpesaAltro
)
from app.models.giustificativo import Giustificativo, TipoGiustificativo
from app.models.odv import Odv
from app.models.evento import Evento
from app.models.impiego_mezzo import ImpiegoMezzo
from app.forms.richiesta_forms import (
    RichiestaBaseForm, 
    SpesaCarburanteForm, SpesaPedaggiForm, SpesaRipristinoForm,
    SpesaVittoForm, SpesaParcheggioForm, SpesaAltroForm,
    GiustificativoForm
)
from app.utils.decorators import admin_required, istruttore_required
from werkzeug.utils import secure_filename
import os
from datetime import datetime

richiesta_bp = Blueprint('richiesta', __name__, url_prefix='/richieste')

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
        richiesta = Richiesta(
            user_id=current_user.id,
            odv_id=form.odv_id.data,
            evento_id=form.evento_id.data,
            note_richiedente=form.note_richiedente.data,
            stato=StatoRichiesta.IN_ATTESA
        )
        
        db.session.add(richiesta)
        db.session.commit()
        
        flash('Richiesta di rimborso creata con successo. Ora aggiungi le spese.', 'success')
        return redirect(url_for('richiesta.aggiungi_spesa', richiesta_id=richiesta.id))
    
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
    
    return render_template('richieste/dettaglio_richiesta.html', richiesta=richiesta)

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
        
        form.populate_obj(richiesta)
        db.session.commit()
        
        flash('Richiesta di rimborso aggiornata con successo', 'success')
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
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

@richiesta_bp.route('/<int:richiesta_id>/spese/aggiungi', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa(richiesta_id):
    """Aggiunge una nuova spesa a una richiesta di rimborso"""
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
    
    # Selezione del form appropriato in base al tipo di spesa
    if tipo_spesa == TipoSpesa.CARBURANTE.value:
        form = SpesaCarburanteForm()
        form.impiego_mezzo_id.choices = [
            (i.id, f"{i.mezzo.tipologia.value} {i.mezzo.targa_inventario} ({i.data_inizio.strftime('%d/%m/%Y')} - {i.data_fine.strftime('%d/%m/%Y')})")
            for i in ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()
        ]
    elif tipo_spesa == TipoSpesa.PEDAGGI.value:
        form = SpesaPedaggiForm()
        form.impiego_mezzo_id.choices = [
            (i.id, f"{i.mezzo.tipologia.value} {i.mezzo.targa_inventario} ({i.data_inizio.strftime('%d/%m/%Y')} - {i.data_fine.strftime('%d/%m/%Y')})")
            for i in ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()
        ]
    elif tipo_spesa == TipoSpesa.RIPRISTINO.value:
        form = SpesaRipristinoForm()
        form.impiego_mezzo_id.choices = [
            (i.id, f"{i.mezzo.tipologia.value} {i.mezzo.targa_inventario} ({i.data_inizio.strftime('%d/%m/%Y')} - {i.data_fine.strftime('%d/%m/%Y')})")
            for i in ImpiegoMezzo.query.filter_by(evento_id=richiesta.evento_id).all()
        ]
    elif tipo_spesa == TipoSpesa.VITTO.value:
        form = SpesaVittoForm()
    elif tipo_spesa == TipoSpesa.PARCHEGGIO.value:
        form = SpesaParcheggioForm()
    else:  # TipoSpesa.ALTRO.value
        form = SpesaAltroForm()
    
    # Imposta il tipo di spesa come valore predefinito nel form
    form.tipo.data = tipo_spesa
    
    if form.validate_on_submit():
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
        
        db.session.add(spesa)
        db.session.commit()
        
        flash('Spesa aggiunta con successo. Ora aggiungi un giustificativo.', 'success')
        return redirect(url_for('richiesta.aggiungi_giustificativo', spesa_id=spesa.id))
    
    return render_template(
        'richieste/form_spesa.html', 
        form=form, 
        richiesta=richiesta, 
        tipo_spesa=tipo_spesa,
        title='Aggiungi Spesa'
    )

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
    
    form = GiustificativoForm()
    
    if form.validate_on_submit():
        # Salva il file
        file = form.file.data
        filename = secure_filename(file.filename)
        # Genera un nome file univoco
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_filename = f"{timestamp}_{filename}"
        
        # Crea la cartella se non esiste
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'giustificativi')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Salva il file
        file_path = os.path.join(upload_dir, new_filename)
        file.save(file_path)
        
        # Crea il giustificativo
        giustificativo = Giustificativo(
            spesa_id=spesa_id,
            tipo=TipoGiustificativo[form.tipo.data],
            numero=form.numero.data,
            data_emissione=form.data_emissione.data,
            emesso_da=form.emesso_da.data,
            importo=form.importo.data,
            file_path=os.path.join('giustificativi', new_filename)
        )
        
        db.session.add(giustificativo)
        db.session.commit()
        
        flash('Giustificativo aggiunto con successo', 'success')
        
        # Offri la possibilità di aggiungere un'altra spesa
        return redirect(url_for('richiesta.dettaglio_richiesta', id=richiesta.id))
    
    return render_template(
        'richieste/form_giustificativo.html', 
        form=form, 
        spesa=spesa,
        richiesta=richiesta,
        title='Aggiungi Giustificativo'
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
