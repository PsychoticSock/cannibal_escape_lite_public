from binary_file_parser import BaseStruct, Retriever
from binary_file_parser.types import int32, Array32

from horde_labels import horde_names, unit_class_labels
from cannibal_labels import cannibal_names, unit_class_labels

mod_names = cannibal_names

_color = {
    'end': '\033[0m',
    'black': '\033[30m',
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_black": "\033[90m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bright_white": "\033[97m",
}


class Log(BaseStruct):
    ticks: int = Retriever(int32)
    delta: int = Retriever(int32)
    unit_id: int = Retriever(int32)
    unit_count: int = Retriever(int32)

    def __repr__(self):
        formatted_ticks = str(self.ticks).ljust(8)
        if self.delta < 0:
            formatted_delta = _color['red'] + str(self.delta).rjust(len(str(self.delta))) +_color['white'] + "\t\tID"
        else:
            formatted_delta = _color['green'] +str(self.delta).rjust(len(str(self.delta))+1) +_color['white'] + "\t\tID"
        if self.unit_id < 1800:
            if self.unit_id >= 900 and self.unit_id < 1000:
                formatted_unit_id = _color['yellow'] + str(self.unit_id).rjust(5) +_color['white']
            else:
                formatted_unit_id = str(self.unit_id).rjust(5)
        else:
            formatted_unit_id = _color['red'] + str(self.unit_id).rjust(5) + _color['white']

        formatted_unit_count = str(self.unit_count).rjust(5)
        if self.unit_id >= 900 and self.unit_id < 962:
            mod_internal_name = _color['yellow'] + unit_class_labels[int(self.unit_id)] + _color['white']
        else:
            if self.unit_id < 1800:
                mod_internal_name = mod_names[int(self.unit_id)]
            else:
                mod_internal_name = _color['red'] + mod_names[int(self.unit_id)] + _color['white']



        print_string = f"\tTicks: {formatted_ticks} Delta:\t{formatted_delta} \t{formatted_unit_id} \t\tCount: \t{formatted_unit_count}\t {mod_internal_name}"
        return print_string
    # implement a __eq__ function, look this up

class LogFile(BaseStruct):
    logs: list[Log] = Retriever(Array32[Log])

#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\default0.xsdat"
logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\cannibal_unit_logger_1.xsdat"
#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\horde_variable_sampling.xsdat"
#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\crash_siege_tower.xsdat"

#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\.xsdat"
#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\horde_crashes\\scorp_tower_crashtest.xsdat"
#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\horde_crashes\\crash_siege_tower.xsdat"
#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\horde_crashes\\scorpion_crash_2.xsdat"
#logfilename = "C:\\Users\\Username\\Games\\Age of Empires 2 DE\\ID_Number\\profile\\horde_crashes\\most_scorps_dead.xsdat"

file = LogFile.from_file(logfilename)
print(file)
for x, log in enumerate(file.logs):
    print(x, log)
"""
prev_log = None
while True:
    log = Log.from_file(logfilename)
    if not prev_log:
        print(log)
        for x, log in enumerate(file.logs):
            print(x, log)
    prev_log = log"""


