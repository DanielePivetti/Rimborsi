@echo off
echo Configurazione dell'ambiente Python e creazione dell'utente compilatore

:: Attiva l'ambiente virtuale se necessario (decommentare la riga successiva se necessario)
:: call venv\Scripts\activate

:: Installa i pacchetti necessari
pip install flask flask-sqlalchemy flask-migrate flask-login

:: Esegui lo script per creare l'utente
python crea_utente_compilatore.py

echo.
echo Operazione completata. Premi un tasto per continuare...
pause > nul
