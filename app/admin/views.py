from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.admin import bp
from app.models.user import User
from app.models.odv import Odv
from app.admin.forms import AssociazioneUserOdvForm
from app.decorators import admin_required

@bp.route('/gestione-compilatori', methods=['GET'])
@login_required
@admin_required
def gestione_compilatori():
    """Vista per visualizzare e gestire le associazioni tra compilatori e organizzazioni."""
    users = User.query.filter_by(ruolo='utente').all()
    return render_template('admin/gestione_compilatori.html', users=users)

@bp.route('/associa-compilatore-odv/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def associa_compilatore_odv(user_id):
    """Vista per associare un compilatore a una o più organizzazioni."""
    user = User.query.get_or_404(user_id)
    form = AssociazioneUserOdvForm()
    
    # Prepopolare il form con le organizzazioni già associate
    if request.method == 'GET':
        form.organizzazioni.data = [odv.id for odv in user.organizzazioni.all()]
    
    if form.validate_on_submit():
        # Rimuovere tutte le associazioni esistenti
        user.organizzazioni = []
        db.session.commit()
        
        # Aggiungere le nuove associazioni
        for odv_id in form.organizzazioni.data:
            odv = Odv.query.get(odv_id)
            if odv:
                user.organizzazioni.append(odv)
        
        db.session.commit()
        flash(f'Le associazioni per {user.nome} {user.cognome} sono state aggiornate.', 'success')
        return redirect(url_for('admin.gestione_compilatori'))
    
    return render_template('admin/associa_compilatore_odv.html', form=form, user=user)

@bp.route('/dettaglio-compilatore/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def dettaglio_compilatore(user_id):
    """Vista per visualizzare il dettaglio delle organizzazioni associate a un compilatore."""
    user = User.query.get_or_404(user_id)
    organizzazioni = user.organizzazioni.all()
    return render_template('admin/dettaglio_compilatore.html', user=user, organizzazioni=organizzazioni)
