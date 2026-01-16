#!/usr/bin/env python3
# Copyright © 2026 Kinara Systems Inc.
# -*- coding: UTF-8 -*-
"""
MQTT Sender
Usage: cat logfile | python3 send-mqtt.py
"""
import os
import io
import sys
import random
import json
import argparse
from dotenv import load_dotenv
import paho.mqtt.client as mqtt

import mqtt.apmsg_pb2 as apmsg

load_dotenv()

MSG_VERSION = 1
DEFAULT_PORT = 1883
DEFAULT_HOST = 'localhost'
DEFAULT_TOPIC = 'ucentral'
DEFAULT_USER = 'test'
DEFAULT_PASS = ''
HOST = os.getenv('MQTT_HOST', DEFAULT_HOST)
PORT = int(os.getenv('MQTT_PORT', str(DEFAULT_PORT)))
TOPIC = os.getenv('MQTT_TOPIC', DEFAULT_TOPIC)
USER = os.getenv('MQTT_USER', DEFAULT_USER)
PASS = os.getenv('MQTT_PASS', DEFAULT_PASS)
CLIENT_ID = f"ucentralmqtt-pub-{random.randint(0, 1000)}"

def main() -> int:
    '''Main program'''
    def on_connect(client, obj, flags, reason_code, properties):
        if verbose:
            print(f"onconnect: Session present: {flags.session_present}")
        if reason_code.is_failure:
            print(f"Failed to connect: {reason_code}")

    def on_disconnect(client, obj, flags, rc, properties):
        if verbose:
            print(f"ondisconnect: flags {flags}")
            print(f"Disconnect rc={rc}")
        else:
            print("Disconnected")

    def packmsg(msg):
        try:
            d = json.loads(msg)
        except Exception:
            print(f"Error: Can't parse JSON line: {msg}")
            return None
        json_msg = json.dumps(d['msg'])
        ucmsg = apmsg.UCentralMsg()
        ucmsg.version = MSG_VERSION
        ucmsg.timestamp = d['timestamp']
        ucmsg.topic = d['topic']
        ucmsg.serial = d['serial']
        ucmsg.msg = json_msg
        print(f"Sending message: topic: {d['topic']}, serial: {d['serial']}, " + \
              f"timestamp: {d['timestamp']}")
        if verbose:
            print(f"  Message: {json_msg}")
        return ucmsg.SerializeToString()

    def send_mqtt(buf) -> int:
        """Send the current message to MQTT broker"""
        msg = packmsg(buf)
        if msg:
            if not dry_run:
                result = client.publish(topic, msg, qos=0, retain=False)
                status = result[0]
                if status != mqtt.MQTT_ERR_SUCCESS:
                    print(f"Failed to send message: {status}:{mqtt.error_string(status)}")
                    return -1
        else:
            return 0
        return 1

    prs = argparse.ArgumentParser(description='Send MQTT messages from JSONL',
                                  formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    prs.add_argument('-d', '--dryrun', action='store_true', default=False,
                     help='Don\'t send to MQTT')
    prs.add_argument('-H', '--host', type=str, default=DEFAULT_HOST,
                     help='Host to send to')
    prs.add_argument('-p', '--password', type=str, default=DEFAULT_PASS,
                     help='Password')
    prs.add_argument('-P', '--port', type=str, default=DEFAULT_PORT,
                     help='Port to send on')
    prs.add_argument('-t', '--topic', type=str, default=DEFAULT_TOPIC,
                     help='Topic on which to send to')
    prs.add_argument('-u', '--user', type=str, default=DEFAULT_USER,
                     help='User name')
    prs.add_argument('-v', '--verbose', action='store_true', default=False,
                     help='Verbose tracing')
    args = prs.parse_args()

    broker = args.host
    port = args.port
    topic = args.topic
    dry_run = args.dryrun
    verbose = args.verbose

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2,
                         client_id=CLIENT_ID,
                         clean_session=True)
    client.username_pw_set(args.user, args.password)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    print(f"Connect to {broker}:{port} as {args.user} using topic {topic}")
    try:
        client.connect(broker, port, 60)
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        return 1

    cnt = 0
    # read JSONL file
    with io.open(sys.stdin.fileno(), 'rb', buffering=0, closefd=False) as stdin:
        for line_bytes in stdin:
            line = line_bytes.decode('utf-8')
            rc = send_mqtt(line)
            if rc < 0:
                break
            cnt += 1

    client.loop_stop()
    client.disconnect()
    if cnt != 1:
        print(f"Sent {cnt} messages")
    else:
        print(f"Sent 1 message")
    return 0


if __name__ == '__main__':
    sys.exit(main())
