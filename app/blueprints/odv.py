from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.odv import Odv
from app.forms.odv_form import OdvForm
from app.utils.decorators import admin_required

odv_bp = Blueprint('odv', __name__, url_prefix='/odv')

@odv_bp.route('/')
@login_required
@admin_required
def lista_odv():
    """Visualizza la lista delle organizzazioni di volontariato"""
    organizazioni = Odv.query.all()
    return render_template('odv/lista_odv.html', organizazioni=organizazioni)

@odv_bp.route('/nuova', methods=['GET', 'POST'])
@login_required
@admin_required
def nuova_odv():
    """Crea una nuova organizzazione di volontariato"""
    form = OdvForm()
    
    if form.validate_on_submit():
        odv = Odv(
            nome=form.nome.data,
            acronimo=form.acronimo.data,
            codice_interno=form.codice_interno.data,
            provincia=form.provincia.data,
            comune=form.comune.data,
            indirizzo=form.indirizzo.data,
            pec=form.pec.data,
            recapito_telefonico=form.recapito_telefonico.data,
            legale_rappresentante=form.legale_rappresentante.data,
            iban=form.iban.data
        )
        
        db.session.add(odv)
        db.session.commit()
        
        flash('Organizzazione di volontariato creata con successo', 'success')
        return redirect(url_for('odv.lista_odv'))
    
    return render_template('odv/form_odv.html', form=form, title='Nuova Organizzazione')

@odv_bp.route('/<int:id>')
@login_required
@admin_required
def dettaglio_odv(id):
    """Visualizza i dettagli di un'organizzazione di volontariato"""
    odv = Odv.query.get_or_404(id)
    return render_template('odv/dettaglio_odv.html', odv=odv)

@odv_bp.route('/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
@admin_required
def modifica_odv(id):
    """Modifica un'organizzazione di volontariato esistente"""
    odv = Odv.query.get_or_404(id)
    form = OdvForm(obj=odv)
    
    if form.validate_on_submit():
        form.populate_obj(odv)
        db.session.commit()
        
        flash('Organizzazione di volontariato aggiornata con successo', 'success')
        return redirect(url_for('odv.dettaglio_odv', id=odv.id))
    
    return render_template('odv/form_odv.html', form=form, title='Modifica Organizzazione')

@odv_bp.route('/<int:id>/elimina', methods=['POST'])
@login_required
@admin_required
def elimina_odv(id):
    """Elimina un'organizzazione di volontariato"""
    odv = Odv.query.get_or_404(id)
    
    db.session.delete(odv)
    db.session.commit()
    
    flash('Organizzazione di volontariato eliminata con successo', 'success')
    return redirect(url_for('odv.lista_odv'))
