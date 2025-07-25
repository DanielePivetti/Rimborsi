from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
from app.models.odv import Odv

def odv_access_required(view_func=None, odv_id_parameter='odv_id'):
    """
    Decoratore che verifica se l'utente corrente ha accesso all'organizzazione specificata.
    
    Args:
        view_func: La funzione view da decorare
        odv_id_parameter: Il nome del parametro che contiene l'ID dell'organizzazione nella vista
    
    Returns:
        La funzione decorata che verifica l'accesso all'organizzazione
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Ottieni l'ID dell'organizzazione dal parametro della vista
            odv_id = kwargs.get(odv_id_parameter)
            
            # Se non c'è un ID, procedi normalmente
            if odv_id is None:
                return f(*args, **kwargs)
            
            # Verifica se l'utente può accedere a questa organizzazione
            if not current_user.can_access_odv(odv_id):
                flash('Non hai accesso a questa organizzazione.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    
    if view_func:
        return decorator(view_func)
    return decorator
