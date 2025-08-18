#!/usr/bin/env python
"""
Script di utilità per resettare un'istruttoria allo stato iniziale.
Ripristina i campi data_fine_istruttoria, protocollo_istruttoria, stato ed esito.
"""

import os
import sys
import click
from pathlib import Path

# Aggiungo il percorso principale dell'applicazione al path di sistema
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rimborsi import create_app, db
from rimborsi.models import Richiesta

@click.command()
@click.argument('id', type=int)
@click.option('--force', is_flag=True, help='Esegue il reset senza chiedere conferma')
def reset_istruttoria(id, force):
    """
    Resetta i campi dell'istruttoria per la richiesta specificata.
    
    ID: ID della richiesta da resettare
    """
    app = create_app()
    
    with app.app_context():
        richiesta = Richiesta.query.get(id)
        
        if not richiesta:
            click.echo(f"Errore: Richiesta con ID {id} non trovata.", err=True)
            return 1
        
        if not force:
            conferma = click.confirm(
                f"Stai per resettare l'istruttoria per la richiesta #{id} - {richiesta.organizzazione}.\n"
                "Questa azione non può essere annullata. Continuare?", 
                default=False
            )
            if not conferma:
                click.echo("Operazione annullata.")
                return 0
        
        # Reset dei campi dell'istruttoria
        richiesta.data_fine_istruttoria = None
        richiesta.protocollo_istruttoria = None
        richiesta.stato = "A"  # Assumo "A" = Attiva/Aperta
        richiesta.esito = None
        
        # Salvataggio modifiche
        db.session.commit()
        
        click.echo(f"Istruttoria per richiesta #{id} - {richiesta.organizzazione} resettata con successo.")
        return 0

if __name__ == '__main__':
    sys.exit(reset_istruttoria())
