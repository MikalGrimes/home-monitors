"""Read the DS18B20 probe and append the reading to data/<slug>/YYYY-MM.csv.

usage: capture_temperature.py <slug>        e.g.  capture_temperature.py rpi03-temperature
"""
import glob
import os
import sys
import time

from datalog import append_reading

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

MAX_TRIES = 10


def read_temp_raw():
    base_dir = '/sys/bus/w1/devices/'
    device_folder = glob.glob(base_dir + '28*')[0]
    with open(device_folder + '/w1_slave', 'r') as f:
        return f.readlines()


def read_temp_f():
    for _ in range(MAX_TRIES):
        lines = read_temp_raw()
        if lines[0].strip()[-3:] == 'YES':  # CRC check passed
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
                return temp_c * 9.0 / 5.0 + 32.0
        time.sleep(0.2)
    raise RuntimeError("no valid reading from probe after {0} tries".format(MAX_TRIES))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    append_reading(sys.argv[1], read_temp_f())
