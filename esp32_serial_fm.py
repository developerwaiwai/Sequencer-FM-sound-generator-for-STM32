from ctypes import *
import serial
from struct import *
from multiprocessing import Process, connection, current_process
import time

import csv
from oto_data import *

from time import sleep

def make_serial_data_param(command, amp100, mul, attack, decay, sus_level100, release_level100):
    return pack("H", command) + pack("H", amp100) + pack("H", mul) + pack("I", 0) + pack("Q", attack) + pack("Q", decay) + pack("H", sus_level100) + pack("H", release_level100) + pack("I", 0)


def make_serial_data_note(command, on_off, algorism, tempo, helz, note_type, velocity):
    return pack('H', command) + pack('H', on_off) + pack('H', algorism) + pack('H', tempo) + pack('H', helz) + pack('Q', note_type) + pack('Q', velocity) + pack('Q', 0)


def send_algorism_param(serial, param_num, amp100, mul, attack, decay, sus_level100, release_level100):
    param_data = make_serial_data_param(param_num, amp100, mul, attack, decay, sus_level100, release_level100)
    serial.write(param_data)
    serial.read()    #return ACK


def send_algorism_param_cache(serial, param_cache):
    for param in param_cache:
        serial.write(param)
        serial.read()    #return ACK


def send_note(serial, on_off, algorism_num, tempo, helz, notetype, velocity):
    note_data = make_serial_data_note(0x10, on_off, algorism_num, tempo, helz, notetype, velocity)

    ack = 0
    while ack == 0:
        serial.write(note_data)
        b = serial.read()    #return ACK
        b_int = unpack("B", b)
        ack = b_int[0]
        time.sleep(1000./1000000.)
        # if ack == 0:
        #     time.sleep(50/1000000.)

def read_and_send_sound_param(serial, file_name):
    f = open(file_name, "r")
    d = csv.DictReader(f)
    index = 1
    for row in d:
        if row["amp100"] is "":
            break
        send_algorism_param(serial, index, int(row["amp100"]), int(row["multiple"]), int(row["attack"]), int(row["decay"]), int(row["sus_level100"]), int(row["rel_level100"]))
        index = index + 1
    f.close()


def read_sound_param(serial, file_name):

    param_cache = []
    f = open(file_name, "r")
    d = csv.DictReader(f)
    index = 1
    for row in d:
        if row["amp100"] is "":
            break
        param = make_serial_data_param(index, int(row["amp100"]), int(row["multiple"]), int(row["attack"]), int(row["decay"]), int(row["sus_level100"]), int(row["rel_level100"]))
        param_cache.append(param)
        index = index + 1
    f.close()

    return param_cache


def read_and_send_note(serial, file_name,sound_color_list):

    sound_color_cache = []
    if len(sound_color_list) > 1:
        index = 0
        for sound_color in sound_color_list:
            sound_color = read_sound_param(serial, sound_color_list[index])
            sound_color_cache.append(sound_color)
            index = index + 1

    f = open(file_name, "r")
    d = csv.DictReader(f)
    for row in d:
        if row["on_off"] is "":
            continue;
        if row["on_off"] is "@":
            send_algorism_param_cache(serial, sound_color_cache[int(row["algorism"])])
#            read_and_send_sound_param(serial, sound_color_list[int(row["algorism"])])
            continue

        length_data = row["length"]
        length_data.upper()
        len_int = 0;
        if '&' in length_data:
            for l in length_data.split('&'):
                len_int += int(ONPU[l])
        else:
            len_int = int(ONPU[length_data])

        velocity = 127
        if "velocity" in row:
            velocity = int(row["velocity"])

        send_note(serial, int(row["on_off"]), int(row["algorism"]), int(row["tempo"]), int(ONKAI[row["helz"]]), len_int, velocity)
    f.close()



#def fm_sound_transfer(serial_port, sound_color_file, note_file):
def fm_sound_transfer(row):
    sound_color_list = []
    for i in range(len(row) - 3):
        sound_color_list.append(row[3 + i])

    serial_port = row[0]
    sound_color_file = sound_color_list[0]
    note_file = row[2]
    boud_rate = row[1]

    print serial_port + sound_color_file + note_file
    s = serial.Serial(serial_port, baudrate=int(boud_rate), bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE)
    s.timeout = 30.0
    read_and_send_sound_param(s, sound_color_file)
    read_and_send_note(s, note_file,sound_color_list)

    s.close()

pool = []
settings_filename = "settings.csv"
f = open(settings_filename)
data = csv.reader(f, delimiter=",", doublequote=True, lineterminator="\n", quotechar='"', skipinitialspace=True)
for row in data:
    if row[0] is "":
        break
#    pool.append(Process(target=fm_sound_transfer, args=(port, sound_color, note)))
    pool.append(Process(target=fm_sound_transfer, args=(row,)))


for p in pool:
    p.start()

sleep(1.0)

for p in pool:
    p.join()


f.close()











# param_data = make_serial_data_param(1, 100, 1, 300, 1000000, 0, 0)
# s.write(param_data)
# s.read()
#
# param_data = make_serial_data_param(2, 50, 2, 300, 1000000, 0, 0)
# s.write(param_data)
# s.read()
#
# param_data = make_serial_data_param(3, 300, 3, 300, 1000000, 0, 0)
# s.write(param_data)
# s.read()
#
# param_data = make_serial_data_param(4, 100, 4, 300, 1000000, 0, 0)
# s.write(param_data)
# s.read()

# note_data = make_serial_data_note(0x10, 1, 7, 120, 392, 500000)
# s.write(note_data)
# s.read()
#
# note_data = make_serial_data_note(0x10, 1, 7, 120, 330, 500000)
# s.write(note_data)
# s.read()
#
# note_data = make_serial_data_note(0x10, 1, 7, 120, 330, 1000000)
# s.write(note_data)
# s.read()
#
# note_data = make_serial_data_note(0x10, 1, 7, 120, 349, 500000)
# s.write(note_data)
# s.read()
#
# note_data = make_serial_data_note(0x10, 1, 7, 120, 294, 500000)
# s.write(note_data)
# s.read()
#
# note_data = make_serial_data_note(0x10, 1, 7, 120, 294, 1000000)
# s.write(note_data)
# s.read()
#
#
# note_data = make_serial_data_note(0x10, 1, 7, 120, 262, 500000)
# s.write(note_data)
# s.read()
# note_data = make_serial_data_note(0x10, 1, 7, 120, 294, 500000)
# s.write(note_data)
# s.read()
# note_data = make_serial_data_note(0x10, 1, 7, 120, 330, 500000)
# s.write(note_data)
# s.read()
# note_data = make_serial_data_note(0x10, 1, 7, 120, 349, 500000)
# s.write(note_data)
# s.read()
# note_data = make_serial_data_note(0x10, 1, 7, 120, 392, 500000)
# s.write(note_data)
# s.read()
# note_data = make_serial_data_note(0x10, 1, 7, 120, 392, 500000)
# s.write(note_data)
# s.read()
# note_data = make_serial_data_note(0x10, 1, 7, 120, 392, 1000000)
# s.write(note_data)
# s.read()
