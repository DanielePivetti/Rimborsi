from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from rimborsi.models import db, Organizzazione, MezzoAttrezzatura
from .forms import OrganizzazioneForm, MezzoAttrezzaturaForm

anagrafica_bp = Blueprint('anagrafica', __name__, 
                         template_folder='templates',
                         url_prefix='/anagrafica')

# --- ROTTE ORGANIZZAZIONI ---

@anagrafica_bp.route('/organizzazioni')
@login_required
def lista_organizzazioni():
    organizzazioni = Organizzazione.query.order_by(Organizzazione.nome).all()
    return render_template('anagrafica/lista_organizzazioni.html', organizzazioni=organizzazioni)

@anagrafica_bp.route('/organizzazioni/crea', methods=['GET', 'POST'])
@login_required
def crea_organizzazione():
    form = OrganizzazioneForm()
    if form.validate_on_submit():
        # COMPLETAMENTO: Logica di salvataggio che mancava
        nuova_org = Organizzazione(
            nome=form.nome.data,
            acronimo=form.acronimo.data,
            codice_interno=form.codice_interno.data,
            indirizzo=form.indirizzo.data
        )
        db.session.add(nuova_org)
        db.session.commit()
        flash('Organizzazione creata con successo!', 'success')
        return redirect(url_for('anagrafica.lista_organizzazioni'))
    return render_template('anagrafica/crea_modifica_organizzazione.html', form=form, titolo="Crea Nuova Organizzazione")

@anagrafica_bp.route('/organizzazioni/modifica/<int:org_id>', methods=['GET', 'POST'])
@login_required
def modifica_organizzazione(org_id):
    org = Organizzazione.query.get_or_404(org_id)
    # CORREZIONE: Passiamo l'ID al form per il validatore personalizzato
    form = OrganizzazioneForm(obj=org, id_organizzazione=org.id)
    if form.validate_on_submit():
        form.populate_obj(org)
        db.session.commit()
        flash('Organizzazione aggiornata con successo!', 'success')
        return redirect(url_for('anagrafica.lista_organizzazioni'))
    return render_template('anagrafica/crea_modifica_organizzazione.html', form=form, titolo="Modifica Organizzazione")

# Cancellazione organizzazione

@anagrafica_bp.route('/organizzazioni/cancella/<int:org_id>', methods=['POST'])
@login_required
def cancella_organizzazione(org_id):
    """Cancella un'organizzazione solo se non ha mezzi associati."""
    # 1. Trova l'organizzazione o restituisci un errore 404
    org = Organizzazione.query.get_or_404(org_id)
    
    # 2. Controlla se l'organizzazione ha mezzi collegati
    if org.mezzi:
        # Se ne ha, blocca la cancellazione e avvisa l'utente
        flash('Non puoi cancellare questa organizzazione perché ha dei mezzi associati. Rimuovi prima quelli.', 'danger')
    else:
        # Altrimenti, procedi con la cancellazione
        db.session.delete(org)
        db.session.commit()
        flash('Organizzazione cancellata con successo.', 'success')
        
    # 3. In ogni caso, reindirizza alla lista delle organizzazioni
    return redirect(url_for('anagrafica.lista_organizzazioni'))

# --- ROTTE MEZZI ---

@anagrafica_bp.route('/mezzi')
@login_required
def lista_tutti_mezzi():
    mezzi = MezzoAttrezzatura.query.join(Organizzazione).order_by(Organizzazione.nome, MezzoAttrezzatura.targa_inventario).all()
    return render_template('anagrafica/lista_tutti_mezzi.html', mezzi=mezzi)

@anagrafica_bp.route('/organizzazioni/<int:org_id>/mezzi')
@login_required
def lista_mezzi(org_id):
    organizzazione = Organizzazione.query.get_or_404(org_id)
    return render_template('anagrafica/lista_mezzi.html', organizzazione=organizzazione)

@anagrafica_bp.route('/organizzazioni/<int:org_id>/mezzi/crea', methods=['GET', 'POST'])
@login_required
def crea_mezzo(org_id):
    organizzazione = Organizzazione.query.get_or_404(org_id)
    form = MezzoAttrezzaturaForm()
    if form.validate_on_submit():
        # COMPLETAMENTO: Logica di salvataggio che mancava
        nuovo_mezzo = MezzoAttrezzatura(
            tipologia=form.tipologia.data,
            targa_inventario=form.targa_inventario.data,
            descrizione=form.descrizione.data,
            organizzazione_id=org_id
        )
        db.session.add(nuovo_mezzo)
        db.session.commit()
        flash('Mezzo/Attrezzatura aggiunto con successo!', 'success')
        return redirect(url_for('anagrafica.lista_mezzi', org_id=org_id))
    
    # CORREZIONE: Popoliamo il campo nascosto prima di mostrare la pagina
    form.organizzazione_id.data = org_id
    return render_template('anagrafica/crea_modifica_mezzo.html', form=form, organizzazione=organizzazione, titolo="Aggiungi Mezzo/Attrezzatura")

@anagrafica_bp.route('/mezzi/modifica/<int:mezzo_id>', methods=['GET', 'POST'])
@login_required
def modifica_mezzo(mezzo_id):
    mezzo = MezzoAttrezzatura.query.get_or_404(mezzo_id)
    # CORREZIONE: Passiamo l'ID al form per il validatore personalizzato
    form = MezzoAttrezzaturaForm(obj=mezzo, id_mezzo=mezzo.id)
    if form.validate_on_submit():
        form.populate_obj(mezzo)
        db.session.commit()
        flash('Mezzo/Attrezzatura aggiornato con successo!', 'success')
        return redirect(url_for('anagrafica.lista_mezzi', org_id=mezzo.organizzazione_id))
    return render_template('anagrafica/crea_modifica_mezzo.html', form=form, organizzazione=mezzo.organizzazione, titolo="Modifica Mezzo/Attrezzatura")