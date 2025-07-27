"""
Modulo per la gestione delle tipologie di spesa e dei loro attributi.
Questo permette di centralizzare la configurazione delle tipologie di spesa
e garantisce coerenza tra modelli, viste e template.
"""
from enum import Enum
from typing import Dict, List, Optional, Union

class TipoSpesa(Enum):
    """Enumerazione per i tipi di spesa supportati."""
    CARBURANTE = "CARBURANTE"
    VITTO = "VITTO"
    PEDAGGI = "PEDAGGI"
    RIPRISTINO = "RIPRISTINO"
    PARCHEGGIO = "PARCHEGGIO"
    ALTRO = "ALTRO"

# Definizione dei campi specifici per ogni tipo di spesa
# Questo dizionario mappa ogni tipo di spesa ai suoi campi specifici
CAMPI_SPESA: Dict[TipoSpesa, List[str]] = {
    TipoSpesa.CARBURANTE: ["tipo_carburante", "litri", "impiego_mezzo_id"],
    TipoSpesa.VITTO: ["numero_pasti"],
    TipoSpesa.PEDAGGI: ["tratta", "impiego_mezzo_id"],
    TipoSpesa.RIPRISTINO: ["descrizione_intervento", "impiego_mezzo_id"],
    TipoSpesa.PARCHEGGIO: ["indirizzo", "durata_ore"],
    TipoSpesa.ALTRO: ["descrizione_dettagliata"],
}

# Etichette per i campi (per la visualizzazione nei form e nelle viste)
ETICHETTE_CAMPI: Dict[str, str] = {
    "tipo_carburante": "Tipo carburante",
    "litri": "Litri",
    "impiego_mezzo_id": "Mezzo utilizzato",
    "numero_pasti": "Numero pasti",
    "tratta": "Tratta",
    "descrizione_intervento": "Descrizione intervento",
    "indirizzo": "Indirizzo",
    "durata_ore": "Durata (ore)",
    "descrizione_dettagliata": "Descrizione dettagliata",
}

def get_campi_per_tipo(tipo_spesa: Union[TipoSpesa, str]) -> List[str]:
    """
    Restituisce i campi specifici per un dato tipo di spesa.
    
    Args:
        tipo_spesa: Il tipo di spesa (può essere una stringa o un'enumerazione TipoSpesa)
        
    Returns:
        Lista dei nomi dei campi specifici per quel tipo di spesa
    """
    if isinstance(tipo_spesa, str):
        tipo_spesa = TipoSpesa(tipo_spesa)
    return CAMPI_SPESA.get(tipo_spesa, [])

def get_etichetta_campo(nome_campo: str) -> str:
    """
    Restituisce l'etichetta leggibile per un dato campo.
    
    Args:
        nome_campo: Il nome del campo
        
    Returns:
        L'etichetta leggibile per il campo
    """
    return ETICHETTE_CAMPI.get(nome_campo, nome_campo.capitalize().replace("_", " "))
