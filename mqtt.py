#!/usr/bin/env python3

import os, sys, re, datetime, time


import time
import paho.mqtt.client as paho
import json
import hashlib
import pprint
import argparse
import tomllib
import copy

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)

parser = argparse.ArgumentParser()
parser.add_argument("printer", choices=['Lefty', 'Poncho', 'Guster'])
args = parser.parse_args()

def debug(*args):
    print(args, file=sys.stderr)

def ts():
    return datetime.datetime.now().timestamp()
last_ts = 0
print("Start")

oauth_token = config['Slack']['oauth_token']




items = [
  'gcode_state','layer_num','total_layer_num','task_id','subtask_name','fail_reason','mc_remaining_time',
  'bed_temper',
  'bed_target_temper',
  'chamber_target_temper',
  'chamber_temper',
  'nozzle_target_temper',
  'nozzle_temper',
  'mc_print_stage',
  'command',
]

#define callbacks
def on_message(client, userdata, message):
  global last_ts
  now = ts()
  ##if now-last_ts < 10: return
  debug(datetime.datetime.now())
  last_ts = ts()
  try:
    pprint.pprint(message.payload.decode(), stream=sys.stderr)
  except:
    pass
  data = json.loads(message.payload)
  #print(f"MESSAGE: {str(datetime.datetime.now())}")
  try:
    #if data['print']['mc_remaining_time'] == client.remaining:
    #  return
    traystate = {}
    currentstate = {
        'gcode_state': data['print']['gcode_state'],
        'task_id': data['print']['task_id'],
        'subtask_name': data['print']['subtask_name'],
    }
    #if currentstate == client.laststate:
    #  return
    client.remaining = data['print']['mc_remaining_time']
    for datum in data:
       debug(datum)
       try: tray_now = data['print']['ams']['tray_now']
       except: tray_now = None
       debug("Tray Now:",tray_now)
       traystate['tray_now'] = tray_now
       traystate['trays'] = []
       for tray in data['print']['ams']['ams'][0]['tray']:
           sys.stderr.write("Tray: ")
           tray_str = ""
           if tray_now == tray['id']: sys.stderr.write('*')
           for key in ['id', 'tray_id_name', 'tray_info_idx','tray_type', 'tray_sub_brands', 'tray_color', 'nozzle_temp_min','nozzle_temp_max']:
               if key in tray:
                   sys.stderr.write(f"{tray[key]} ")
                   tray_str += f"{tray[key]} "
               else:
                   sys.stderr.write("None ")
                   tray_str += "None "
           sys.stderr.write('\n')
           sys.stdout.flush()
           traystate['trays'].append(
               tray_str.strip()
           )
       traystate['trays'].append(
           f"{data['print']['vt_tray']['id']} {data['print']['vt_tray']['tray_type']} {data['print']['vt_tray']['tray_color']} {data['print']['vt_tray']['nozzle_temp_min']} {data['print']['vt_tray']['nozzle_temp_max']}"
       )
       print(f"Tray: {data['print']['vt_tray']['id']} {data['print']['vt_tray']['tray_type']} {data['print']['vt_tray']['tray_color']} {data['print']['vt_tray']['nozzle_temp_min']} {data['print']['vt_tray']['nozzle_temp_max']}", file=sys.stderr)
       for x in data[datum]:
           if x in items:
             debug(f'\t{x}:\t{data[datum][x]}')
       pprint.pprint(traystate,stream=sys.stderr)
       pprint.pprint(currentstate,stream=sys.stderr)
       if not client.traystate or not client.state:
           client.traystate = copy.deepcopy(traystate)
           client.state = copy.deepcopy(currentstate)
       ht = hashlib.sha256(json.dumps(traystate,sort_keys=True).encode('utf-8')).hexdigest()
       hc = hashlib.sha256(json.dumps(currentstate,sort_keys=True).encode('utf-8')).hexdigest()
       lht = hashlib.sha256(json.dumps(client.traystate,sort_keys=True).encode('utf-8')).hexdigest()
       lhc = hashlib.sha256(json.dumps(client.state,sort_keys=True).encode('utf-8')).hexdigest()
       debug(ht)
       debug(lht)
       if ht != lht or client.initial:
           print("Filament changed:", datetime.datetime.now())
           pprint.pprint(traystate)
           client.traystate = copy.deepcopy(traystate)
       debug(hc)
       debug(lhc)
       if hc != lhc or client.initial:
           print("Print state changed",  datetime.datetime.now())
           pprint.pprint(currentstate)
           client.state = copy.deepcopy(currentstate)
    client.initial = False
  except Exception as e:
    debug("ERROR",e)
    debug(data)
    return



def on_log(client, userdata, level, buf):
  debug("log: ",userdata, level, buf)


def on_subscribe(client, userdata, mid, reason_code_list, properties):
    # Since we subscribed only for a single channel, reason_code_list contains
    # a single entry
    if reason_code_list[0].is_failure:
        print(f"sub: Broker rejected you subscription: {reason_code_list[0]}")
    else:
        print(f"sub: Broker granted the following QoS: {reason_code_list[0].value}")

def on_connect(client, userdata, flags, reason_code, properties):
  print("connected?")
  print(client, userdata, flags, reason_code, properties)


client=paho.Client(paho.CallbackAPIVersion.VERSION2) 
client.on_message=on_message
#client.on_log=on_log
client.on_connect=on_connect
client.on_subscribe=on_subscribe
client.remaining = -99
client.laststate = None
client.traystate = None
client.initial = True
client.username_pw_set("bblp",config[args.printer]['ACCESS_CODE'])
print("connecting to broker")
port = int(config[args.printer]['PORT'])
print(port)
client.connect("127.0.0.1", port, 60)
client.subscribe((f"device/{config[args.printer]['SERIAL']}/report",1),(f"device/{config[args.printer]['SERIAL']}/requests",1))

##start loop to process received messages
client.loop_forever()
time.sleep(1)

