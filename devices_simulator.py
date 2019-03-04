import argparse
import os
import json
from mqtt_client import MQTTClient

def main():
    parser = argparse.ArgumentParser(description='GCP arguments')
    parser.add_argument('--project', help='GCP project id')
    parser.add_argument('--registry', help='IoT registry id ')
    parser.add_argument('--region', help='Region of the IoT core registry')
    parser.add_argument('--device', help='id of the device to create')
    parser.add_argument('--cacerts', help='path to root certs')
    args = parser.parse_args()

    client = MQTTClient(
        args.project, args.registry, args.device, args.region, args.cacerts)
    client.connect_to_server()

    payload = {}
    payload['connected'] = True
    payload['device'] = args.device

    client.send_event(args.device, json.dumps(payload))

    client.disconnect_from_server()

if __name__=="__main__":
    main()
