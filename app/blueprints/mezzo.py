from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.mezzo import Mezzo, TipologiaMezzo
from app.models.odv import Odv
from app.forms.mezzo_form import MezzoForm
from app.utils.decorators import admin_required

mezzo_bp = Blueprint('mezzo', __name__, url_prefix='/mezzi')

@mezzo_bp.route('/')
@login_required
@admin_required
def lista_mezzi():
    """Visualizza la lista dei mezzi"""
    mezzi = Mezzo.query.all()
    return render_template('mezzi/lista_mezzi.html', mezzi=mezzi)

@mezzo_bp.route('/nuovo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuovo_mezzo():
    """Crea un nuovo mezzo"""
    form = MezzoForm()
    
    # Popola le scelte delle ODV
    form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in Odv.query.all()]
    
    if form.validate_on_submit():
        mezzo = Mezzo(
            odv_id=form.odv_id.data,
            tipologia=form.tipologia.data,
            targa_inventario=form.targa_inventario.data,
            descrizione=form.descrizione.data
        )
        
        db.session.add(mezzo)
        db.session.commit()
        
        flash('Mezzo creato con successo', 'success')
        return redirect(url_for('mezzo.lista_mezzi'))
    
    return render_template('mezzi/form_mezzo.html', form=form, title='Nuovo Mezzo')

@mezzo_bp.route('/<int:id>')
@login_required
@admin_required
def dettaglio_mezzo(id):
    """Visualizza i dettagli di un mezzo"""
    mezzo = Mezzo.query.get_or_404(id)
    return render_template('mezzi/dettaglio_mezzo.html', mezzo=mezzo)

@mezzo_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@admin_required
def modifica_mezzo(id):
    """Modifica un mezzo esistente"""
    mezzo = Mezzo.query.get_or_404(id)
    form = MezzoForm(obj=mezzo)
    
    # Popola le scelte delle ODV
    form.odv_id.choices = [(o.id, f"{o.nome} ({o.acronimo})") for o in Odv.query.all()]
    
    if form.validate_on_submit():
        form.populate_obj(mezzo)
        db.session.commit()
        
        flash('Mezzo aggiornato con successo', 'success')
        return redirect(url_for('mezzo.dettaglio_mezzo', id=mezzo.id))
    
    return render_template('mezzi/form_mezzo.html', form=form, title='Modifica Mezzo')

@mezzo_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@admin_required
def elimina_mezzo(id):
    """Elimina un mezzo"""
    mezzo = Mezzo.query.get_or_404(id)
    
    db.session.delete(mezzo)
    db.session.commit()
    
    flash('Mezzo eliminato con successo', 'success')
    return redirect(url_for('mezzo.lista_mezzi'))
