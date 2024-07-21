import os
import socket
import threading
import time
from typing import List
import tkinter as tk
from tkinter import filedialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import psutil


class FileUploadEventHandler(FileSystemEventHandler):
    def __init__(self, server_address, server_port, report_label):
        super().__init__()
        self.server_address = server_address
        self.server_port = server_port
        self.report_label = report_label
        self.response_time_label = response_time_label
        self.memory_usage_label = memory_usage_label

    def on_modified(self, event):
        if not event.is_directory:
            self.report_label.config(text=f"Detected modification to {event.src_path}, uploading to server...")
            # Measure response time
            start_time = time.time()
            upload_file(self.server_address, self.server_port, event.src_path)
            end_time = time.time()
            elapsed_time = end_time - start_time
            response_time = end_time - start_time
            
            # Get memory usage
            memory_used = psutil.virtual_memory().used / (1024 * 1024)  # in megabytes
            
            # Update the labels with metrics
            self.report_label.config(text=f"File uploaded successfully.")
            self.response_time_label.config(text=f"Response Time: {response_time:.2f} seconds")
            self.memory_usage_label.config(text=f"Memory Usage: {memory_used:.2f} MB")

def upload_file(server_address, server_port, file_path):
    # create the client socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # connect to the server
        client_socket.connect((server_address, server_port))

        # send the upload request with the filename
        filename = os.path.basename(file_path)
        request = f"UPLOAD {filename}"
        client_socket.sendall(request.encode())

        # send the file data to the server
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(1024)
                if not chunk:
                    break
                client_socket.sendall(chunk)

        print(f"File {filename} uploaded to server.")

def watch_directories(directories_to_watch: List[str], server_address: str, server_port: int, report_label):
    # create a file system event handler to monitor changes to the selected directories
    event_handler = FileUploadEventHandler(server_address, server_port, report_label)

    # create an observer to watch for changes to the selected directories
    observer = Observer()
    for path in directories_to_watch:
        observer.schedule(event_handler, path, recursive=True)
    observer.start()

    report_label.config(text=f"Monitoring directories {', '.join(directories_to_watch)} for changes...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

def on_select_directories():
    global directories_to_watch
    directories = []
    while True:
        directory = filedialog.askdirectory()
        if not directory:
            break
        directories.append(directory)
    directories_to_watch = directories
    directories_label.config(text=f"Selected directories: {', '.join(directories)}")

def on_connect():
    global is_connected
    global server_address
    global server_port
    if not is_connected:
        threading.Thread(target=watch_directories, args=(directories_to_watch, server_address.get(), int(server_port.get()), report_label)).start()
        is_connected = True
        status_label.config(text=f"Connected to server {server_address.get()}:{server_port.get()}!")
    else:
        status_label.config(text="Already connected to server.")

if __name__ == "__main__":
    # initialize the directories to monitor
    directories_to_watch = []

    # initialize the connection status
    is_connected = False

    # create the GUI
    root = tk.Tk()
    root.title("Directory Watcher")

    # create the select directories button
    select_directories_button = tk.Button(root, text="Select Directories", command=on_select_directories)
    select_directories_button.pack()

    # create the selected directories label
    directories_label = tk.Label(root, text="")
    directories_label.pack()

    # create the server address entry widget
    server_address_label = tk.Label(root, text="Server Address:")
    server_address_label.pack()
    server_address = tk.Entry(root, width=30)
    server_address.pack()
    server_address.insert(0, "192.168.1.4")

    # create the server port entry widget
    server_port_label = tk.Label(root, text="Server Port:")
    server_port_label.pack()
    server_port = tk.Entry(root, width=30)
    server_port.pack()
    server_port.insert(0, "5500")

    # create the connect button
    connect_button = tk.Button(root, text="Connect", command=on_connect)
    connect_button.pack()
    # Create labels for benchmark metrics
    execution_time_label = tk.Label(root, text="")
    execution_time_label.pack()
    response_time_label = tk.Label(root, text="")
    response_time_label.pack()
    memory_usage_label = tk.Label(root, text="")
    memory_usage_label.pack()
    execution_time_label = tk.Label(root, text="")
    execution_time_label.pack()
    # create the status label
    status_label = tk.Label(root, text="")
    status_label.pack()

    # create the report label
    report_label = tk.Label(root, text="")
    report_label.pack()
    # Create a thread to monitor CPU usage
    #cpu_l-tk.Label(root.psutil.cpu_percent(4))
    #cpu_l.pack()
    #cpu_monitor_thread = threading.Thread(target=monitor_cpu_usage, args=(5, cpu_label))
    
    #cpu_monitor_thread.start()

    # run the GUI
    root.mainloop()