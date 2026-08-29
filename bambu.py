#!/usr/bin/env python3
import os, sys, re, datetime, time
import argparse
import sqlite3
from inspect import currentframe, getframeinfo
parser = argparse.ArgumentParser()
parser.add_argument("printer",choices=("Guster","Lefty","Poncho"))
parser.add_argument("--slack", "-s", action="store_true")
parser.add_argument("--debug", "-d", action="store_true")
parser.add_argument("--update", "-u", action="store_true")
args = parser.parse_args()
import time
import bambulabs_api as bl
import shelve
from slack import Slack
import tomllib

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)

shelf = shelve.open(f"{args.printer}.state", writeback=True)

if __name__ == "__main__":
    print("Starting bambulabs_api example")
    print("Connecting to Bambulabs 3D printer")
    print(f"IP: {config[args.printer]['IP']}")
    print(f"Serial: {config[args.printer]['SERIAL']}")
    print(f"Access Code: {config[args.printer]['ACCESS_CODE']}")
    print("LINE:",getframeinfo(currentframe()).lineno)

    # Create a new instance of the API
    printer = bl.Printer(config[args.printer]['IP'], config[args.printer]['ACCESS_CODE'], config[args.printer]['SERIAL'])
    print("LINE:",getframeinfo(currentframe()).lineno)
    print(printer)
    print(printer.__dict__)
    print(dir(printer))

    # Connect to the Bambulabs 3D printer
    conn_stat = printer.mqtt_start()
    print("LINE:",getframeinfo(currentframe()).lineno, conn_stat)
    time.sleep(5)
    status = printer.get_state().strip()
    print("LINE:",getframeinfo(currentframe()).lineno, status)

    state_changed = False
    print("LINE:",getframeinfo(currentframe()).lineno)
    now = datetime.datetime.now().timestamp()
    print("LINE:",getframeinfo(currentframe()).lineno)
    now_hour = datetime.datetime.now().strftime("%H")
    print("LINE:",getframeinfo(currentframe()).lineno)

    if status == "UNKNOWN":
        shelf['status'] = status
        shelf['subtask'] = None
    else:
        try:
            time.sleep(5)

            # Get the printer status
            print("LINE:",getframeinfo(currentframe()).lineno)
            status = printer.get_state()
            print(getframeinfo(currentframe()).lineno,status)
            if 'status' not in shelf:
                shelf['status'] = "UNKNOWN"
            print("LINE:",getframeinfo(currentframe()).lineno)
            print(shelf['status'])
            if 'time' in shelf:
                last_hour = datetime.datetime.fromtimestamp(float(shelf['time'])).strftime("%H")
            else:
                shelf['time'] = 0
                last_hour = now_hour
            print(last_hour,now_hour)
            if status != shelf['status']:
                state_changed = True
            elif 'time' in shelf and (now-float(shelf['time'])) >= 3560:
                state_changed = True
            elif args.update:
                state_changed = True
            shelf['status'] = status
            print("LINE:",getframeinfo(currentframe()).lineno)
            shelf['percentage'] = printer.get_percentage()
            print("LINE:",getframeinfo(currentframe()).lineno)
            shelf['layer_num'] = printer.current_layer_num()
            print("LINE:",getframeinfo(currentframe()).lineno)
            shelf['total_layer_num'] = printer.total_layer_num()
            print("LINE:",getframeinfo(currentframe()).lineno)
            shelf['bed_temperature'] = printer.get_bed_temperature()
            shelf['nozzle_temperature'] = printer.get_nozzle_temperature()
            print("LINE:",getframeinfo(currentframe()).lineno)
            shelf['remaining_time'] = printer.get_time()
            shelf['subtask'] = printer.subtask_name()
            print("LINE:",getframeinfo(currentframe()).lineno)
            if shelf['remaining_time']:
                finish_time = datetime.datetime.now() + datetime.timedelta(
                    minutes=int(shelf['remaining_time']))
                finish_time_format = finish_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                finish_time_format = "NA"

            print(
                f'''Printer status: {shelf['status']}
                Layers: {shelf['layer_num']}/{shelf['total_layer_num']}
                percentage: {shelf['percentage']}%
                Bed temp: {shelf['bed_temperature']} ºC
                Nozzle temp: {shelf['nozzle_temperature']} ºC
                Remaining time: {shelf['remaining_time']}m
                Subtask name: {shelf['subtask']}
                Finish time: {finish_time_format}
                '''
            )
            if 'ts' in shelf: print(shelf['ts'])

            if args.debug:
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
        except Exception as err:
            print(repr(err))
            print(traceback.print_exc())
        finally:
            # Disconnect from the Bambulabs 3D printer
            printer.disconnect()
    printer.disconnect()

try:
    remaining = datetime.timedelta(minutes=int(shelf['remaining_time']))
except:
    remaining = 0
    shelf['remaining_time'] = remaining
print(shelf['remaining_time'])
print(remaining)
if int(shelf['remaining_time']):
    if shelf['status'] == "RUNNING":
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
    if 'channel_id' not in shelf:
        shelf['channel_id'] = slack.get_channel_id('3d-printer-status')
    channel_id = shelf['channel_id']
    if 'ts' in shelf and shelf['ts'] and False:
        response = slack.update(shelf['ts'],channel_id,msg) or slack.postMessage(channel_id,msg)
    else:
        response = slack.postMessage(channel_id,msg)
        if response and 'ts' in response: shelf['ts'] = response['ts']
    shelf['time'] = float(now)
    print(response)

if shelf['status'] in [ "FINISH","FAILED","IDLE","PAUSE", "UNKNOWN" ]:
    shelf['time'] = float(now)
if 'ts' not in shelf: shelf['ts'] = 0
print("TS",shelf['ts'], datetime.datetime.fromtimestamp(float(shelf['ts'])))
print("TIME",shelf['time'],datetime.datetime.fromtimestamp(float(shelf['time'])))
print(now-float(shelf['ts']))

shelf.close()
