document.addEventListener('DOMContentLoaded', function() {
    
    // --- BLOCCO 1: LOGICA PER "APPROVA TUTTI GLI IMPORTI" ---
    
    const approvaTuttiBtn = document.getElementById('approva-tutti-btn');
    if (approvaTuttiBtn) {
        approvaTuttiBtn.addEventListener('click', function(event) {
            // Impedisce al form di partire subito se il type fosse 'submit'
            event.preventDefault(); 
            
            if (confirm('Sei sicuro di voler approvare tutti gli importi richiesti?')) {
                const righeSpesa = document.querySelectorAll('.riga-spesa');
                
                righeSpesa.forEach(riga => {
                    const importoRichiestoText = riga.querySelector('.importo-richiesto').innerText;
                    const importoApprovatoInput = riga.querySelector('.importo-approvato');
                    
                    const valoreRichiesto = parseFloat(importoRichiestoText.replace('€', '').replace(/\./g, '').replace(',', '.').trim());
                    
                    if (!isNaN(valoreRichiesto)) {
                        importoApprovatoInput.value = valoreRichiesto.toFixed(2);
                    }
                });

                // Dopo l'aggiornamento visivo, salva i progressi inviando il form principale
                document.getElementById('form-istruttoria-principale').submit();
            }
        });
    }

    // --- BLOCCO 2: LOGICA PER "VERIFICA TUTTI I DOCUMENTI" ---

    const verificaTuttiButtons = document.querySelectorAll('.verifica-tutti-btn');
    verificaTuttiButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); 
            
            const modal = button.closest('.modal');
            const checkboxes = modal.querySelectorAll('.doc-verificato-check');
            
            checkboxes.forEach(checkbox => {
                checkbox.checked = true;
            });
            
            // Invia il form specifico di questa azione
            button.closest('form').submit();
        });
    });
});