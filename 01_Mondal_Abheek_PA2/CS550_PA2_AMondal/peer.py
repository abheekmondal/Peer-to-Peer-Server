import shutil, time
import socket, hashlib, json, os, time, argparse, threading, logging, signal, random, sys

class PeerNode:
    def __init__(self, host, port, files_dir, indexing_server_ip, indexing_server_port):
        self.host = host
        self.port = port
        self.files_dir = files_dir
        self.indexing_server_ip = indexing_server_ip
        self.indexing_server_port = indexing_server_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.file_list = {}

    def register_with_indexing_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.indexing_server_ip, self.indexing_server_port))
        client_socket.sendall(f'register {self.host}:{self.port}'.encode())
        client_socket.close()
        logging.info(f'Successfully registered with indexing server at {self.indexing_server_ip}:{self.indexing_server_port}')

    def get_file_list(self):
        file_list = {}
        for filename in os.listdir(self.files_dir):
            file_path = os.path.join(self.files_dir, filename)
            if os.path.isfile(file_path):
                file_list[filename] = os.path.getsize(file_path)
        return file_list

    def handle_client(self, client_socket, address):
        # Receive request from client
        request = client_socket.recv(1024).decode()
        if request.startswith("download "):
            # Handle file download request
            filename = request.split()[1]
            file_path = os.path.join(self.files_dir, filename)
            if os.path.isfile(file_path):
                with open(file_path, "rb") as f:
                    data = f.read()
                checksum = hashlib.md5(data).hexdigest()
                client_socket.sendall(data)
                client_socket.close()
                logging.info(f"Sent file {filename} ({len(data)} bytes) to {address}. Checksum: {checksum}")
            else:
                client_socket.sendall(f"File {filename} not found".encode())
                client_socket.close()
                logging.error(f"File {filename} not found")
        else:
            # Handle unknown request
            client_socket.sendall(f"Unknown request: {request}".encode())
            client_socket.close()
            logging.error(f"Unknown request: {request}")

    def unregister_from_indexing_server(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.indexing_server_ip, self.indexing_server_port))
        client_socket.sendall(f'unregister {self.host}:{self.port}'.encode())
        client_socket.close()
        logging.info(f'Successfully unregistered from indexing server at {self.indexing_server_ip}:{self.indexing_server_port}')
        sys.exit(0)
    
    def query_indexing_server(self, filename):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.indexing_server_ip, self.indexing_server_port))
        client_socket.sendall(f'query {filename}'.encode())
        response = client_socket.recv(1024).decode()
        client_socket.close()
        if response == 'not found':
            return []
        else:
            return json.loads(response)

    def download_file(self, peer_node, filename):
        host, port = peer_node.split(':')
        port = int(port)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        client_socket.sendall(f'download {filename}'.encode())
        data = b''
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            data += chunk
        client_socket.close()
        checksum = hashlib.md5(data).hexdigest()
        file_path = os.path.join(self.files_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(data)
        logging.info(f"Received file {filename} ({len(data)} bytes) from {peer_node}. Checksum: {checksum}")

    def handle_incoming_file_download_requests(self):
        while True:
            client_socket, address = self.server_socket.accept()
            logging.info(f'Received file download request from {address}')
            t = threading.Thread(target=self.handle_client, args=(client_socket, address))
            t.start()

    def register_files_with_indexing_server(self, files):
        # Connect to indexing server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.indexing_server_ip, self.indexing_server_port))

        # Register node and files with indexing server
        file_info = []
        for filename in files:
            file_path = os.path.join(self.directory, filename)
            with open(file_path, 'rb') as f:
                data = f.read()
            file_hash = hashlib.sha256(data).hexdigest()
            file_size = os.path.getsize(file_path)
            file_info.append({'filename': filename, 'filehash': file_hash, 'filesize': file_size})
        request = json.dumps({'command': 'register', 'node_address': self.address, 'files': file_info})
        client_socket.sendall(request.encode())
        client_socket.close()

    def update_file_list(self):
        # Connect to indexing server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.indexing_server_ip, self.indexing_server_port))

        # Request file list from indexing server
        request = json.dumps({'command': 'get_files_list'})
        client_socket.sendall(request.encode())

        # Receive file list from indexing server
        response = client_socket.recv(1024).decode()
        file_list = json.loads(response)
        client_socket.close()
        
        # Display file list
        print('List of available files:')
        for filename, file_size in file_list.items():
            print(f'{filename} ({file_size} bytes)')

    def query_indexing_server_for_peer_list(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.indexing_server_ip, self.indexing_server_port))
        client_socket.sendall(b'peer_list')
        response = client_socket.recv(1024).decode()
        client_socket.close()
        if response == 'not found':
            return []
        else:
            return json.loads(response)

    def delete_folder(self):
        shutil.rmtree(self.files_dir)

    def start(self):
        # Register with indexing server when starting
        self.register_with_indexing_server()
        # Update file list
        self.file_list = self.get_file_list()
        # Handle exit signal
        signal.signal(signal.SIGINT, self.unregister_from_indexing_server)
        while True:
            print(f'\nMenu - Peer {self.port}:')
            print('1. Host files')
            print('2. List hosted files')
            print('3. Download file')
            print('4. Update file list')
           # print('5. List host peers')
            print('6. Unregister from indexing server')
            print('7. Exit')
            choice = input('Enter your choice: ')

            if choice == '1':
                print('Hosting files...')
                # Start a new thread to handle incoming file download requests
                t = threading.Thread(target=self.handle_incoming_file_download_requests)
                t.start()
                # Update file list
                self.file_list = self.get_file_list()

            elif choice == '2':
                print('List of hosted files:')
                for filename, file_size in self.file_list.items():
                    print(f'{filename} ({file_size} bytes)')

            elif choice == '3':
                filename = input('Enter the name of the file to download: ')
                if filename in self.file_list:
                    # Query indexing server for peer nodes associated with the requested file
                    peer_nodes = self.query_indexing_server(filename)
                    if peer_nodes:
                        # Randomly select a peer node
                        selected_peer = random.choice(peer_nodes)
                        # Download the file from the selected peer
                        self.download_file(selected_peer, filename)
                    else:
                        print(f'No peer node found for {filename}')
                else:
                    print(f'File {filename} not found in hosted files')

            elif choice == '4':
                print('Updating file list...')
                # Update file list
                self.file_list = self.get_file_list()

            # elif choice == '5':
            #     print('List of host peers:')
            #     # Query indexing server for the list of registered peer nodes
            #     peer_nodes = self.query_indexing_server_for_peer_list()
            #     if peer_nodes:
            #         for peer_node in peer_nodes:
            #             print(f'Peer {peer_node[1]}')
            #     else:
            #         print('No host peers found')

            elif choice == '6':
                print('Unregistering from indexing server...')
                # Unregister from indexing server
                self.unregister_from_indexing_server()

            elif choice == '7':
                print('Exiting...')
                self.delete_folder()
                sys.exit(0)

            else:
                print('Invalid choice')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Peer node for file sharing network')
    parser.add_argument('--host', type=str, default='localhost', help='host IP address')
    parser.add_argument('--port', type=int, help='host port')
    parser.add_argument('--indexing-server-ip', type=str, default='localhost', help='indexing server IP address')
    parser.add_argument('--indexing-server-port', type=int, default=1313, help='indexing server port')
    args = parser.parse_args()

    # If the port argument is not specified, find an unused port
    if args.port is None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 0))
        args.port = s.getsockname()[1]
        s.close()

    # Create folder for files if it does not exist
    files_dir = f'Peer{args.port}'
    if not os.path.exists(files_dir):
        os.makedirs(files_dir)
    peer_node = PeerNode(args.host, args.port, files_dir, args.indexing_server_ip, args.indexing_server_port)
    peer_node.start()