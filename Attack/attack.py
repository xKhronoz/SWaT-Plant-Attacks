from scapy.all import *
from scapy.utils import rdpcap

pkts = rdpcap("packets.pcap")
ip = get_if_addr(conf.iface)
mac = get_if_hwaddr(conf.iface)
print(ip, mac)
for pkt in pkts:
    del pkt[IP].chksum
    pkt[Ether].src = mac  # i.e new_src_mac="00:11:22:33:44:55"
    #pkt[IP].src = ip  # i.e new_src_ip="255.255.255.255"
    #pkt.display()
    srp1(pkt, timeout=2)  # sending packet at layer 2