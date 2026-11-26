# Lab 09 - Soluzione

#### Argomenti

- Utilizzo Pattern MVC e DAO
- Utilizzo dell'Object Relational Mapping (ORM)
- Algoritmi di Ricorsione

---
> **❗ ATTENZIONE:**
>  Ricordare di effettuare il **fork** del repository principale, quindi clonare su PyCharm il **repository personale**
> (https://github.com/my-github-username/Lab09) e non quello principale.
>
> In caso di dubbi consultare la guida caricata nel lab02:
> https://github.com/Programmazione-Avanzata-2026-27/Lab02/blob/main/Guida.pdf
>
> Per il setup del database (XAMPP, DBeaver e creazione del database tramite il file `parchi_naturali.sql`) fare riferimento alla spiegazione del Lab06.

---

##  Analisi Ottimale dei Pacchetti Escursionistici di un Parco Naturale
Un'agenzia di **escursioni nei parchi naturali** vuole usare i dati delle escursioni già proposte ai clienti per
suggerire pacchetti di viaggio ottimali ai nuovi visitatori. Per ogni escursione sono noti il parco in cui si svolge,
la durata in giorni, il costo e i punti di interesse naturalistici che include (cascate, laghi, belvedere, ecc.),
ciascuno con il voto medio assegnato dai visitatori (da 1 a 10).

Realizzare un programma che consenta all'utente di scegliere un parco, di indicare il numero massimo di giorni
a disposizione (`G`) e un budget massimo (`B`). A partire dalle escursioni disponibili nel parco selezionato, il
programma dovrà generare un pacchetto che consista in una combinazione di escursioni che massimizzi il gradimento
complessivo dei visitatori (la somma dei voti dei punti di interesse presenti nelle escursioni selezionate) e che
rispetti i seguenti vincoli:
- Le escursioni incluse nel pacchetto devono essere **tutte diverse tra loro**.
- Non devono esserci **punti di interesse duplicati** all'interno del pacchetto (non si visita due volte lo stesso
punto di interesse).
- La durata complessiva del pacchetto non deve superare il **numero massimo di giorni** indicato (`G`).
- Il costo totale del pacchetto non deve eccedere il **budget massimo** previsto (`B`).

Il programma utilizza il database fornito, denominato `parchi_naturali.sql`, che contiene quattro tabelle principali:
- `parco`: contiene le informazioni degli 8 parchi:
  - id
  - nome

- `punto_interesse`: contiene le informazioni inerenti ai punti di interesse:
  - id
  - nome
  - voto_visitatori (il voto medio assegnato dai visitatori, da 1 a 10)

- `escursione`: contiene le informazioni inerenti a ciascuna escursione:
  - id
  - id_parco
  - nome
  - durata_giorni
  - costo

- `escursione_punto_interesse`: la tabella che gestisce la relazione **molti-a-molti (N:N)** tra escursioni e punti
di interesse. Permette di trovare tutti i punti di interesse inclusi in un'escursione e tutte le escursioni a cui
ciascun punto di interesse appartiene:
  - id_escursione
  - id_punto_interesse

![relazione_db.png](img/relazione_db.png)

L'applicazione, sviluppata in Python, deve permettere di
- Gestire **la relazione N:N** tra punti di interesse ed escursioni tramite l'**ORM** e opportune strutture dati in Python.
- Calcolare la sequenza di escursioni che massimizzi il voto complessivo dei punti di interesse presenti nelle
escursioni selezionate (e che rispetti i vari vincoli indicati) attraverso un **algoritmo di ottimizzazione ricorsiva**.


##  Funzionalità Richieste
Nel progetto di base, l'interfaccia grafica (file `view.py` e `controller.py`) è già implementata con il seguente layout:
![layout.png](img/layout.png)

### **Problema di Ottimizzazione (algoritmo ricorsivo + ORM)**
A partire dal layout proposto, l'applicazione deve permettere all'utente di:
- Selezionare un parco (un codice alfanumerico univoco, l'id del parco), tramite un Dropdown;
- Inserire il numero massimo di giorni a disposizione tramite un TextField;
- Inserire un budget massimo tramite un TextField;
- Premendo un pulsante (“Genera Pacchetto”) visualizzare tramite una ListView la lista di escursioni che massimizzano
il voto complessivo.

>💡 **Esempio**: L'utente seleziona il parco “Monte Azzurro”, indica una durata di 4 giorni e un budget pari a €400 → il
> programma mostra la lista di escursioni che massimizzano il voto complessivo, rispettando i vincoli indicati.
![esempio.png](img/esempio.png)

È inoltre importante considerare alcune condizioni particolari per il corretto funzionamento dell'applicazione:
- Se l'utente non specifica un budget massimo, il sistema interpreta la richiesta come la volontà di generare un
pacchetto senza alcun limite di costo.
- Se l'utente non indica un numero massimo di giorni, il sistema considera la ricerca libera da vincoli di durata.

##  Nota Bene
Per pensare come impostare la **ricorsione**, è consigliato utilizzare lo schema seguente.
Può esser utile ragionare su carta per capire come impostare l'algoritmo.

```code
def recursion(..., level):
    # 🟤 A - Istruzioni che dovrebbero essere sempre eseguite
    do_always(...)
   
    # 🟢 B - Potrebbe non essere necessaria per questo problema
    if terminal_condition:
        do_something(...)
   
    for ...: # un loop, se necessario    
   
        # 🟡 C - Considerare dei vincoli prima di procedere con la ricorsione
        if filter:
       
            # 🔵 D
            compute_partial()
           
            # 🔴 E
            recursion(..., level + 1)
       
            # 🟣 F
            back_tracking()
```

**💡 Suggerimenti Pratici**
- Quando è necessario copiare liste di oggetti per evitare di modificare l'originale durante la ricorsione,
è meglio usare il metodo `.copy()` che crea una copia superficiale della lista: la nuova lista contiene gli stessi
oggetti della lista originale, ma modificando la lista copiata non si altera la lista originale.
    ```code
    lista_copia = lista_originale.copy()
    ```
- Per le strutture dati `set()`, ricordare che sono disponibili molti metodi utili, tra cui: `.add()`, `.update()`,
`.intersection()`, `.difference()`, `.difference_update()`, ecc. (vedi
[Python Sets](https://www.w3schools.com/python/python_ref_set.asp)). Questi permettono di gestire in modo efficace
insiemi di elementi senza duplicati. Inoltre, è importante ricordare che tutti gli elementi di un `set()`
devono essere **hashable**, cioè immutabili e confrontabili.

## Materiale Fornito
Il repository del lab09 è organizzato con la struttura ad albero mostrata di seguito e contiene tutto il necessario per
svolgere il laboratorio:

```code
Lab09/
├── database/
│   ├── __init__.py
|   ├── connector.cnf
|   ├── DB_connect.py
│   ├── parco_DAO.py
│   ├── punto_interesse_DAO.py
│   └── escursione_DAO.py
│
├── model/
│   ├── __init__.py
│   ├── model.py (DA MODIFICARE) 
│   ├── parco.py
│   ├── punto_interesse.py
│   └── escursione.py
│
├── UI/
│   ├── __init__.py
│   ├── alert.py
│   ├── controller.py
│   ├── view.py
│   └── mappa_parchi.png
│
├── parchi_naturali.sql (DA IMPORTARE)
├── requirements.txt
└── main.py (DA ESEGUIRE)
 ```
