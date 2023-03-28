README for server.py

The server.py file is an implementation of an indexing server that keeps track of the files and their associated metadata registered by the peers on the network. This indexing server provides a centralized repository where peers can search for files that are shared by other peers on the network.
Starting the Server

To start the server, simply run the server.py script. The server listens on IP address 127.0.0.1 and port 1313.
Menu Options

The indexing server provides a command-line interface with the following menu options:

    List files: This option allows the server to list all the files that have been registered by the peers on the network.
    Search file: This option allows the server to search for files by their name or by the name of their owner.
    Add file: This option allows the server to register a new file that has been added by a peer on the network.
    Delete file: This option allows the server to delete a file that has been registered by a peer on the network.

README for peer.py

The peer.py file is an implementation of a peer node that participates in a peer-to-peer network. Each peer node maintains a list of files that it has shared on the network, as well as a list of other peer nodes on the network.
Starting a Peer Node

To start a peer node, simply run the peer.py script. The peer node listens on IP address 127.0.0.1 and port 1313. Each peer will be generated with a unique peer port number, which creates a folder called peer <port number>. This file is deleted when the peer chooses to exit.

Menu Options

The peer node provides a command-line interface with the following menu options:

    List files: This option allows the peer to list all the files that it has shared on the network.

    Search file: This option allows the peer to search for files that have been shared by other peers on the network.

    Add file: This option allows the peer to add a new file to the list of files that it shares on the network.

    Delete file: This option allows the peer to delete a file from the list of files that it shares on the network.

    Register: This option allows the peer to register itself with the indexing server by providing its IP address and a list of files 	that it shares on the network.

    Unregister: This option allows the peer to unregister itself from the indexing server.

    Update: This option allows the peer to update the indexing server with changes to its list of shared files.

    Exit: This option allows the peer to exit the program.