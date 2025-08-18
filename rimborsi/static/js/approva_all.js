document.addEventListener('DOMContentLoaded', function() {
    // Seleziona il pulsante "Approva Tutti"
    const approvaTuttiBtn = document.getElementById('approva-tutti-btn');
    
    // Se il pulsante esiste nella pagina...
    if (approvaTuttiBtn) {
        approvaTuttiBtn.addEventListener('click', function() {
            // Chiedi conferma all'utente
            if (confirm('Sei sicuro di voler approvare tutti gli importi richiesti?')) {
                // Trova tutte le righe della tabella delle spese
                const righeSpesa = document.querySelectorAll('.riga-spesa');
                
                righeSpesa.forEach(riga => {
                    // Per ogni riga, trova il valore richiesto e il campo approvato
                    const importoRichiestoText = riga.querySelector('.importo-richiesto').innerText;
                    const importoApprovatoInput = riga.querySelector('.importo-approvato');
                    
                    // Pulisci il testo e convertilo in numero
                    const valoreRichiesto = parseFloat(importoRichiestoText.replace('€', '').replace(/\./g, '').replace(',', '.').trim());
                    
                    // Aggiorna il valore del campo input
                    if (!isNaN(valoreRichiesto)) {
                        importoApprovatoInput.value = valoreRichiesto.toFixed(2);
                    }
                });
                
                // Ora sottometti il form per salvare i dati nel database
                document.getElementById('form-approva-tutti').submit();
            }
        });
    }
});