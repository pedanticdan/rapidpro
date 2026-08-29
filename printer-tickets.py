#!/usr/bin/env python3
import os, sys, re, datetime, time
import argparse
import sqlite3
import json
from inspect import currentframe, getframeinfo
parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", action="store_true")
args = parser.parse_args()
import time
import bambulabs_api as bl
import shelve
from slack import Slack
import tomllib

bambus = []

with open("/home/rapidpro/.config/bambu.toml", "rb") as f:
    config = tomllib.load(f)
for x in config:
    if "BAMBU" in config[x]:
        bambus.append(x)

shelf = shelve.open("printer-tickets.state", writeback=True)

if __name__ == "__main__":

    now = int(datetime.datetime.now().timestamp()+0.5)
    since = now - 7200
    if args.debug:
        print(now)
        print(since)
    slack = Slack()
    slack.connect(token=config['Slack']['oauth_token'])
    if 'channel_id' not in shelf:
        if args.debug: print("lookup channel_id")
        shelf['channel_id'] = slack.get_channel_id('printer-tickets')
    channel_id = shelf['channel_id']
    if args.debug: print(channel_id)
    history = slack.conversations_history(channel_id,since)
    if args.debug: print(history)
    if history['ok']:
        for message in history['messages']:
            if 'user' in message:
                user = message['user']
                if args.debug: print(f"user: {user}")
            if 'client_msg_id' in message:
                msg_id = message['client_msg_id']
                if args.debug: print(f"client_msg_id: {msg_id}")
            if 'text' in message:
                text = message['text']
                if args.debug: print(f"text: {text}")
                for bambu in bambus:
                    if bambu in text:
                        print(f"text mentions {bambu}")

    shelf.close()
