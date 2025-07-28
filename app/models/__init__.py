# app/models/__init__.py
# Questo file è necessario per rendere la cartella un pacchetto Python

from app.models.user import User
from app.models.evento import Evento
from app.models.odv import Odv
from app.models.mezzo import Mezzo, TipologiaMezzo
from app.models.impiego_mezzo import ImpiegoMezzo
from app.models.richiesta import Richiesta, StatoRichiesta
from app.models.spesa import (
    Spesa, TipoSpesa, 
    SpesaCarburante, SpesaPedaggi, SpesaRipristino,
    SpesaVitto, SpesaViaggi, SpesaAltro
)
from app.models.documento_spesa import DocumentoSpesa, TipoDocumento
