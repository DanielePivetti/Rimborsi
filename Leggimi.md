Applicazione Prototipo Rimborsi articoli 40

Ultimo commit 23/08/2025

A) Descrizione del progetto
Questa applicazione web simula la gestione e la trasmissione delle richieste di rimborso spese sostenute in eventi di emergenza da parte di organizzazioni di volontariato.

B) Ruoli previsti: L'applicazione prevede tre ruoli

Ruolo Compilatore: 
L'utente con tale ruolo registra le spese, l’impiego di mezzi e attrezzature, allega i documenti giustificativi per le spese registrate e trasmettte la richiesta. L'utente compilatore può effettuare la compilazione per una o più organizzazioni. L'associazione tra utente compilatore e organizzazioni è gestita dall'utente amministratore.

Istruttore
L'utente con tale ruolo crea gli eventi di emergenza ed effettua l'istruttoria delle richieste. In particolare  prende in carico le richieste inviate, esamina ciascuna voce di spesa confermando o modificando l'importo richiesto, compilando l'importo approvato ed effettua il controllo sui documenti giustificativi allegati a ciascuna spesa.

Ammministratore

L'utente con tale ruolo crea gli oggetti necessari al flusso, ossia le organizzazioni di volontariato, i mezzi e le attrezzature associati alle organizzazioni di volontariato e associa gli utenti che si registrano come compilatori alle organizzazioni 
(attualmente è implementata la  registrazione di utenti generici)

Flusso operativo Compilatore

1) Login
2) creazione della richiesta, partendo dalla selezione dell'evento di emergenza. 
 Ogni richiesta deve essere associata a un evento di emergenza creato dall’istruttore. L'utente non può creare eventi. Con il salvataggio la richiesta assume un codice univoco interno (codice interno organizzazine + timestamp)
3) Registrazione dei dati relativi alle spese e all'impiego del impiego mezzi/attrezzature. Per la registrazione dell'impiego il compilatore deve selezionare un mezzo o un'attrezzatura di un'organizzazione. 
4) Registrazione dei dati di riferimento relativi ai documenti giustificativi e caricamento degli allegati. Gli allegati possono essere in formato PDF, JPEG, JPG e PNG
5) Controllo finale e trasmissione per la fase istruttoria.
6) Il sistema determina in automatico il passaggio della richiesta dallo stato A (in bozza) allo stato B (In istruittoria) e il salvataggio di un numero di protocollo di invio

Gestione dei tipi di spesa e tipi di documento:

Tipologie di spesa:
01: Carburante
02: Pedaggi autostradali
03: Pasti
04: Ripristino danni mezzi
05: Viaggio
06: Altro

Tipi di documento:
A: Scontrino
B: Fattura
C: Autorizzazione
D: Attestazione Danno

Vincoli applicativi:
- Tutti i tipi di spesa richiedono almeno un documento di tipo A (Scontrino) o B (Fattura).
- Il tipo di spesa 05 (Viaggio) richiede obbligatoriamente anche un documento di tipo C (Autorizzazione).
- Il tipo di spesa 04 (Ripristino danni mezzi) richiede obbligatoriamente anche un documento di tipo D (Attestazione Danno).
- Le spese di tipo 01 (Carburante), 02 (Pedaggi autostradali), 04 (Ripristino danni mezzi) devono essere associate a un impiego di mezzo/attrezzatura

- Le modifiche e cancellazazione degli oggetti sono possobili se la richiesta è nello stato A (In bozza). Non è possibile la cancellazioni in cascata, ossia non l'eliminazione di un oggetto se sono presenti oggetti associati all'oggetto principale.

Flusso operativo Istruttore

1) Login

a) Istruttoria
2) Visualizzazione  richiesta da istruire.  Ogni richiesta risulterà  associata ad un evento di emergenza creato dall’istruttore.
3) Visualizzazione del tab delle richieste in istruttoria, con il dettaglio riportante le spese, l'impiego dei mezzi e i documenti giustificativi allegati  
4) Per ogni spesa conferma o modifica del valore riportato nell'importo richiesto: l'istruttore deve registrare nel campo importo approvato lo stesso valore o un importo inferiore. Per ogni spesa è possibile inserire una nota 
4) Visualizzazione dei documenti giustificativi allegati a ciascuna spesa e la conferma de documento attraverso la compilazione del campo verifica. Per ogni documento è possibile inserire una nota
5) Controllo finale e conclusione dell'istruttoria
6) Il sistema determina in automatico il passaggio della richiesta dallo stato B (In istruttoria ) allo stato C (Istruita) e il salvataggio di un numero di protocollo istruttoria

Per i punti 4 e 5 è possibile effettuare un'approvazione massiva, ossia la conferma  dell'importo richiesto per tutte le spese e la verifica per tutti i documenti. La conclusione dell'istruttoria prevede la registrazione dell'esito approvato, approvato parzialmente e respinto.
(attualmente se la somma dell'importo in corrispondenza del richiesto è superiore a quello dell'approvato l'esito possibile è approvato parzialmente e respinto ed è obbligatoria la compilazione del campo note).

b) Evento

2) Creazione di un evento di emergenza da rendere disponibile per la compilazione delle richieste
3) Modifica di un evento esistente


Flusso operativo Amministratore

1) Login
2A) Creazione e modifica organizzazioni
2B) Aggiunta e modifica Mezzi  
(NO cancellazione)

C= Istruzioni per l'installazione

Istruzioni per l’installazione
1. Prerequisiti
Python 3.9 o superiore installato sul sistema
(puoi scaricarlo da python.org)

2. Clona il repository
Se non l’hai già fatto, scarica il progetto sul tuo computer:

git clone <URL_DEL_REPOSITORY>
cd rimborsi

3. Crea un ambiente virtuale
Consigliato per isolare le dipendenze del progetto:

python -m venv venv

4. Attiva l’ambiente virtuale

4.1) Windows 
python -m venv venv

4.2) Mac/Linux 

source venv/bin/activate

5. Installa le dipendenze

pip install -r requirements.txt

6) Configura il database

flask db upgrade

8. Avvia l’applicazione

lanciare i comandi dall'ambiente virtuale creato
flask run  oppure
python run.py

L’applicazione sarà disponibile su http://127.0.0.1:5000

9. Primo popolamento del database

Lanciando lo script 
python seed.py

si creano due organizzazioni, i relativi mezzi, l'utente compilatore, l'utente istruttore e l'utente amministratore:
compilatore@test.com, istruttore@test.com, admin@test.com
   

