UDP Client-Server Program Documentation

Welcome to the UDP client-server program documentation. This document provides essential information on how to run and configure the UDP communication program, which includes both udpclient.py and udpserver.py.

Program Overview
This program simulates a basic UDP communication between a client and a server. It includes functionalities such as connection establishment, data transfer with simulated packet loss, and connection termination. The program is designed to be simple yet illustrative of key networking concepts.

Running Environment
Server: Runs on Ubuntu 20.04.6 LTS with Python version 3.8.10.
Client: Can be run on any system with Python 3.12.2 or compatible versions.
Client Program - udpclient.py
How to Run
Open a terminal and run the client program using the following command format:

python udpclient.py --serverIP <IP_ADDRESS> --serverPort <PORT> --packetsNum <NUMBER_OF_PACKETS>
For example:

python udpclient.py --serverIP 192.168.10.130 --serverPort 12345 --packetsNum 12
If no arguments are provided, the client will use default values.

Command Line Arguments
--serverIP: The IP address of the server. Default is 192.168.10.130.
--serverPort: The port on which the server is listening. Default is 12345.
--packetsNum: The number of packets the client will send. Default is 12.
Server Program - udpserver.py
How to Run
On the server machine, open a terminal and start the server with:

python udpserver.py
The server does not require command line arguments and will start listening for incoming connections on the default port.

Configuration Options
Buffer Size: Set by the buffer_size variable in both client and server scripts. Default is 1024 bytes.
Timeout: Set by the time_out variable. Default is 0.1 seconds (100ms).
Drop Rate: Simulated packet loss rate set by the drop_rate variable in the server script. Default is 0.05 (5%).
Note
Ensure that the server is running before starting the client.
The client and server must agree on the IP address and port for successful communication.
Getting Started
Start the server on the designated machine.
On the client machine, open a terminal and navigate to the directory containing udpclient.py.
Run the client with the desired command line arguments or use the defaults.
Additional Information
This program is for educational purposes and simulates aspects of network communication using UDP.
For any issues or feature requests, please create an issue on the associated GitHub repository.