from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from rimborsi.models import db, Richiesta, Comunicazione, StatoRichiesta
from datetime import datetime
from .forms import IntegrazioneRequestForm


integrazione_bp = Blueprint('integrazione', __name__, template_folder='templates',
                            url_prefix='/integrazione')


@integrazione_bp.route('/dettaglio/<int:richiesta_id>')
@login_required
def dettaglio_integrazione(richiesta_id):
    """
    Visualizza il dettaglio di una richiesta in integrazione per il compilatore.
    Mostra la motivazione della richiesta di integrazione.
    """
    richiesta = Richiesta.query.get_or_404(richiesta_id)

    # Solo compilatori della stessa organizzazione
    if current_user.role != 'compilatore':
        flash("Accesso non autorizzato.", "danger")
        return redirect(url_for('main.dashboard'))

    if not current_user.organizzazioni or richiesta.organizzazione_id not in [org.id for org in current_user.organizzazioni]:
        flash("Non hai i permessi per questa richiesta.", "danger")
        return redirect(url_for('main.dashboard'))

    if richiesta.stato != StatoRichiesta.IN_INTEGRAZIONE:
        flash("La richiesta non è in stato di integrazione.", "warning")
        return redirect(url_for('main.dashboard'))

    # Recupera l'ultima comunicazione di integrazione per mostrare la motivazione
    ultima_integrazione = Comunicazione.query.filter_by(
        richiesta_id=richiesta.id,
        stato_successore=StatoRichiesta.IN_INTEGRAZIONE.value
    ).order_by(Comunicazione.data_transazione.desc()).first()

    return render_template('integrazione/dettaglio_integrazione.html',
                           richiesta=richiesta,
                           ultima_integrazione=ultima_integrazione,
                           StatoRichiesta=StatoRichiesta)
