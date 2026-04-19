from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.packet.ethernet import ethernet, ETHER_BROADCAST
from pox.lib.packet.arp import arp
from pox.lib.addresses import EthAddr

log = core.getLogger()

arp_table = {}     # IP -> MAC
mac_to_port = {}   # switch_dpid -> {mac: port}

def _handle_ConnectionUp(event):
    log.info("Switch connected: %s", event.connection)

def _handle_PacketIn(event):
    packet = event.parsed
    if not packet:
        return

    dpid = event.connection.dpid
    in_port = event.port

    if dpid not in mac_to_port:
        mac_to_port[dpid] = {}

    # Learn source MAC -> port
    mac_to_port[dpid][packet.src] = in_port

    # ARP handling
    a = packet.find('arp')
    if a:
        arp_table[a.protosrc] = a.hwsrc
        log.info("Learned ARP: %s -> %s", a.protosrc, a.hwsrc)

        # ARP request intercepted
        if a.opcode == arp.REQUEST:
            target_ip = a.protodst

            # If target IP known, generate ARP reply
            if target_ip in arp_table:
                reply = arp()
                reply.opcode = arp.REPLY
                reply.hwsrc = arp_table[target_ip]
                reply.hwdst = a.hwsrc
                reply.protosrc = target_ip
                reply.protodst = a.protosrc

                e = ethernet(type=ethernet.ARP_TYPE,
                             src=reply.hwsrc,
                             dst=packet.src)
                e.payload = reply

                msg = of.ofp_packet_out()
                msg.data = e.pack()
                msg.actions.append(of.ofp_action_output(port=in_port))
                event.connection.send(msg)

                log.info("Sent ARP reply: %s is-at %s", target_ip, arp_table[target_ip])
                return

    # Normal forwarding
    if packet.dst in mac_to_port[dpid]:
        out_port = mac_to_port[dpid][packet.dst]

        # Install flow rule
        fm = of.ofp_flow_mod()
        fm.match = of.ofp_match.from_packet(packet, in_port)
        fm.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(fm)

        # Forward current packet
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=out_port))
        event.connection.send(msg)
    else:
        # Flood unknown packets
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        event.connection.send(msg)

def launch():
    core.openflow.addListenerByName("ConnectionUp", _handle_ConnectionUp)
    core.openflow.addListenerByName("PacketIn", _handle_PacketIn)
    log.info("ARP handler controller started")
