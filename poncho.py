#!/usr/bin/env python3
import os, sys, re, datetime, time

import time
import bambulabs_api as bl

SERIAL="00M09D520501126"
ACCESS_CODE="30b57c7c"
IP="10.2.160.133"


debug = os.getenv("debug", False)

if __name__ == '__main__':
    print('Starting bambulabs_api example')
    print('Connecting to Bambulabs 3D printer')
    print(f'IP: {IP}')
    print(f'Serial: {SERIAL}')
    print(f'Access Code: {ACCESS_CODE}')

    # Create a new instance of the API
    printer = bl.Printer(IP, ACCESS_CODE, SERIAL)

    # Connect to the Bambulabs 3D printer
    printer.connect()

    try:
        while True:
            time.sleep(5)

            # Get the printer status
            status = printer.get_state()
            percentage = printer.get_percentage()
            layer_num = printer.current_layer_num()
            total_layer_num = printer.total_layer_num()
            bed_temperature = printer.get_bed_temperature()
            nozzle_temperature = printer.get_nozzle_temperature()
            remaining_time = printer.get_time()
            filename = printer.subtask_name()
            if remaining_time is not None:
                finish_time = datetime.datetime.now() + datetime.timedelta(
                    minutes=int(remaining_time))
                finish_time_format = finish_time.strftime("%Y-%m-%d %H:%M:%S")
            else:
                finish_time_format = "NA"

            print(
                f'''Printer status: {status}
                Layers: {layer_num}/{total_layer_num}
                percentage: {percentage}%
                Bed temp: {bed_temperature} ºC
                Nozzle temp: {nozzle_temperature} ºC
                Remaining time: {remaining_time}m
                File name: {filename}
                Finish time: {finish_time_format}
                '''
            )

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
                break
    finally:
        # Disconnect from the Bambulabs 3D printer
        printer.disconnect()
