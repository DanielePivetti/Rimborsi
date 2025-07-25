"""
Script per creare organizzazioni e mezzi di esempio.
"""
import sys
import os

# Aggiungi la directory principale al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.odv import Odv
from app.models.mezzo import Mezzo, TipologiaMezzo

app = create_app()

with app.app_context():
    # Verifica se ci sono già organizzazioni
    if Odv.query.count() > 0:
        print("Sono già presenti organizzazioni nel database. Uscita.")
        sys.exit(0)
    
    # Crea alcune organizzazioni di esempio
    odv1 = Odv(
        nome="Associazione Volontari Protezione Civile Cesena",
        acronimo="AVPC Cesena",
        provincia="Forlì-Cesena",
        comune="Cesena",
        indirizzo="Via Emilia Ponente, 123",
        pec="avpc.cesena@pec.it",
        recapito_telefonico="0547-123456",
        legale_rappresentante="Mario Rossi",
        iban="IT60X0542811101000000123456"
    )
    
    odv2 = Odv(
        nome="Gruppo Comunale Volontari Protezione Civile Rimini",
        acronimo="GCVPC Rimini",
        provincia="Rimini",
        comune="Rimini",
        indirizzo="Viale dei Volontari, 45",
        pec="protezionecivile.rimini@pec.it",
        recapito_telefonico="0541-987654",
        legale_rappresentante="Giuseppe Verdi",
        iban="IT60X0542811101000000654321"
    )
    
    odv3 = Odv(
        nome="Associazione Volontari Soccorso Ravenna",
        acronimo="AVSR",
        provincia="Ravenna",
        comune="Ravenna",
        indirizzo="Via del Soccorso, 78",
        pec="avsr.ravenna@pec.it",
        recapito_telefonico="0544-567890",
        legale_rappresentante="Anna Bianchi",
        iban="IT60X0542811101000000789012"
    )
    
    # Aggiungi le organizzazioni al database
    db.session.add(odv1)
    db.session.add(odv2)
    db.session.add(odv3)
    db.session.commit()
    
    print(f"Aggiunte {Odv.query.count()} organizzazioni di volontariato.")
    
    # Crea alcuni mezzi di esempio
    mezzi = [
        Mezzo(
            odv_id=odv1.id,
            tipologia=TipologiaMezzo.VEICOLO,
            targa_inventario="FC123AB",
            descrizione="Land Rover Defender 110"
        ),
        Mezzo(
            odv_id=odv1.id,
            tipologia=TipologiaMezzo.IDROPULITRICE,
            targa_inventario="INV-0123",
            descrizione="Idropulitrice a caldo 150 bar"
        ),
        Mezzo(
            odv_id=odv2.id,
            tipologia=TipologiaMezzo.AUTOCARRO,
            targa_inventario="RN456CD",
            descrizione="Iveco Daily 35C18"
        ),
        Mezzo(
            odv_id=odv2.id,
            tipologia=TipologiaMezzo.TORREFARO,
            targa_inventario="TF-RN-01",
            descrizione="Torre faro 6 metri con generatore"
        ),
        Mezzo(
            odv_id=odv3.id,
            tipologia=TipologiaMezzo.VEICOLO,
            targa_inventario="RA789EF",
            descrizione="Toyota Hilux doppia cabina"
        )
    ]
    
    # Aggiungi i mezzi al database
    for mezzo in mezzi:
        db.session.add(mezzo)
    
    db.session.commit()
    
    print(f"Aggiunti {Mezzo.query.count()} mezzi.")
    print("Operazione completata con successo.")
