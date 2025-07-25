from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.evento import Evento
from app.forms.evento_forms import EventoForm
from app import db
from datetime import datetime
from sqlalchemy import desc

evento_bp = Blueprint('evento', __name__)

def is_istruttore():
    return current_user.is_authenticated and current_user.is_istruttore()

@evento_bp.route('/eventi')
@login_required
def lista_eventi():
    if not is_istruttore():
        flash('Non hai il permesso di accedere a questa pagina.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    eventi = Evento.query.order_by(desc(Evento.data_creazione)).all()
    return render_template('eventi/lista_eventi.html', title='Eventi', eventi=eventi)

@evento_bp.route('/eventi/nuovo', methods=['GET', 'POST'])
@login_required
def nuovo_evento():
    if not is_istruttore():
        flash('Non hai il permesso di accedere a questa pagina.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = EventoForm()
    if form.validate_on_submit():
        evento = Evento(
            tipo=form.tipo.data,
            nome=form.nome.data,
            numero_attivazione=form.numero_attivazione.data,
            data_attivazione=form.data_attivazione.data,
            luogo=form.luogo.data,
            data_inizio=form.data_inizio.data,
            data_fine=form.data_fine.data
        )
        db.session.add(evento)
        db.session.commit()
        flash('Evento creato con successo.', 'success')
        return redirect(url_for('evento.lista_eventi'))
    
    return render_template('eventi/form_evento.html', title='Nuovo Evento', form=form)

@evento_bp.route('/eventi/<int:id>')
@login_required
def dettaglio_evento(id):
    if not is_istruttore():
        flash('Non hai il permesso di accedere a questa pagina.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    evento = Evento.query.get_or_404(id)
    return render_template('eventi/dettaglio_evento.html', title='Dettaglio Evento', evento=evento)

@evento_bp.route('/eventi/<int:id>/modifica', methods=['GET', 'POST'])
@login_required
def modifica_evento(id):
    if not is_istruttore():
        flash('Non hai il permesso di accedere a questa pagina.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    evento = Evento.query.get_or_404(id)
    form = EventoForm(obj=evento)
    
    if form.validate_on_submit():
        evento.tipo = form.tipo.data
        evento.nome = form.nome.data
        evento.numero_attivazione = form.numero_attivazione.data
        evento.data_attivazione = form.data_attivazione.data
        evento.luogo = form.luogo.data
        evento.data_inizio = form.data_inizio.data
        evento.data_fine = form.data_fine.data
        db.session.commit()
        flash('Evento aggiornato con successo.', 'success')
        return redirect(url_for('evento.dettaglio_evento', id=evento.id))
    
    return render_template('eventi/form_evento.html', title='Modifica Evento', form=form, evento=evento)
