#!/bin/bash

# Set variables
SERVER_IP_ADDRESS="127.0.0.1"
PORT=1313
PEERS="peer.py"
SERVER="server.py"
FILE_DIRECTORY="shared_files"

# Deploy server
python3 $SERVER &

# Deploy three peer nodes
for i in {1..3}
do
  # Create peer directory if it does not exist
  peer_directory="$PEER_DIRECTORY_PREFIX$i"
  if [ ! -d "$peer_directory" ]; then
    mkdir -p "$peer_directory"
  fi

  # Copy peer code to peer directory
  cp peer.py "$peer_directory"

  # Start peer process
  cd "$peer_directory"
  python3 peer.py "$PEER_PORT" &
done
