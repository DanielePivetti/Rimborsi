// JavaScript per l'applicazione di rimborsi con Bootstrap Italia

document.addEventListener('DOMContentLoaded', function() {
    // Inizializza tutti i componenti di Bootstrap Italia
    // window.bootstrap.init();  // Questa funzione non esiste in Bootstrap Italia
    
    // Gestione degli alerts
    const alertList = document.querySelectorAll('.alert');
    alertList.forEach(function (alert) {
        new bootstrap.Alert(alert);
        
        // Auto-chiusura degli alert dopo 5 secondi
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(function() {
                bootstrap.Alert.getInstance(alert).close();
            }, 5000);
        }
    });
    
    // Inizializza datepicker per i campi data (se presenti)
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Sostituisci l'input standard con il datepicker di Bootstrap Italia
        const datepickerContainer = document.createElement('div');
        datepickerContainer.className = 'it-datepicker-wrapper';
        input.parentNode.insertBefore(datepickerContainer, input);
        datepickerContainer.appendChild(input);
        
        // Aggiungi l'icona del calendario
        const calendarIcon = document.createElement('div');
        calendarIcon.className = 'it-date-datepicker';
        calendarIcon.innerHTML = '<svg class="icon icon-primary"><use href="https://cdn.jsdelivr.net/npm/bootstrap-italia@2.6.1/dist/svg/sprites.svg#it-calendar"></use></svg>';
        datepickerContainer.appendChild(calendarIcon);
    });
    
    // Gestione delle conferme di eliminazione
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Sei sicuro di voler eliminare questo elemento? Questa azione non può essere annullata.')) {
                e.preventDefault();
            }
        });
    });
    
    // Gestione dell'upload dei file con anteprima
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const fileName = e.target.files[0]?.name;
            if (fileName) {
                const filePreview = input.closest('.form-group').querySelector('.file-preview');
                if (filePreview) {
                    filePreview.textContent = 'File selezionato: ' + fileName;
                }
            }
        });
    });
});
