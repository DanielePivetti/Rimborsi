"""
Script per verificare le organizzazioni esistenti
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.odv import Odv

app = create_app()

with app.app_context():
    odv_list = Odv.query.all()
    for odv in odv_list:
        print(f"ID: {odv.id}, Nome: {odv.nome}, Acronimo: {odv.acronimo}, Codice Interno: {odv.codice_interno}")
