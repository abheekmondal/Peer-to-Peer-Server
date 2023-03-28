import socket
import os
import json
import hashlib
import threading

class ClientThread(threading.Thread):
    def __init__(self, client_socket, client_address, file_directory):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.client_address = client_address
        self.file_directory = file_directory
        self.nodes = server.nodes

    def run(self):
        while True:
            try:
                data = self.client_socket.recv(1024).decode()
            except ConnectionAbortedError:
                self.client_socket.close()
                break
            if not data:
                break

            tokens = data.split()
            if len(tokens) < 3:
                self.client_socket.sendall(b'Error: Not enough arguments provided.')
                continue

            command = tokens[0]
            if command == 'get_files_list':
                file_list = self.get_file_list()
                self.client_socket.sendall(json.dumps(file_list).encode())
            elif command == 'download':
                filename = tokens[1]
                file_path = os.path.join(self.file_directory, filename)
                if not os.path.isfile(file_path):
                    self.client_socket.sendall(f'File {filename} not found on server.'.encode())
                else:
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    self.client_socket.sendall(data)
            elif command == 'register':
                node_address = tokens[1]
                files = json.loads(tokens[2])
                self.register_node(node_address, files)
            elif command == 'unregister':
                node_address = tokens[1]
                self.unregister_node(node_address)
            elif command == 'add_file':
                node_address = tokens[1]
                filename = tokens[2]
                file_size = int(tokens[3])
                self.add_file(node_address, filename, file_size)
            elif command == 'delete_file':
                node_address = tokens[1]
                filename = tokens[2]
                self.delete_file(node_address, filename)
            elif command == 'update_files_list':
                print(f"Node {self.client_address[0]} has requested an updated file list.")
                file_list = self.get_file_list()
                self.client_socket.sendall(json.dumps(file_list).encode())
                print("Update complete.")

        self.client_socket.close()



    def get_file_list(self):
        files = os.listdir(self.file_directory)
        file_list = {}
        for filename in files:
            file_path = os.path.join(self.file_directory, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                file_list[filename] = file_size
        return file_list


    def register_node(self, node_address, files):
        if len(tokens) < 3:
            self.client_socket.sendall("Error: Not enough parameters provided for register command.".encode())
            return

        if node_address not in self.nodes:
            self.nodes[node_address] = set()
        for file_info in files:
            filename = file_info['filename']
            file_hash = file_info['filehash']
            file_size = file_info['filesize']
            self.nodes[node_address].add((filename, file_hash, file_size))

    def unregister_node(self, node_address):
        if node_address in self.nodes:
            del self.nodes[node_address]

    def add_file(self, node_address, filename, file_size):
        file_path = os.path.join(self.file_directory, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            file_hash = hashlib.sha256(data).hexdigest()
            self.nodes[node_address].add((filename, file_hash, file_size))

    def delete_file(self, node_address, filename):
        if node_address in self.nodes:
            for file_info in self.nodes[node_address]:
                if file_info[0] == filename:
                    self.nodes[node_address].remove(file_info)
                    break

class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.file_directory = 'server_database'
        self.nodes = {}

    def start(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(5)
        print(f'Server listening on {self.ip}:{self.port}...')

        while True:
            client_socket, client_address = server_socket.accept()
            print(f'Accepted connection from {client_address[0]}:{client_address[1]}')
            client_thread = ClientThread(client_socket, client_address, self.file_directory)
            client_thread.start()

    def get_node_list(self, filename):
        nodes_with_file = []
        for node_address, files in self.nodes.items():
            if filename in files:
                nodes_with_file.append(node_address)
        return nodes_with_file


if __name__ == '__main__':
    server = Server('127.0.0.1', 1313)
    server_thread = threading.Thread(target=server.start)
    server_thread.start()
    server_thread.join()