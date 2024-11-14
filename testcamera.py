import os
import time
import threading
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from datetime import datetime


class VideoStreamRecorder(threading.Thread):
    def __init__(self, max_space=1000, max_file_size=100, directory="videos", file_index=0):
        """
        Inizializza la classe per la registrazione video.
        :param max_space: spazio massimo in MB da utilizzare (default 1000MB)
        :param max_file_size: dimensione massima di ciascun file video in MB (default 100MB)
        :param directory: cartella di destinazione per i file video
        """
        super().__init__()
        self.max_space = max_space * 1024 * 1024  # Convertiamo in byte
        self.max_file_size = max_file_size * 1024 * 1024  # Convertiamo in byte
        self.directory = directory
        self.running = False
        self.picam2 = Picamera2()
        self.video_config = self.picam2.create_video_configuration()
        self.picam2.configure(self.video_config)
        self.encoder = H264Encoder(10000000)
        self.file_index = file_index
        
        if not os.path.exists(directory):
            os.makedirs(directory)

        self.start()


    def _cleanup_old_files(self):
        """Cancella i file video più vecchi se lo spazio supera il limite massimo."""
        files = files = sorted([f for f in os.listdir(self.directory) if f.endswith('.h264')], key=lambda f: os.path.getctime(os.path.join(self.directory, f)))
        total_size = sum(os.path.getsize(os.path.join(self.directory, f)) for f in files if os.path.exists(os.path.join(self.directory, f)))

        while total_size > self.max_space and files:
            oldest_file = files.pop(0)
            video_path = os.path.join(self.directory, oldest_file)
            txt_path = f"{video_path}.txt"

            os.remove(video_path)
            os.remove(txt_path)
            print('eliminato ' + str(video_path))

            total_size = sum(os.path.getsize(os.path.join(self.directory, f)) for f in files if os.path.exists(os.path.join(self.directory, f)))



    def run(self):
        """Avvia la registrazione video continua."""
        self.running = True
        
        while self.running:
            # Genera il nome del file basato sulla data e ora
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            video_file = os.path.join(self.directory, f"{timestamp}_{self.file_index}.h264")
            txt_file = f"{video_file}.txt"
            
            # Avvia la registrazione
            self.picam2.start_recording(self.encoder, video_file, pts=txt_file)
            
            # Controlla la dimensione del file e ferma la registrazione se supera il limite
            while os.path.getsize(video_file) < self.max_file_size and self.running:
                time.sleep(1)
            
            # Ferma la registrazione e prepara per il prossimo file
            self.picam2.stop_recording()
            self._cleanup_old_files()


    def stop(self):
        """Ferma la registrazione e termina il thread."""
        self.running = False


# Esempio di utilizzo
if __name__ == "__main__":
    recorder = VideoStreamRecorder(max_space=300, max_file_size=100)  # 500MB di spazio e 10MB per file
    
    
    # Registra per 30 secondi
    time.sleep(30000)
    
    # Ferma la registrazione
    recorder.stop()
    recorder.join()
