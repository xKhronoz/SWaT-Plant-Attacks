import time
from pylogix import PLC
import random

PLC_IPS = {
    'plc1'      : '192.168.1.10',
    'plc2'      : '192.168.1.20',
    'plc3'      : '192.168.1.30',
    'plc4'      : '192.168.1.40',
    'plc5'      : '192.168.1.50',
    'plc6'      : '192.168.1.60',
    'plc1r'     : '192.168.1.11',
    'plc2r'     : '192.168.1.21',
    'plc3r'     : '192.168.1.31',
    'plc4r'     : '192.168.1.41',
    'plc5r'     : '192.168.1.51',
    'plc6r'     : '192.168.1.61',
    'scada'     : '192.168.1.211'
}

dtypes = {
    "STRUCT"    : 160,
    "BOOL"      : 193,
    "SINT"      : 194,
    "INT"       : 195,
    "DINT"      : 196,
    "LINT"      : 197,
    "USINT"     : 198,
    "UINT"      : 199,
    "UDINT"     : 200,
    "LWORD"     : 201,
    "REAL"      : 202,
    "LREAL"     : 203,
    "DWORD"     : 211,
    "STRING"    : 218
}

def discover_devices():
    with PLC() as comm:
        devices = comm.Discover()
    for device in devices.Value:
        print(device.IPAddress)
        print('  Product Code: ' + device.ProductName + ' ' + str(device.ProductCode))
        print('  Vendor/Device ID:' + device.Vendor + ' ' + str(device.DeviceID))
        print('  Revision/Serial:' +  device.Revision + ' '  + device.SerialNumber)
        print('')

def plc_write(plc_ip, tag_name, value, dtype = None):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        comm.Write(tag_name, value, datatype = dtype)

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

def plc_read(plc_ip, tag_name, dtype = None):
    with PLC() as comm:
        comm.IPAddress = plc_ip
        ret = comm.Read(tag_name, datatype = dtype)
        print(ret.Value)
        return (ret.Value)

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

def main():

    # LIT101 = plc_read(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', dtypes['REAL'])
    # plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', True, dtypes['BOOL'])
    plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', False, dtypes['BOOL'])
    plc_write(PLC_IPS['plc1'], 'HMI_MV101.Cmd', 2, dtypes['INT'])
    while(1):
        LIT101 = plc_read(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', dtypes['REAL'])
        # LIT101+=round(random.uniform(0,0.5),2)
        # plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', LIT101, dtypes['REAL'])
        print(LIT101)
        time.sleep(1)
    # if LIT101 > 800:
    #     plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', True, dtypes['BOOL'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', False, dtypes['BOOL'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_MV101.Cmd', 1, dtypes['INT'])
    #     for i in range(0,300):
    #         LIT101+=randrange (0,3,1)
    #         plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', LIT101, dtypes['REAL'])
    #         time.sleep(1.5)
    # else:
    #     plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', True, dtypes['BOOL'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', False, dtypes['BOOL'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_MV101.Cmd', 1, dtypes['INT'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_P101.Auto', False, dtypes['BOOL'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_P101.Cmd', 1, dtypes['INT'])
    #     for i in range(0,300):
    #         LIT101-=randrange (0,3,1)
    #         plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim_PV', LIT101, dtypes['REAL'])
    #         time.sleep(1)
    #     plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', False, dtypes['BOOL'])
    #     plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', True, dtypes['BOOL'])
    #     time.sleep(600)

if __name__ == '__main__':
    try:
       main()
    # tags = get_all_tags(PLC_IPS['plc1'])
    # for t in tags.Value:
    #     if 'HMI' in t.TagName:
    #         print(t.TagName, t.DataType)
    except:
       plc_write(PLC_IPS['plc1'], 'HMI_LIT101.Sim', False, dtypes['BOOL'])
       plc_write(PLC_IPS['plc1'], 'HMI_MV101.Auto', True, dtypes['BOOL'])
       plc_write(PLC_IPS['plc1'], 'HMI_P101.Auto', True, dtypes['BOOL'])
