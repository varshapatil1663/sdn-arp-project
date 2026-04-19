ARP Handling in SDN using POX and Mininet
Objective

Implement ARP request and reply handling using an SDN controller.
The controller intercepts ARP packets, generates responses, performs host discovery, and validates communication.
Features

    Intercept ARP packets at controller

    Generate ARP replies

    Maintain IP → MAC mapping (Host Discovery)

    Enable communication between hosts

    Validate using ping

Technologies Used

    Mininet

    POX Controller

    OpenFlow

    Ubuntu (Virtual Machine)

Project Structure

sdn-arp-project/
│
├── pox-files/
│   └── ext/
│       └── arp_handler.py
│
├── screenshots/
│   ├── ping.png
│   ├── arp.png
│   ├── logs.png
│
└── README.md

Setup and Execution
1. Install Mininet

sudo apt update
sudo apt install mininet openvswitch-switch -y

2. Install POX

git clone https://github.com/noxrepo/pox.git
cd pox

3. Run Controller

cd ~/pox
python3.8 pox.py log.level --DEBUG openflow.of_01 forwarding.l2_learning ext.arp_handler

4. Run Mininet

sudo mn --topo single,3 --mac --controller=remote,ip=127.0.0.1,port=6633

5. Test

Inside Mininet:

pingall

Expected output:

0% packet loss

Validation
ARP Table

h1 arp -n
h2 arp -n
h3 arp -n

Individual Ping

h1 ping -c 1 h2

Output

    All hosts successfully communicate

    ARP requests handled by controller

    IP-MAC mappings learned dynamically

    No packet loss in ping

Screenshots

Logs:
![logs](screenshots/Screenshot%20from%202026-04-19%2011-04-02.png)

Ping Result:
![ping](screenshots/Screenshot%20from%202026-04-19%2011-04-15.png)

ARP:
![arp](screenshots/Screenshot%20from%202026-04-19%2011-04-29.png)

Conclusion

Successfully implemented ARP handling in SDN using POX controller with host discovery and communication validation.
Author

Varsha Patil
