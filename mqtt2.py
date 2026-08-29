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

def diff(str1,str2):
    len1 = len(str1)
    len2 = len(str2)
    for i in range(min(len1,len2)):
        if str1[i] != str2[i]:
            return i
    if len1 == len2:
        return -1
    return i

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)

parser = argparse.ArgumentParser()
parser.add_argument("printer", choices=['Lefty', 'Poncho'])
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

last_hash = ''

#define callbacks
def on_message(client, userdata, message):
    global last_hash
    ht = hashlib.sha256(message.payload).hexdigest()
    if last_hash != '':
        x = diff(last_hash, message.payload)
        print(x)
        if x >= 0:
            print(len(last_hash),len(message.payload))
            print("<",last_hash[x:x+20])
            if len(last_hash) < 300: print(last_hash)
            print(">",message.payload[x:x+20])
    last_hash = message.payload
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
print(PORT[args.printer])
client.connect("127.0.0.1", PORT[args.printer], 60)
client.subscribe((f"device/{config[args.printer]['SERIAL']}/report",1),(f"device/{config[args.printer]['SERIAL']}/requests",1))

##start loop to process received messages
client.loop_forever()
time.sleep(1)

