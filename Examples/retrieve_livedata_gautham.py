"""The following code uses Pylogix package to communicate with the PLCs. In
the event that there is need to use Zmq just change the pylogix methods."""

from datetime import datetime
from pylogix import PLC
import re
import pandas as pd

STAGE1 = ['FIT101', 'LIT101', 'MV101', 'P101', 'P102']
STAGE2 = ['FIT201', 'MV201']
STAGE3 = ['FIT301', 'LIT301', 'MV301',
          'MV302', 'MV303', 'MV304', 'P301', 'P302']
STAGE4 = ['FIT401', 'LIT401', 'P401', 'P402', 'P403', 'P404']
STAGE5 = ['FIT501', 'FIT502', 'FIT503', 'FIT504', 'P501', 'P502']
STAGE6 = ['FIT601', 'P601', 'P602']

ALL_STAGES = ["LIT101", "FIT101", "MV101", "P101", "P102", "FIT201", "AIT201", "AIT202", "AIT203", "MV201", "P201", "P202", "P203",     "P204", "P205", "P206", "P207",
              "P208", "AIT301", "AIT302", "AIT303", "LIT301", "FIT301", "DPIT301", "MV301", "MV302", "MV303", "MV304", "P301", "P302", "LIT401", "FIT401", "AIT401",
              "AIT402", "P401", "P402", "P403", "P404", "UV401", "FIT501", "FIT502", "FIT503", "FIT504", "AIT501", "AIT502", "AIT503", "AIT504",
              "PIT501", "PIT502", "PIT503", "P501", "P502", "MV501", "MV502", "MV503", "MV504", "FIT601", "P601", "P602", "P603"]

DTYPES = {
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

# PLC IP address
PLC_IPS = {
    'plc1': '192.168.1.10',
    'plc2': '192.168.1.20',
    'plc3': '192.168.1.30',
    'plc4': '192.168.1.40',
    'plc5': '192.168.1.50',
    'plc6': '192.168.1.60',
}


def plc_read(plc_obj, tag_name, dtype=None):
    """Read data directly from PLC based on tag_name.

    Args:
        plc_obj (PLC()): Pylogix plc obj to maintain connection
        tag_name (str): HMI tag of the object 
        dtype (int, optional): Dtype to read the data from the PLC().
        Defaults to None.

    Returns:
        [type]: [description]
    """
    ret = plc_obj.Read(tag_name, datatype=dtype)
    return ret.Value


def return_plc_list():
    """Creates a PLCs object for each PLC IPAddress

    Returns:
        Dict: Dictionary of PLC objects based on IP addresses
    """
    plc_obj_dict = {}
    for key in PLC_IPS.keys():
        plc_obj = PLC()
        plc_obj.IPAddress = PLC_IPS[key]
        plc_obj_dict[key] = plc_obj
    return plc_obj_dict


def retrieve_value_dict(plc_dict_obj):
    """
    Format to add into the for loop to retrieve different readings.
    1) First change the ALL_STAGES list by adding the specific indicators you want to retrieve from the specific stages.
    2) Add the regex line below if the indicator is not LIT/FIT/P/MV. For example AIT indicators.
    elif re.match(r"AIT\d.+", element):
            no = str(re.findall(r"AIT(\d).+", element)[0])
            res_dict[element] = [
                plc_read(plc_dict_obj[f'plc{no}'], f'HMI_{element}.Sim_PV', DTYPES['INT'])]
    """
    res_dict = {}
    res_dict["Timestamp"] = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    # add a timestamp to the dictionary --> Timeformat e.g. "day-month-year hour:min:sec"
    for element in ALL_STAGES:  # List of all the stages that we want to retrieve
        # REGEX is used to determine which PLC to connect to detect
        # You may add another regex fi you want to add another indicator such as AITs just follow the example below
        # Change which indicator you want to view for example change LIT to AIT
        if re.match(r"LIT\d.+", element):
            # Change which indicator you want to view for example change FIT to AIT
            no = str(re.findall(r"LIT(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Sim_PV', DTYPES['REAL'])
            # Change the DTYPE object to the correct type that is used to read data
        elif re.match(r"FIT\d.+", element):
            no = str(re.findall(r"FIT(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Sim_PV', DTYPES['REAL'])
        elif re.match(r"P\d.+", element):
            no = str(re.findall(r"P(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Cmd', DTYPES['INT'])
        elif re.match(r"MV\d.+", element):
            no = str(re.findall(r"MV(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Cmd', DTYPES['INT'])
        elif re.match(r"AIT\d.+", element):
            no = str(re.findall(r"AIT(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Sim_Pv', DTYPES['REAL'])
        elif re.match(r"DPIT\d.+", element):
            no = str(re.findall(r"DPIT(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Sim_Pv', DTYPES['REAL'])
        elif re.match(r"PIT\d.+", element):
            no = str(re.findall(r"PIT(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Sim_PV', DTYPES['REAL'])
        elif re.match(r"UV\d.+", element):
            no = str(re.findall(r"UV(\d).+", element)[0])
            res_dict[element] = plc_read(plc_dict_obj[f'plc{no}'],
                                         f'HMI_{element}.Cmd', DTYPES['INT'])
    return res_dict


plc_dict_obj = return_plc_list()

while (True):
    res_dict = retrieve_value_dict(plc_dict_obj)
    # live_df = pd.DataFrame(res_dict)
    # live_df.dropna(inplace=True)
    # if live_df.isnull().values.any():
    #     continue
    # data_test = live_df
    # Add ["Timestamp"] if you need Timestamp added..
    # data_test variable already has timestamp inside
    print(res_dict)
