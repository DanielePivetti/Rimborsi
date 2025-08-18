document.addEventListener('DOMContentLoaded', function() {
    const cameraModal = document.getElementById('cameraModal');
    const video = document.getElementById('camera-feed');
    const canvas = document.getElementById('camera-canvas');
    const captureBtn = document.getElementById('capture-btn');
    const fileInput = document.getElementById('allegato');
    let stream;

    // Quando la finestra modale si apre, avvia la fotocamera
    cameraModal.addEventListener('show.bs.modal', async function () {
        try {
            stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
            video.srcObject = stream;
        } catch (err) {
            console.error("Errore nell'accesso alla fotocamera: ", err);
            alert("Impossibile accedere alla fotocamera. Assicurati di aver dato i permessi.");
        }
    });

    // Quando la finestra modale si chiude, ferma la fotocamera
    cameraModal.addEventListener('hide.bs.modal', function () {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
        }
    });

    // Quando l'utente clicca su "Scatta e Allega"
    captureBtn.addEventListener('click', function() {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
        
        canvas.toBlob(function(blob) {
            const capturedFile = new File([blob], "cattura_documento.jpg", { type: "image/jpeg" });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(capturedFile);
            fileInput.files = dataTransfer.files;
            
            const modal = bootstrap.Modal.getInstance(cameraModal);
            modal.hide();
            alert('Foto allegata con successo! Premi "Aggiungi Documento" per salvarla.');
        }, 'image/jpeg');
    });
});