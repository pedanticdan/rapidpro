#!/usr/bin/python3

import os, sys,  re, datetime, time
import json
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", action="store_true")
parser.add_argument("--slack", "-s", action="store_true")
parser.add_argument("--update", "-u", action="store_true")
args = parser.parse_args()

import requests
import pprint
import tomllib

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)

print(config['Big60'])

r = requests.get("http://10.2.156.242/rr_model?flags=d99fno")

data = json.loads(r.content.decode())

if args.debug:
    pprint.pprint(data)

x = datetime.timedelta(seconds=data['result']['job']['timesLeft']['filament'])
print("Filament:",x)
x = datetime.timedelta(seconds=data['result']['job']['timesLeft']['file'])
print("File:",x)
x = datetime.timedelta(seconds=data['result']['job']['timesLeft']['slicer'])
print("Slicer:",x)
