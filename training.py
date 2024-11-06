import tkinter as tk
import time
import csv
import threading
try:
    import RPi.GPIO as GPIO
    RASPImode = 1
except ImportError:
    RASPImode = 0

# Configurazioni iniziali
RESOLUTION = (800, 600)
HB_POSITION = (200, 300)
TARGET_POSITION = (600, 300)
CIRCLE_DIAMETER = 100



# Classe StateMachine per gestire i task
class TaskStateMachine:
    def __init__(self, task_id, canvas, saver_thread, reward_thread):
        self.task_id = task_id
        self.state = 0
        self.trial = 1
        self.canvas = canvas
        self.saver_thread = saver_thread
        self.reward_thread = reward_thread
        self.HB_button = self.create_circle(HB_POSITION, "black", tag="HB_button")
        self.TARGET_button = self.create_circle(TARGET_POSITION, "black", tag="TARGET_button")
        self.stateHB = 0  # Stato di pressione per HB: 1 se premuto, 0 se rilasciato
        self.stateTB = 0  # Stato di pressione per TARGET: 1 se premuto, 0 se rilasciato
        self.last_time = time.time()
        
        # Associa gli eventi di pressione e rilascio a entrambi i cerchi
        self.canvas.tag_bind("HB_button", "<ButtonPress-1>", self.on_click_press)
        self.canvas.tag_bind("HB_button", "<ButtonRelease-1>", self.on_click_release)
        self.canvas.tag_bind("TARGET_button", "<ButtonPress-1>", self.on_click_press)
        self.canvas.tag_bind("TARGET_button", "<ButtonRelease-1>", self.on_click_release)


        self.update_state()

    def create_circle(self, position, color, tag):
        x, y = position
        radius = CIRCLE_DIAMETER / 2
        return self.canvas.create_oval(
            x - radius, y - radius, x + radius, y + radius,
            fill=color, outline="", tags=tag)

    def update_state(self): ###### DEFINIZIONE TASK #########
        if self.task_id == 1:

            if self.state == 0: #reset e check se pressato
                self.canvas.itemconfig(self.HB_button, fill="black")
                self.canvas.itemconfig(self.TARGET_button, fill="black")
                if (self.stateHB == 0 & self.stateTB == 0):  
                    self.save_state_data()
                    self.state = 1
                else:
                    self.state = 99
                
            elif self.state == 1: #aspetta 2 sec e visualizza HB
                if (self.stateHB == 0 & self.stateTB == 0):
                    
                    if time.time() > self.last_time + 2:
                        self.canvas.itemconfig(self.HB_button, fill="white")
                        self.save_state_data()
                        self.state = 2    
                else:   
                    self.state = 99         
                

            elif self.state == 2: #dai 10sec per premere
                if time.time() < self.last_time + 10:
                    if self.stateHB == 1:
                        self.save_state_data()
                        self.state = 3        
                else:
                    self.state = 99 

            elif self.state == 3: #reward
                self.reward_thread.deliver()
                self.save_state_data()
                self.state = 0
                self.trial += 1

            elif self.state == 99:
                self.save_state_data('error')
                self.canvas.itemconfig(self.HB_button, fill="black")
                self.canvas.itemconfig(self.TARGET_button, fill="black")
                if (self.stateHB == 0 & self.stateTB == 0):
                    self.state = 0 
        
        if self.task_id == 2:

            if self.state == 0: #reset e check se pressato
                self.canvas.itemconfig(self.HB_button, fill="black")
                self.canvas.itemconfig(self.TARGET_button, fill="black")
                if (self.stateHB == 0 & self.stateTB == 0):  
                    self.save_state_data()
                    self.state = 1
                else:
                    self.state = 99
                
            elif self.state == 1: #aspetta 2 sec e visualizza HB
                if (self.stateHB == 0 & self.stateTB == 0):
                    
                    if time.time() > self.last_time + 2:
                        self.canvas.itemconfig(self.HB_button, fill="white")
                        self.save_state_data()
                        self.state = 2    
                else:   
                    self.state = 99  

            elif self.state == 2: #aspetta il click HB entro 5 sec se click alla fine accende green
                if time.time() < self.last_time +5:
                    if self.stateHB == 1:
                        self.save_state_data()
                        self.canvas.itemconfig(self.TARGET_button, fill="green")
                        self.state = 3          
                else:
                    self.state = 99

            elif self.state == 3: #controlla il mantenimento della pressione, accende rosso dopo 2sec
    
                if (self.stateHB == 1):
                    if (time.time() > self.last_time + 2): 
                        self.save_state_data()
                        self.canvas.itemconfig(self.TARGET_button, fill="red")
                        self.state = 4
                else:
                    self.state = 99   

            elif self.state == 4: #controlla rilascio di HB 
                if (time.time() < self.last_time + 2):
                    if (self.stateHB == 0):
                        self.save_state_data()
                        self.state = 5    
                else:
                    self.state = 99 

            elif self.state == 5: #controlla tocco di rosso 
                if time.time() < self.last_time + 5:
                    if self.stateTB == 1:
                        self.save_state_data()
                        self.state = 6  
                else:
                    self.state = 99 

            elif self.state == 6: #da reward
                self.reward_thread.deliver()
                self.save_state_data()
                self.state = 0
                self.trial += 1

            elif self.state == 99:
                self.save_state_data('error')
                self.canvas.itemconfig(self.HB_button, fill="black")
                self.canvas.itemconfig(self.TARGET_button, fill="black")
                if (self.stateHB == 0 & self.stateTB == 0):
                    self.state = 0 


        self.canvas.after(1, self.update_state)


    def on_click_press(self, event):
        # Verifica quale cerchio è stato premuto e aggiorna lo stato corrispondente
        clicked_item = self.canvas.gettags("current")[0]
        if clicked_item == "HB_button":
            self.stateHB = 1
            print("HB button pressed") 
        elif clicked_item == "TARGET_button":
            self.stateTB = 1
            print("TARGET button pressed") 

    def on_click_release(self, event):
        # Verifica quale cerchio è stato rilasciato e aggiorna lo stato corrispondente
        clicked_item = self.canvas.gettags("current")[0]
        if clicked_item == "HB_button":
            self.stateHB = 0
            print("HB button released") 
        elif clicked_item == "TARGET_button":
            self.stateTB = 0
            print("TARGET button released")

    def save_state_data(self, status = 'ok'):
        self.last_time = time.time()
        row = [self.task_id, self.trial, self.state, self.last_time, status]
        self.saver_thread.save_data(row)


# Classe per salvare i dati in un thread separato
class DataSaverThread(threading.Thread):
    def __init__(self, file_name="experiment_data.csv"):
        super().__init__()
        self.file_name = file_name
        self.data_queue = []
        self.running = True 
        self.lock = threading.Lock()
        self.start()

    def run(self):
        with open(self.file_name, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            while self.running:
                if self.data_queue:
                    with self.lock:
                        data = self.data_queue.pop(0)
                    writer.writerow(data)
                    csvfile.flush()
                time.sleep(0.1)
    
    def stop(self):
        self.running = False

    def save_data(self, data):
        with self.lock:
            self.data_queue.append(data)


class RewardGPIO(threading.Thread):
    def __init__(self, gpio=18, mode=0):
        super().__init__()
        self.GPIO_PIN = gpio
        self.mode = mode
        if self.mode:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.GPIO_PIN, GPIO.OUT)

    def deliver(self, time=1):
        if self.mode:
            GPIO.output(self.GPIO_PIN, GPIO.HIGH)
            time.sleep(time)
            GPIO.output(self.GPIO_PIN, GPIO.LOW)
        print('reward delivered')

# Configura l'interfaccia grafica
def main():
    # Numero di task disponibili
    n_tasks = ['pigio bevo','delayed reach']  # Imposta il numero di task disponibili
    task_id = [None]  # Lista per passare task_id tramite la funzione di callback

    # Funzione per mostrare la finestra di selezione del task
    def show_task_selection():
        task_window = tk.Tk()
        task_window.geometry(f"{RESOLUTION[0]}x{RESOLUTION[1]}")
        task_window.configure(bg="black")

        # Funzione per selezionare il task e chiudere la finestra di selezione
        def select_task(id):
            task_id[0] = id + 1
            task_window.destroy()
            show_main_window()  # Mostra la finestra principale dopo la selezione del task

        # Crea un pulsante per ogni task
        for i in range(len(n_tasks)):
            button = tk.Button(
                task_window,
                text=f"Task {n_tasks[i]}",
                font=("Arial", 20),
                width=20,
                height=2,
                command=lambda i=i: select_task(i)
            )
            button.pack(pady=10)

        task_window.mainloop()

    # Funzione per mostrare la finestra principale dopo la selezione del task
    def show_main_window():
        root = tk.Tk()
        root.geometry(f"{RESOLUTION[0]}x{RESOLUTION[1]}")
        root.configure(bg="black")

        canvas = tk.Canvas(root, width=RESOLUTION[0], height=RESOLUTION[1], bg="black")
        canvas.pack()

        # Thread per salvare i dati
        saver_thread = DataSaverThread()
        reward_thread = RewardGPIO(gpio=18, mode=RASPImode)

        # Avvia la macchina a stati con il task selezionato
        TaskStateMachine(task_id[0], canvas, saver_thread, reward_thread)

        root.mainloop()
        if RASPImode:
            GPIO.cleanup()
        saver_thread.stop()

    # Mostra la finestra di selezione dei task all'inizio
    show_task_selection()

if __name__ == "__main__":
    main()