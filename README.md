# MQTT Sender

This directory contains a tool for sending MQTT messages to an MQTT broker.

## Overview

- Send captured messages from JSONL log files

## Files

- `send-mqtt.py` - Python script that reads log files and sends messages to an MQTT broker
- `logfile.txt` - Sample log file containing captured MQTT messages

## Requirements

- Python 3
- `uv` is installed
- Required Python packages:
  - `paho-mqtt` - MQTT client library
  - `python-dotenv` - Environment variable management
  - `protobuf` - Protobuf library
  - Protocol buffer definitions from `mqtt.apmsg_pb2`

## Protobuf to Python generation

Run `protoc -I=. --python_out=mqtt apmsg.proto` to (re)generate the python stubs for protobuf.
This requires the `protobuf` package to be installed.

## Configuration

Set the following environment variables (or use command-line arguments):

- `MQTT_HOST` - MQTT broker hostname (default: localhost)
- `MQTT_PORT` - MQTT broker port (default: 1883)
- `MQTT_TOPIC` - Topic to publish to (default: ucentral)
- `MQTT_USER` - MQTT username (default: test)
- `MQTT_PASS` - MQTT password (default: "")

If an .env file is present with these variables set, then these variables will be loaded from it.

## Setup

1. Initialize the uv environment using `uv sync` and make sure you're in the virtual environment.
2. For subsequent uses run `source .venv/bin/activate`.

## Usage

### Basic Usage

Send messages from a log file to an MQTT broker:

```bash
cat logfile.txt | python3 send-mqtt.py -H mqtt-broker-host -u username -p password
```

### Advanced Options

```bash
python3 send-mqtt.py [OPTIONS]
```

**Options:**

- `-H, --host HOST` - MQTT broker hostname
- `-P, --port PORT` - MQTT broker port (default: 1883)
- `-u, --user USER` - MQTT username
- `-p, --password PASS` - MQTT password
- `-t, --topic TOPIC` - MQTT topic to publish to
- `-d, --dryrun` - Parse messages without sending to MQTT broker
- `-v, --verbose` - Verbose output

### Input Format

The script supports JSONL input format, with one JSON object per line.

### Examples

**Scale test with simulated clients:**
```bash
cat logfile.txt | python3 send-mqtt.py -H broker 
```
This sends all the messages in logfile.txt.

**Dry run to test parsing:**
```bash
cat logfile.txt | python3 send-mqtt.py -d
```

## How It Works

1. The script reads messages from stdin (in JSONL format)
2. The message is serialized into protobuf format (UCentralMsg)
3. The message is published to the MQTT broker

## Notes

- Default port is 1883 for MQTT broker connections
- Messages are published with QoS 0 (no acknowledgment)
- The timestamps in the messages is not changed.

## Copyright

Copyright © 2026 Kinara Systems Inc.
