#!/usr/bin/env python3
import os, sys, re, datetime, time, fcntl
import argparse
import sqlite3
from inspect import currentframe, getframeinfo
from subprocess import Popen, DEVNULL
parser = argparse.ArgumentParser()
parser.add_argument("printer",choices=("Guster","Lefty","Poncho"))
parser.add_argument("--debug", "-d", action="store_true")
args = parser.parse_args()
import time
import bambulabs_api as bl
import tomllib

print(args)

def lock_file():
    global lock_file_handle
    # Open or create a hidden lock file
    lock_file_handle = open('/home/rapidpro/data-out/stream.lock', 'w')
    try:
        # Request an exclusive, non-blocking lock from the OS
        fcntl.lockf(lock_file_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except IOError:
        print("Another instance is holding the file lock. Exiting.")
        sys.exit(0)

lock_file()


shelf = {}

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)

if __name__ == "__main__":
    print("Starting bambulabs_api example")
    print("Connecting to Bambulabs 3D printer")
    print(f"IP: {config[args.printer]['IP']}")
    print(f"Serial: {config[args.printer]['SERIAL']}")
    print(f"Access Code: {config[args.printer]['ACCESS_CODE']}")
    print("LINE:",getframeinfo(currentframe()).lineno)

    # Create a new instance of the API
    printer = bl.Printer(config[args.printer]['IP'], config[args.printer]['ACCESS_CODE'], config[args.printer]['SERIAL'])

    # Connect to the Bambulabs 3D printer
    conn_stat = printer.mqtt_start()
    print("LINE:",getframeinfo(currentframe()).lineno, conn_stat)
    time.sleep(5)
    status = printer.get_state().strip()

    now = datetime.datetime.now().timestamp()

    print(status) 

    printer.disconnect()

    ffmpeg = f'''/usr/bin/ffmpeg -i rtsps://bblp:{config[args.printer]['ACCESS_CODE']}@{config[args.printer]['IP']}:322/streaming/live/1 \
    -f lavfi -i anullsrc -c:a aac -b:a 128k \
    -c:v copy -f flv rtmp://live.restream.io/live/{config[args.printer]['KEY']}'''
    p = Popen(ffmpeg.split(), stdout=DEVNULL, stderr=DEVNULL)
    p.wait()
    sys.exit(p.returncode)

