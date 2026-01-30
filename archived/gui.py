import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from audio_processing import run_karaoke_process

class KaraokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Karaoke Creator")
        self.root.geometry("400x250")

        # --- UI Elements ---
        tk.Label(root, text="AI Karaoke Processor", font=("Arial", 14, "bold")).pack(pady=10)
        
        self.btn = tk.Button(root, text="Select Video & Start", command=self.start_thread,
                            bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=20, pady=5)
        self.btn.pack(pady=10)

        # Progress Bar (Indeterminate means it slides back and forth)
        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
        self.progress.pack(pady=20)

        self.status = tk.Label(root, text="Ready", fg="gray")
        self.status.pack()

    def start_thread(self):
        """Starts the file dialog and launches the processing thread."""
        file_path = filedialog.askopenfilename(filetypes=[("Video", "*.mp4")])
        if not file_path:
            return

        # Disable button so user doesn't click twice
        self.btn.config(state="disabled")
        self.status.config(text="AI is working... this may take a minute.", fg="blue")
        
        # Start the loading bar animation
        self.progress.start(10) 

        # Create and start a background thread
        processing_thread = threading.Thread(target=self.run_logic, args=(file_path,))
        processing_thread.start()

    def run_logic(self, file_path):
        """This function runs in the background thread."""
        success, message = run_karaoke_process(file_path)

        # Use root.after to safely update the GUI from a thread
        self.root.after(0, self.finish_up, success, message)

    def finish_up(self, success, message):
        """Resets the UI once the thread finishes."""
        self.progress.stop()
        self.btn.config(state="normal")
        
        if success:
            self.status.config(text="Success!", fg="green")
            messagebox.showinfo("Finished", "Audio separation complete!")
        else:
            self.status.config(text="Error occurred", fg="red")
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = KaraokeApp(root)
    root.mainloop()