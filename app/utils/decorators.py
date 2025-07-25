from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            flash('Accesso negato. È richiesto il ruolo di amministratore.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def istruttore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_istruttore():
            flash('Accesso negato. È richiesto il ruolo di istruttore.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_or_istruttore_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not (current_user.is_admin() or current_user.is_istruttore()):
            flash('Accesso negato. È richiesto il ruolo di amministratore o istruttore.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function
