from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO

class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0

        # Salvo come attributi di istanza la lista delle escursioni filtrate per il parco scelto
        # e i vincoli dell'utente, cosi posso usarli comodamente nella ricorsione senza passarli ogni volta
        self._escursioni_parco = []
        self._max_giorni = None
        self._max_budget = None

        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # Chiedo al DAO la lista di tutte le coppie (id_escursione, id_punto_interesse) dalla tabella ponte
        relazioni = EscursioneDAO.get_escursioni_punti_interesse()
        if relazioni is None or self.escursioni_map is None or self.punti_interesse_map is None:
            return

        # Scorro ogni relazione e collego i due oggetti in entrambe le direzioni (ORM della relazione N:N)
        for rel in relazioni:
            escursione = self.escursioni_map.get(rel["id_escursione"])
            punto = self.punti_interesse_map.get(rel["id_punto_interesse"])

            # Se trovo entrambi gli oggetti nelle mappe, aggiorno i rispettivi set
            if escursione is not None and punto is not None:
                escursione.punti_interesse.add(punto)
                punto.escursioni.add(escursione)

    def genera_pacchetto(self, id_parco: str, max_giorni: int = None, max_budget: float = None):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        # Azzero sempre i risultati di eventuali ricerche precedenti prima di avviare la nuova ricorsione
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        if self.escursioni_map is None:
            return self._pacchetto_ottimo, self._costo, 0

        # Filtro solo le escursioni che appartengono al parco selezionato dall'utente
        self._escursioni_parco = [e for e in self.escursioni_map.values() if e.id_parco == id_parco]
        self._max_giorni = max_giorni
        self._max_budget = max_budget

        # Faccio partire la ricorsione dall'indice 0 con pacchetto vuoto, durata/costo/voto a 0 e set dei punti usati vuoto
        self._ricorsione(
            start_index=0,
            pacchetto_parziale=[],
            durata_corrente=0,
            costo_corrente=0.0,
            valore_corrente=0,
            punti_usati=set()
        )

        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    def _ricorsione(self, start_index: int, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
        """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""

        # A - Controllo subito se la combinazione attuale migliora il voto massimo trovato finora
        # Uso .copy() per salvare una copia della lista, altrimenti il backtracking la svuoterebbe
        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()
            self._costo = costo_corrente

        # B - Non mi serve una condizione terminale esplicita perche il ciclo for termina da solo
        # quando start_index raggiunge la lunghezza della lista delle escursioni del parco

        # Parto da start_index per generare combinazioni senza ripetizioni (evito di provare la stessa escursione piu volte o in ordini diversi)
        for i in range(start_index, len(self._escursioni_parco)):
            escursione = self._escursioni_parco[i]

            # C - Verifico i vincoli prima di aggiungere l'escursione al pacchetto parziale
            # 1) Se l'utente ha messo un limite di giorni, controllo di non superarlo
            if self._max_giorni is not None and (durata_corrente + escursione.durata_giorni) > self._max_giorni:
                continue

            # 2) Se l'utente ha messo un budget massimo, controllo di non sforarlo
            if self._max_budget is not None and (costo_corrente + escursione.costo) > self._max_budget:
                continue

            # 3) Controllo che l'escursione non contenga punti di interesse gia presenti nel pacchetto usando intersection()
            if len(punti_usati.intersection(escursione.punti_interesse)) > 0:
                continue

            # D - Aggiungo l'escursione e aggiorno il set dei punti usati e il voto parziale
            pacchetto_parziale.append(escursione)
            punti_usati.update(escursione.punti_interesse)
            valore_escursione = sum(p.voto_visitatori for p in escursione.punti_interesse)

            # E - Passo al livello successivo partendo da i + 1 per non riutilizzare la stessa escursione
            self._ricorsione(
                start_index=i + 1,
                pacchetto_parziale=pacchetto_parziale,
                durata_corrente=durata_corrente + escursione.durata_giorni,
                costo_corrente=costo_corrente + escursione.costo,
                valore_corrente=valore_corrente + valore_escursione,
                punti_usati=punti_usati
            )

            # F - Backtracking: rimuovo l'escursione e i suoi punti di interesse per provare le altre combinazioni
            # Durata, costo e valore non hanno bisogno di backtracking perche li ho passati come somme nuove nella chiamata ricorsiva
            pacchetto_parziale.pop()
            punti_usati.difference_update(escursione.punti_interesse)