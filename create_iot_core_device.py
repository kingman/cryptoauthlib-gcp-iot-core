#!/usr/bin/env python

# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Creating device in a existing library using the public key of the secure element
Usage example:
python create_iot_core_device.py --service_account_json '/path/to/service_account' \
--project project_id \
--registry registry_id \
--region region \
--device device_id
"""
import argparse
import base64
from cryptoauthlib import *
from google.oauth2 import service_account
from googleapiclient import discovery
from googleapiclient.errors import HttpError

def _get_client(service_account_json):
    """Returns an authorized API client by discovering the IoT API and creating
    a service object using the service account credentials JSON."""
    api_scopes = ['https://www.googleapis.com/auth/cloud-platform']
    api_version = 'v1'
    discovery_api = 'https://cloudiot.googleapis.com/$discovery/rest'
    service_name = 'cloudiotcore'

    credentials = service_account.Credentials.from_service_account_file(
            service_account_json)
    scoped_credentials = credentials.with_scopes(api_scopes)

    discovery_url = '{}?version={}'.format(
            discovery_api, api_version)

    return discovery.build(
            service_name,
            api_version,
            discoveryServiceUrl=discovery_url,
            credentials=scoped_credentials)

def _create_es256_device(
        service_account_json, project_id, cloud_region, registry_id,
        device_id, public_key):
    """Create a new device with the given id, using ES256 for
    authentication."""
    # [START iot_create_es_device]
    registry_name = 'projects/{}/locations/{}/registries/{}'.format(
            project_id, cloud_region, registry_id)

    client = _get_client(service_account_json)

    # Note: You can have multiple credentials associated with a device.
    device_template = {
        'id': device_id,
        'credentials': [{
            'publicKey': {
                'format': 'ES256_PEM',
                'key': public_key
            }
        }]
    }

    devices = client.projects().locations().registries().devices()
    return devices.create(parent=registry_name, body=device_template).execute()
    # [END iot_create_es_device]

def _get_hardware_publis_key():
    ATCA_SUCCESS = 0x00

    # Loading cryptoauthlib(python specific)
    load_cryptoauthlib()

    cfg = cfg_ateccx08a_i2c_default()

    cfg.cfg.atcai2c.bus = 1

    # Initialize the stack
    assert atcab_init(cfg) == ATCA_SUCCESS

    # Check the device locks
    is_locked = AtcaReference(False)
    assert atcab_is_locked(0, is_locked) == ATCA_SUCCESS
    config_zone_locked = bool(is_locked.value)

    assert atcab_is_locked(1, is_locked) == ATCA_SUCCESS
    data_zone_locked = bool(is_locked.value)

    #Load the public key
    if data_zone_locked:
        public_key = bytearray(64)
        assert atcab_get_pubkey(0, public_key) == ATCA_SUCCESS

        public_key =  bytearray.fromhex('3059301306072A8648CE3D020106082A8648CE3D03010703420004') + bytes(public_key)
        public_key = base64.b64encode(public_key).decode('ascii')
        public_key = ''.join(public_key[i:i+64] + '\n' for i in range(0,len(public_key),64))
        public_key = '-----BEGIN PUBLIC KEY-----\n' + public_key + '-----END PUBLIC KEY-----'
    else:
        raise Exception
    atcab_release()
    return public_key

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GCP arguments')
    parser.add_argument('--service_account_json', help='Credentials to service account with right to create device')
    parser.add_argument('--project', help='GCP project id')
    parser.add_argument('--registry', help='IoT registry id ')
    parser.add_argument('--region', help='Region of the IoT core registry')
    parser.add_argument('--device', help='id of the device to create')
    args = parser.parse_args()
    hardware_public_key = _get_hardware_publis_key()
    _create_es256_device(
            args.service_account_json, args.project, args.region, args.registry,
            args.device, hardware_public_key)
