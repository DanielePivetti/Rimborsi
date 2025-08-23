Leggimi 

23/08/2025

Descrizione del progetto
Questa applicazione web simula la gestione e la trasmissione delle richieste di rimborso spese sostenute in eventi di emergenza da parte di organizzazioni di volontariato.

Ruoli previsti:
Compilatore: 
registra le spese, l’impiego di mezzi e attrezzature, e allega i documenti giustificativi e trasmettte la richiesta.
Istruttore: crea gli eventi di emergenza, prende in carico le richieste conferma o modifica l'importo richiesto, compilando l'importo approvato e controlla i documenti.
Amministratore: crea gli oggetti necessari al flusso, ossia le organizzazioni di volontariato, i mezzi e le attrezzature associati alle organizzazioni di volontariato e associa gli utenti che si registrano come compilatori alle organizzazioni 
(attualmente è implementata la  registrazione di utenti generici)

Flusso operativo Compilatore

1)  Login
2) Creazione della richiesta, selezionando l'evento di emergenza. 
 Ogni richiesta deve essere associata a un evento di emergenza creato dall’istruttore.
3) Registrazione, spese e impiego mezzi
4) Registrazione  documenti giustificativi e allegati
5) Controllo finale e trasmissione per la fase istruttoria.
6) Passaggio di stato della richiesta da A a B

Con la trasmissione, la richiesta passa dallo stato A (in bozza) allo stato B (in istruttoria).

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

- Le modifiche e cancellzaione degli oggetti sono possobili se la richiesta è in stato A: In bozza. NOn è possibile la cancellazioni in cascata, ossia non si può eliminare un oggetto se sono presenti oggetti associati all'oggetto principale.


Flusso operativo Istruttore

1) Login

a) Istruttoria

2) Visualizzazione  richiesta da istruire 
 Ogni richiesta risulterà  associata ad un evento di emergenza creato dall’istruttore.
3) Visualizzazione dal tab in istruttoria delle spese, degli importi richiesti  
4) Conferma o modifica dell'importo richiesto con la registrazione  dell'importo approvato. Per ogni spesa è possibile inserire una nota 
4) Visualizzazione dei documenti giustificativi e allegati e conferma tramite il campo verifica. Per ogni documento è possibile inserire una nota
5) Controllo finale e conclusione dell'istruttoria
6) Passaggio di stato della richiesta da B a C 

Per i punti 4 e 5 è possibile effettuare un'approvazione massiva, ossia la conferma  dell'importo richiesto per tutte le spese e la verifica per tutti i documenti. La conclusione dell'istruttoria prevede la registrazione dell'esito approvato, approvato parzialmente e respinto.
(attualmente se la somma dell'importo in corrispondenza del richiesto è superiore a quello dell'approvato l'esito possibile è approvato parzialmente e respinto ed è obbligatoria la compilazione del campo note).

b) Evento

2) Creazione di un evento di emergenza da rendere disponibile
3) Modifica di un evento esistente


Flusso operativo Amministratore

1) Login
2A) Creazione e modifica organizzazioni
2B) Aggiunta e modifica Mezzi  
(NO cancellazione)

Istruzioni per l'installazione

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

flask run

L’applicazione sarà disponibile su http://127.0.0.1:5000