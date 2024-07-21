import socket
import os
import datetime

def handle_client(client_socket, client_address, file_directory):
    print(f"Accepted connection from {client_address}")
    with client_socket:
        while True:
            # receive the client request
            data = client_socket.recv(1024).decode().strip()
            if not data:
                break
            print(f"Received request {data} from {client_address}")

            # parse the request
            parts = data.split(" ")
            if len(parts) < 2:
                client_socket.sendall("ERROR Invalid request".encode())
                continue

            command = parts[0]
            filename = " ".join(parts[1:])

            # handle the request
            if command == "UPLOAD":
                # receive the file data
                with open(os.path.join(file_directory, filename), "wb") as f:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        f.write(data)
                print(f"Received file {filename} from {client_address}")
                # generate a report
                report = f"{datetime.datetime.now()}: Uploaded file {filename} from {client_address}"
                print(report)
                client_socket.sendall("OK".encode())
            elif command == "REPLACE":
                # receive the file data
                with open(os.path.join(file_directory, filename), "wb") as f:
                    while True:
                        data = client_socket.recv(1024)
                        if not data:
                            break
                        f.write(data)
                print(f"Replaced file {filename} from {client_address}")
                # generate a report
                report = f"{datetime.datetime.now()}: Replaced file {filename} from {client_address}"
                print(report)
                client_socket.sendall("OK".encode())
            elif command == "CHECK":
                # check if the file exists
                if os.path.exists(os.path.join(file_directory, filename)):
                    client_socket.sendall("EXISTS".encode())
                else:
                    client_socket.sendall("NOT FOUND".encode())
            elif command == "DELETE":
                # delete the file
                try:
                    os.remove(os.path.join(file_directory, filename))
                    print(f"Deleted file {filename} from {client_address}")
                    # generate a report
                    report = f"{datetime.datetime.now()}: Deleted file {filename} from {client_address}"
                    print(report)
                    client_socket.sendall("OK".encode())
                except OSError:
                    print(f"Failed to delete file {filename} from {client_address}")
                    # generate a report
                    report = f"{datetime.datetime.now()}: Failed to delete file {filename} from {client_address}"
                    print(report)
                    client_socket.sendall("ERROR".encode())
            else:
                client_socket.sendall("ERROR Invalid command".encode())

def start_server(address, port, file_directory):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((address, port))
        server_socket.listen()

        print(f"Server listening on {address}:{port}, serving files from {file_directory}")

        while True:
            client_socket, client_address = server_socket.accept()
            handle_client(client_socket, client_address, file_directory)

if __name__ == "__main__":
    address = "192.168.1.5"
    port = 5150
    file_directory = "C:\\app1"

    start_server(address, port, file_directory)