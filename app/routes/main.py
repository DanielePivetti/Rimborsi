from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models.user import User
from app.models.rimborso import Rimborso
from app import db
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    rimborsi = None
    if current_user.is_admin():
        # Gli amministratori vedono tutti i rimborsi
        rimborsi = Rimborso.query.order_by(Rimborso.data_richiesta.desc()).all()
    elif current_user.is_approvatore():
        # Gli approvatori vedono solo i rimborsi in attesa
        rimborsi = Rimborso.query.filter_by(stato='in_attesa').order_by(Rimborso.data_richiesta.desc()).all()
    else:
        # Gli utenti normali vedono solo i propri rimborsi
        rimborsi = Rimborso.query.filter_by(user_id=current_user.id).order_by(Rimborso.data_richiesta.desc()).all()
    
    return render_template('dashboard.html', title='Dashboard', rimborsi=rimborsi)

@main_bp.route('/rimborsi')
@login_required
def lista_rimborsi():
    rimborsi = Rimborso.query.filter_by(user_id=current_user.id).order_by(Rimborso.data_richiesta.desc()).all()
    return render_template('rimborsi.html', title='I miei rimborsi', rimborsi=rimborsi)

@main_bp.route('/rimborsi/<int:id>')
@login_required
def dettaglio_rimborso(id):
    rimborso = Rimborso.query.get_or_404(id)
    if rimborso.user_id != current_user.id and not current_user.is_approvatore():
        flash('Non hai il permesso di visualizzare questo rimborso.', 'danger')
        return redirect(url_for('main.dashboard'))
    return render_template('dettaglio_rimborso.html', title='Dettaglio rimborso', rimborso=rimborso)
