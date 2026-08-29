#!/usr/bin/env python3
import os, sys, re, datetime, time
import argparse
import sqlite3
parser = argparse.ArgumentParser()
parser.add_argument("printer",choices=("Prusa",))
parser.add_argument("--slack", "-s", action="store_true")
parser.add_argument("--update", "-u", action="store_true")
args = parser.parse_args()
import time
import PrusaLinkPy

import shelve
from slack import Slack
import requests
import tomllib

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)



shelf = shelve.open(f"{args.printer}.state", writeback=True)

debug = os.getenv("debug", False)

if __name__ == '__main__':
    print('Connecting to Prusa 3D printer')
    print(f'IP: {IP[args.printer]}')
    print(f'Serial: {SERIAL[args.printer]}')
    print(f'Access Code: {ACCESS_CODE[args.printer]}')

    printer = PrusaLinkPy.PrusaLinkPy(IP[args.printer], ACCESS_CODE[args.printer])

    # Connect to the Bambulabs 3D printer
    p = printer.get_printer()
    data = p.json()
    for key in sorted(data):
        print(f"{key}:")
        for subkey in sorted(data[key]):
            print(f"\t{subkey}: {data[key][subkey]}")
    status = printer.get_status().json()
    for key in sorted(status):
        print(f"{key}:")
        for subkey in sorted(status[key]):
            print(f"\t{subkey}: {status[key][subkey]}")
    job = printer.get_job().json()
    for key in sorted(job):
        print(f"{key}: {job[key]}")
    now = datetime.datetime.now().timestamp()
    print(now)
    print(status['printer']['state'])
    print(status['job']['time_remaining'])
    ts = datetime.timedelta(seconds=int(status['job']['time_remaining']))
    print(ts)

    state_changed = False

    try:
        #while True:
            time.sleep(5)

            # Get the printer status
            print(status)
            if 'status' not in shelf:
                shelf['status'] = "UNKNOWN"
            print(shelf['status'])
            if status['printer']['state'] != shelf['status']:
                state_changed = True
            elif 'time' in shelf and (now-float(shelf['time'])) >= 3600:
                state_changed = True
            elif args.update:
                state_changed = True
            shelf['status'] = status['printer']['state']
            shelf['percentage'] = job['progress']
            shelf['bed_temperature'] = status['printer']['temp_bed']
            shelf['nozzle_temperature'] = status['printer']['temp_nozzle']
            shelf['remaining_time'] = status['job']['time_remaining']
            shelf['subtask'] = job['file']['display_name']
            if shelf['remaining_time']:
                finish_time = datetime.datetime.now() + datetime.timedelta(
                    seconds=int(shelf['remaining_time']))
                finish_time_format = finish_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                finish_time_format = "NA"

            print(
                f'''Printer status: {shelf['status']}
                percentage: {shelf['percentage']}%
                Bed temp: {shelf['bed_temperature']} ºC
                Nozzle temp: {shelf['nozzle_temperature']} ºC
                Remaining time: {shelf['remaining_time']}m
                Subtask name: {shelf['subtask']}
                Finish time: {finish_time_format}
                '''
            )
            if 'ts' in shelf: print(shelf['ts'])

            if debug:
                import json
                print("=" * 100)
                print("Printer MQTT Dump")
                print(json.dumps(
                    printer.mqtt_dump(),
                    sort_keys=True,
                    indent=2
                ))
                print("=" * 100)
            #break
    finally:
        # Disconnect from the Bambulabs 3D printer
        pass

try:
    remaining = datetime.timedelta(seconds=int(shelf['remaining_time']))
except:
    remaining = 0
    shelf['remaining_time'] = remaining
print(shelf['remaining_time'])
print(remaining)
if int(shelf['remaining_time']):
    if shelf['status'] == "PRINTING":
        msg = f"{args.printer} {remaining} remaining\n\t\"{shelf['subtask']}\""
    else:
        msg = f"{args.printer} {shelf['status']} {remaining} remaining\n\t\"{shelf['subtask']}\""
else:
    msg = f"{args.printer} {shelf['status']} \"{shelf['subtask']}\""
print(msg)
if state_changed and args.slack:
    print("Should slack")
    slack = Slack()
    slack.connect(token=config['Slack']['oauth_token'])
    channel_id = slack.get_channel_id('3d-printer-status')
    if 'ts' in shelf and shelf['ts'] and False:
        response = slack.update(shelf['ts'],channel_id,msg) or slack.postMessage(channel_id,msg)
    else:
        response = slack.postMessage(channel_id,msg)
        if response and 'ts' in response: shelf['ts'] = response['ts']
    shelf['time'] = float(now)
    print(response)

if shelf['status'] in [ "FINISH","FAILED","IDLE","PAUSE" ]:
    shelf['time'] = float(now)
if 'ts' not in shelf: shelf['ts'] = 0
print("TS",shelf['ts'], datetime.datetime.fromtimestamp(float(shelf['ts'])))
print("TIME",shelf['time'],datetime.datetime.fromtimestamp(float(shelf['time'])))
print(now-float(shelf['ts']))

shelf.close()
