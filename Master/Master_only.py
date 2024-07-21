import os
import shutil
import threading
import time
import tkinter as tk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BackupEventHandler(FileSystemEventHandler):
    def __init__(self, src_dir: str, dest_dir: str):
        self.src_dir = src_dir
        self.dest_dir = dest_dir

    def on_modified(self, event):
        if event.is_directory:
            return
        
        src_path = event.src_path
        if not os.path.exists(src_path):
            return

        dest_path = src_path.replace(self.src_dir, self.dest_dir, 1)
        if not os.path.exists(os.path.dirname(dest_path)):
            os.makedirs(os.path.dirname(dest_path))

        shutil.copy2(src_path, dest_path)
        print(f"{src_path} backed up to {dest_path}")

class BackupSystemGUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Backup System")
        self.window.geometry("400x300")

        self.src_dirs = []
        self.dest_dirs = []

        self.src_label = tk.Label(self.window, text="Source Directories")
        self.src_label.pack(pady=(10, 0))

        self.src_listbox = tk.Listbox(self.window, selectmode=tk.MULTIPLE)
        self.src_listbox.pack(padx=10, pady=(5, 10), fill=tk.BOTH, expand=True)

        self.src_add_button = tk.Button(self.window, text="Add", command=self.add_src_dir)
        self.src_add_button.pack(side=tk.LEFT, padx=(10, 5))

        self.src_remove_button = tk.Button(self.window, text="Remove", command=self.remove_src_dir)
        self.src_remove_button.pack(side=tk.LEFT, padx=(0, 10))

        self.dest_label = tk.Label(self.window, text="Destination Directories")
        self.dest_label.pack(pady=(10, 0))

        self.dest_listbox = tk.Listbox(self.window, selectmode=tk.MULTIPLE)
        self.dest_listbox.pack(padx=10, pady=(5, 10), fill=tk.BOTH, expand=True)

        self.dest_add_button = tk.Button(self.window, text="Add", command=self.add_dest_dir)
        self.dest_add_button.pack(side=tk.LEFT, padx=(10, 5))

        self.dest_remove_button = tk.Button(self.window, text="Remove", command=self.remove_dest_dir)
        self.dest_remove_button.pack(side=tk.LEFT, padx=(0, 10))

        self.start_button = tk.Button(self.window, text="Start", command=self.start_backup_system)
        self.start_button.pack(side=tk.LEFT, padx=(10, 5), pady=(0, 10))

        self.stop_button = tk.Button(self.window, text="Stop", command=self.stop_backup_system, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10), pady=(0, 10))

        self.status_label = tk.Label(self.window, text="")
        self.status_label.pack(pady=(0, 10))

    def add_src_dir(self):
        src_dir = filedialog.askdirectory()
        if src_dir not in self.src_dirs:
            self.src_dirs.append(src_dir)
            self.src_listbox.insert(tk.END, src_dir)

    def remove_src_dir(self):
        selection = self.src_listbox.curselection()
        if len(selection) > 0:
            index = selection[0]
            src_dir = self.src_dirs[index]
            self.src_dirs.remove(src_dir)
            self.src_listbox.delete(index)

    def add_dest_dir(self):
        dest_dir = filedialog.askdirectory()
        if dest_dir not in self.dest_dirs:
            self.dest_dirs.append(dest_dir)
            self.dest_listbox.insert(tk.END, dest_dir)

    def remove_dest_dir(self):
        selection = self.dest_listbox.curselection()
        if len(selection) > 0:
            index = selection[0]
            dest_dir = self.dest_dirs[index]
            self.dest_dirs.remove(dest_dir)
            self.dest_listbox.delete(index)

    def start_backup_system(self):
        if len(self.src_dirs) == 0 or len(self.dest_dirs) == 0:
            return

        self.src_listbox.config(state=tk.DISABLED)
        self.dest_listbox.config(state=tk.DISABLED)
        self.src_add_button.config(state=tk.DISABLED)
        self.src_remove_button.config(state=tk.DISABLED)
        self.dest_add_button.config(state=tk.DISABLED)
        self.dest_remove_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        self.status_label.config(text="Backup system started. Monitoring directories for changes.")

        self.event_handlers = []

        for src_dir in self.src_dirs:
            for dest_dir in self.dest_dirs:
                event_handler = BackupEventHandler(src_dir, dest_dir)
                self.event_handlers.append(event_handler)
                observer = Observer()
                observer.schedule(event_handler, src_dir, recursive=True)
                observer.start()

        self.observer_running = True
        try:
            while self.observer_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_backup_system()

    def stop_backup_system(self):
        self.observer_running = False
        for event_handler in self.event_handlers:
            event_handler.stop()
        self.status_label.config(text="Backup system stopped.")
        self.src_listbox.config(state=tk.NORMAL)
        self.dest_listbox.config(state=tk.NORMAL)
        self.src_add_button.config(state=tk.NORMAL)
        self.src_remove_button.config(state=tk.NORMAL)
        self.dest_add_button.config(state=tk.NORMAL)
        self.dest_remove_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def run(self):
        self.window.mainloop()

backup_system_gui = BackupSystemGUI()
backup_system_gui.run()