# TRAININGBOX

## UTILIZZO BASE
- caricare la chiocciola con i pellet nello sportello superiore
- collegare a un trasformatore 12V e attendere l'avvio (sii paziente!)
- doppio click su Run training sul desktop
- seleziona Esegui
- seleziona il task
- se vuoi cambiare il task, premi il bottone incassato sul pannello posteriore
- spegni il raspberry con chiudi sessione dalla GUI, evita di cavare corrente se non necessario

## SCARICARE I DATI
I dati sono salvati nella cartella trainingbox/saves e trainingbox/videos. In saves ci sono i csv con le timeslices (ID all'inizio del nome), in video ti lascio immaginare (ID alla fine).
Per accedere la cosa più facile è fare hotspot con il cellulare, connettere il raspberry (wifi manager in alto), recuperare l'indirizzo IP e connettersi con winscp
user: monkey
password: monkey
c'è anche attivo VNC che puoi conneterti con RealVNC Viewer (è un desktop remoto)

## SETUP BASE
attuale configurazione (apri training.py):

RESOLUTION = (600,300) #se esugui windowed se no è fullscreen
HB_POSITION = (200, 240) #in pixels
TARGET_POSITION = (600, 240) #in pixels
CIRCLE_DIAMETER = 150 #grandezza bottoni
FULLSCREEN = 1 #1 fullscreen 0 o per vedere console
MAXTRIAL = 100 #massimo numero trial
SPEED = 500 #velocità chiocciola pellet
VIDEODIR = '/home/monkey/Desktop/trainingbox/videos'
MAXVIDEOSPACE = 6000 #massimo spazio utilizzato dai video poi inizia a cancellare (in MB) usa df -h
(con l'attuale risoluzione fa circa 100mb ogni 2min, si cambia su testcamera.py)

## NUOVA CONDITION
sotto def update_state(self) crea un nuovo if self.task_id == x:, fai le schifezze con le timeslices copiando le altre
e aggiungi sotto per far comparire il bottone iniziale
n_tasks = ['pigio bevo', 'delayed reach']  # Imposta il numero di task disponibili, da aggiungere qui quando si programmano

