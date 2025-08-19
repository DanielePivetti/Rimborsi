# rimborsi/auth/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

# Importa solo i modelli e i form necessari per queste rotte
from rimborsi.models import User, db
from .forms import LoginForm, RegistrationForm

# 1. Crea il nuovo Blueprint 'auth'
auth_bp = Blueprint('auth', __name__, template_folder='templates')


# 2. Le rotte ora usano @auth_bp
@auth_bp.route('/')
def index():
    return render_template('auth/index.html')

@auth_bp.route('/registrati', methods=['GET', 'POST'])
def registrati():
    """
    Registrazione per nuovi utenti compilatori.
    L'associazione alle organizzazioni avverrà successivamente tramite l'amministratore.
    """
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Crea il nuovo utente con ruolo 'compilatore'
        nuovo_utente = User(
            username=form.username.data,
            email=form.email.data.lower(),  # Salva in minuscolo per consistenza
            password_hash=generate_password_hash(form.password.data),
            role='compilatore'  # Tutti i nuovi utenti sono compilatori
        )
        
        try:
            db.session.add(nuovo_utente)
            db.session.commit()
            
            flash(
                'Registrazione completata con successo! '
                'Un amministratore dovrà associarti a un\'organizzazione prima che tu possa iniziare a compilare richieste.',
                'success'
            )
            
            # Reindirizza alla pagina di login
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Errore durante la registrazione. Riprova più tardi.', 'danger')
    
    return render_template('auth/registrati.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # 3. Aggiorna url_for per puntare alla dashboard (che sarà in un altro blueprint)
        return redirect(url_for('main.dashboard')) # Assumiamo che la dashboard sia in un blueprint 'main'

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login effettuato con successo!', 'success')
            return redirect(url_for('main.dashboard')) # Aggiornato anche qui
        else:
            flash('Login non riuscito. Controlla email e password.', 'danger')
            
    return render_template('auth/login.html', form=form) # Il template sarà in templates/auth/

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sei stato disconnesso.', 'info')
    return redirect(url_for('auth.index')) # Aggiornato per puntare alla index di questo blueprint
