"""
Latest @ 3/2/21
A client using tag names from the SWat.
This script is just to make testing the PLC easily,
but you may refer to it.

Currently, reading or writing strings is a big no no.
Other than that, the rest is fine.

If you want to not create a new session each time, (which you probably want)
feel free to edit the "with self.plc as comm:" line.

If you want to add on to this script, do credit me ty ty.

Author: Adrian Heng Yu Liang
Email: adrianhengyl@gmail.com
"""
from pylogix.eip import PLC


class CIPClient:
    TAGS = ["HMI_P1_STATE", "HMI_LIT101.Pv", "FIT101.Pv", "MV101.cmd",
            "P101.cmd", "P102.Status", "P2_STATE", "FIT201.Pv", "AIT201.Pv",
            "AIT202.Pv", "AIT203.Pv", "MV201.Status", "P201.Status",
            "P202.Status", "P203.Status", "P204.Status", "P205.Status",
            "P206.Status", "P207.Status", "P208.Status", "LS201.Alarm",
            "LS202.Alarm", "LSL203.Alarm", "LSLL203.Alarm", "P3_STATE",
            "AIT301.Pv", "AIT302.Pv", "AIT303.Pv", "LIT301.Pv", "FIT301.Pv",
            "DPIT301.Pv", "MV301.Status", "MV302.Status", "MV303.Status",
            "MV304.Status", "P301.Status", "P302.Status", "PSH301.Alarm",
            "DPSH301.Alarm", "P4_STATE", "LIT401.Pv", "FIT401.Pv", "AIT401.Pv",
            "AIT402.Pv", "P401.Status", "P402.Status", "P403.Status",
            "P404.Status", "UV401.Status", "LS401.Alarm", "P5_STATE",
            "FIT501.Pv", "FIT502.Pv", "FIT503.Pv", "FIT504.Pv", "AIT501.Pv",
            "AIT502.Pv", "AIT503.Pv", "AIT504.Pv", "PIT501.Pv", "PIT502.Pv",
            "PIT503.Pv", "P501.Status", "P502.Status", "MV501.Status",
            "MV502.Status", "MV503.Status", "MV504.Status", "PSH501.Alarm",
            "PSL501.Alarm", "P6_STATE", "FIT601.Pv", "P601.Status",
            "P602.Status", "P603.Status", "LSH601.Alarm", "LSL601.Alarm",
            "LSH602.Alarm", "LSL602.Alarm", "LSH603.Alarm", "LSL603.Alarm"]

    def __init__(self, host, port, tags=TAGS):
        self.host = host
        self.port = port
        self.tags = tags
        self.comm = PLC()
        self.comm.IPAddress = self.host
        self.comm.conn.Port = self.port

    def get_socket(self):
        return self.comm.conn.Socket

    def set(self, set_tags_dict, verbose=True):
        for tag in set_tags_dict:
            reply = self.comm.Write(tag, set_tags_dict[tag])
            if verbose:
                print(
                    f"[{reply.Status}] Set {tag} to {set_tags_dict[tag]}")
            return False
        return True

    def read(self, read_tag, verbose=True):
        data = self.comm.Read(read_tag)
        if verbose:
            print(f"[{data.Status}] {read_tag} = {data.Value}")
        return data.Value

    def read_all(self, verbose=True):
        output = dict()
        for tag in self.tags:
            data = self.comm.Read(tag)
            output[tag] = data.Value
            if verbose:
                print(f"[{data.Status}] {tag} = {data.Value}")
        return output

    def close(self):
        self.comm.close()

    # Currently doesn't work with CPPPO's server...
    # def get_tags(self, verbose=True):
    #     with self.plc as comm:
    #         comm.IPAddress = self.host
    #         comm.conn.Port = self.port
    #         tags = comm.GetTagList()
    #         if verbose:
    #             for t in tags.Value:
    #                 print(t.TagName, t.DataType)
    #         return tags


def test_interface():
    client = CIPClient(input("IP: "), int(input("Port: ")))
    while True:
        try:
            func_option = int(input("""
0. Show Tags
1. Read a specific tag
2. Read all
3. Set a tag
Input: """))
        except TypeError:
            print("Enter a valid option.")
        finally:
            if func_option == 0:
                print(' '.join(CIPClient.TAGS))
            elif func_option == 1:
                tag_to_read = input("Tag: ")
                client.read(tag_to_read)
            elif func_option == 2:
                client.read_all()
            elif func_option == 3:
                tag_to_set = input("Tag: ")
                value = input("Value: ")
                client.set({tag_to_set: value})
            else:
                print("Enter a valid option.")


if __name__ == "__main__":
    test_interface()
    # client = CIPClient("127.0.0.1", 44818)
    # client.read("P1_STATE")
