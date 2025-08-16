from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

# Importa solo i modelli e i form necessari per queste rotte

from rimborsi.models import Evento, db  # Importa dal package principale 'rimborsi'
from .forms import EventoForm             # Importa il form dalla cartella corrente


# 1. Crea il nuovo Blueprint 'istruttoria'
istruttoria_bp = Blueprint('istruttoria', __name__, template_folder='templates')

    
# Gestione Eventi

@istruttoria_bp.route('/gestione_eventi')
@login_required
def gestione_eventi():
    eventi = Evento.query.order_by(Evento.data_inizio.desc()).all()
    return render_template('istruttoria/gestione_eventi.html', eventi=eventi)

# Modifica eventi

@istruttoria_bp.route('/modifica_evento/<int:evento_id>', methods=['GET', 'POST'])
@login_required
def modifica_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    form = EventoForm(obj=evento)
    if form.validate_on_submit():
        form.populate_obj(evento)
        db.session.commit()
        flash('Evento modificato con successo!', 'success')
        return redirect(url_for('istruttoria.gestione_eventi'))
    return render_template('istruttoria/crea_modifica_evento.html', form=form, evento=evento)


# Cancella evento

@istruttoria_bp.route('/cancella_evento/<int:evento_id>', methods=['POST'])
@login_required
def cancella_evento(evento_id):
    evento = Evento.query.get_or_404(evento_id)
    db.session.delete(evento)
    db.session.commit()
    flash('Evento cancellato con successo!', 'success')
    return redirect(url_for('istruttoria.gestione_eventi'))

# Crea evento

@istruttoria_bp.route('/crea_evento', methods=['GET', 'POST'])
@login_required
def crea_evento():
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento()
        form.populate_obj(evento)
        db.session.add(evento)
        db.session.commit()
        flash('Evento creato con successo!', 'success')
        return redirect(url_for('istruttoria.gestione_eventi'))
    return render_template('istruttoria/crea_modifica_evento.html', form=form)

