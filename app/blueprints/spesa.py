from flask import Blueprint, redirect, url_for
from flask_login import login_required

# Crea il blueprint per la gestione delle spese
spesa_bp = Blueprint('spesa', __name__, url_prefix='/spese')

# Reindirizzamento della vecchia rotta a tab alla nuova interfaccia
@spesa_bp.route('/aggiungi-spesa-tab/<int:richiesta_id>', methods=['GET', 'POST'])
@login_required
def aggiungi_spesa_tab(richiesta_id):
    """Reindirizza al nuovo endpoint gestione_spese"""
    # Reindirizzamento al nuovo endpoint
    return redirect(url_for('spesa.gestione_spese', richiesta_id=richiesta_id))

