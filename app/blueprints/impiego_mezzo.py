from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.impiego_mezzo import ImpiegoMezzo
from app.models.mezzo import Mezzo
from app.models.evento import Evento
from app.forms.impiego_mezzo_form import ImpiegoMezzoForm
from app.utils.decorators import admin_required, istruttore_required
from datetime import datetime

impiego_mezzo_bp = Blueprint('impiego_mezzo', __name__, url_prefix='/impieghi-mezzi')

@impiego_mezzo_bp.route('/')
@login_required
def lista_impieghi():
    """Visualizza la lista degli impieghi mezzi"""
    impieghi = ImpiegoMezzo.query.all()
    return render_template('impiego_mezzo/lista_impieghi.html', impieghi=impieghi)

@impiego_mezzo_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_impiego():
    """Crea un nuovo impiego mezzo"""
    form = ImpiegoMezzoForm()
    
    # Popola le scelte dei mezzi
    form.mezzo_id.choices = [(m.id, f"{m.organizzazione.acronimo} - {m.tipologia.value} {m.targa_inventario}") 
                           for m in Mezzo.query.join(Mezzo.organizzazione).all()]
    
    # Popola le scelte degli eventi
    form.evento_id.choices = [(e.id, f"{e.nome} ({e.data_inizio.strftime('%d/%m/%Y')} - {e.data_fine.strftime('%d/%m/%Y')})") 
                            for e in Evento.query.all()]
    
    if form.validate_on_submit():
        impiego = ImpiegoMezzo(
            mezzo_id=form.mezzo_id.data,
            evento_id=form.evento_id.data,
            data_inizio=form.data_inizio.data,
            data_fine=form.data_fine.data,
            km_partenza=form.km_partenza.data,
            km_arrivo=form.km_arrivo.data,
            note=form.note.data
        )
        
        db.session.add(impiego)
        db.session.commit()
        
        flash('Impiego mezzo registrato con successo', 'success')
        return redirect(url_for('impiego_mezzo.lista_impieghi'))
    
    return render_template('impiego_mezzo/form_impiego.html', form=form, title='Nuovo Impiego Mezzo')

@impiego_mezzo_bp.route('/<int:id>')
@login_required
def dettaglio_impiego(id):
    """Visualizza i dettagli di un impiego mezzo"""
    impiego = ImpiegoMezzo.query.get_or_404(id)
    return render_template('impiego_mezzo/dettaglio_impiego.html', impiego=impiego)

@impiego_mezzo_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_impiego(id):
    """Modifica un impiego mezzo esistente"""
    impiego = ImpiegoMezzo.query.get_or_404(id)
    form = ImpiegoMezzoForm(obj=impiego)
    
    # Popola le scelte dei mezzi
    form.mezzo_id.choices = [(m.id, f"{m.organizzazione.acronimo} - {m.tipologia.value} {m.targa_inventario}") 
                           for m in Mezzo.query.join(Mezzo.organizzazione).all()]
    
    # Popola le scelte degli eventi
    form.evento_id.choices = [(e.id, f"{e.nome} ({e.data_inizio.strftime('%d/%m/%Y')} - {e.data_fine.strftime('%d/%m/%Y')})") 
                            for e in Evento.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(impiego)
        db.session.commit()
        
        flash('Impiego mezzo aggiornato con successo', 'success')
        return redirect(url_for('impiego_mezzo.dettaglio_impiego', id=impiego.id))
    
    return render_template('impiego_mezzo/form_impiego.html', form=form, title='Modifica Impiego Mezzo')

@impiego_mezzo_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
def elimina_impiego(id):
    """Elimina un impiego mezzo"""
    impiego = ImpiegoMezzo.query.get_or_404(id)
    
    # Verifica se ci sono spese associate a questo impiego
    # Non permettere l'eliminazione se ci sono spese collegate
    
    db.session.delete(impiego)
    db.session.commit()
    
    flash('Impiego mezzo eliminato con successo', 'success')
    return redirect(url_for('impiego_mezzo.lista_impieghi'))
