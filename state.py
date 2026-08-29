#!/usr/bin/env python3
import os, sys, re, datetime, time, glob
import argparse
import sqlite3
from inspect import currentframe, getframeinfo
parser = argparse.ArgumentParser()
parser.add_argument("--debug", "-d", action="store_true")
args = parser.parse_args()
import time
import bambulabs_api as bl
import shelve
from slack import Slack
import tomllib

files = glob.glob("*.state")

for file in sorted(files):
    print(file)
    shelf = shelve.open(file, 'r')
    for key in sorted(shelf):
        print(f"\t{key}: {shelf[key]}")

