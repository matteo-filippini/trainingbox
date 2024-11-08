import os
import time
import glob
import gst
from datetime import datetime

class VideoRecorder:
    def __init__(self, save_folder, max_space_gb, max_file_size_mb=100):
        self.save_folder = save_folder
        self.max_space_gb = max_space_gb
        self.max_file_size_mb = max_file_size_mb
        self.current_file = None
        self.current_file_size = 0
        self.current_file_index = 0
        self.video_pipeline = None
        self._ensure_folder_exists()

    def _ensure_folder_exists(self):
        """Assicura che la cartella di salvataggio esista."""
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

    def _get_available_space(self):
        """Restituisce lo spazio disponibile sulla cartella in GB."""
        total, used, free = os.statvfs(self.save_folder)
        return free * total / (1024 ** 3)

    def _get_video_filename(self):
        """Genera un nome di file unico per ogni sessione video."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.save_folder, f"video_{timestamp}_{self.current_file_index}.mp4")

    def _check_and_manage_space(self):
        """Gestisce lo spazio, eliminando i file più vecchi se lo spazio è insufficiente."""
        while self._get_available_space() < self.max_space_gb:
            files = sorted(glob.glob(os.path.join(self.save_folder, "*.mp4")), key=os.path.getmtime)
            if files:
                os.remove(files[0])
                print(f"File eliminato per fare spazio: {files[0]}")
            else:
                print("Non ci sono file da eliminare.")
                break

    def _initialize_pipeline(self):
        """Inizializza la pipeline GStreamer per registrare il video."""
        self.current_file = self._get_video_filename()
        self.video_pipeline = gst.parse_launch(f"v4l2src ! videoconvert ! x264enc tune=zerolatency speed-preset=fast ! mp4mux ! filesink location={self.current_file}")
        self.video_pipeline.set_state(gst.State.PLAYING)
        self.current_file_size = 0

    def start_recording(self):
        """Inizia la registrazione e gestisce i file di salvataggio."""
        self._initialize_pipeline()
        print(f"Inizio registrazione in {self.current_file}")

        while True:
            # Controlla la dimensione del file e se è necessario passare a un nuovo file
            self.current_file_size = os.path.getsize(self.current_file) / (1024 * 1024)  # In MB
            if self.current_file_size >= self.max_file_size_mb:
                print(f"File {self.current_file} ha raggiunto la dimensione massima di {self.max_file_size_mb}MB.")
                self.current_file_index += 1
                self._check_and_manage_space()  # Verifica lo spazio disponibile e elimina file se necessario
                self._initialize_pipeline()  # Passa a un nuovo file di registrazione

            time.sleep(1)

    def stop_recording(self):
        """Ferma la registrazione."""
        if self.video_pipeline:
            self.video_pipeline.set_state(gst.State.NULL)
            print(f"Registrazione fermata. File salvato in {self.current_file}")
        else:
            print("Nessuna registrazione in corso.")


if __name__ == "__main__":
    save_folder = "/videos"  # Sostituisci con il percorso della tua cartella di salvataggio
    max_space_gb = 5  # 5 GB di spazio massimo
    recorder = VideoRecorder(save_folder, max_space_gb)
    
    # Avvia la registrazione
    recorder.start_recording()

    # Per fermare la registrazione (per esempio, dopo 10 minuti)
    time.sleep(600)  # Simula un tempo di registrazione di 10 minuti
    recorder.stop_recording()