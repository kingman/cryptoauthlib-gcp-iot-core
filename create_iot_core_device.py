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
--region region
"""
import argparse
import sys
from google.oauth2 import service_account
from googleapiclient import discovery

from coral.cloudiot.ecc608 import ecc608_i2c_address
from coral.cloudiot.ecc608 import ecc608_serial
from coral.cloudiot.ecc608 import ecc608_public_key

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
        device_info):
    """Create a new device with the given id, using ES256 for
    authentication."""
    # [START iot_create_es_device]
    registry_name = 'projects/{}/locations/{}/registries/{}'.format(
            project_id, cloud_region, registry_id)

    client = _get_client(service_account_json)

    # Note: You can have multiple credentials associated with a device.
    device_template = {
        'id': device_info['device_id'],
        'credentials': [{
            'publicKey': {
                'format': 'ES256_PEM',
                'key': device_info['pub_key']
            }
        }]
    }

    devices = client.projects().locations().registries().devices()
    return devices.create(parent=registry_name, body=device_template).execute()

def _get_device_info():
    if ecc608_i2c_address is None:
        return None
    else:
        device_info = {}
        device_info['device_id'] = 'enviro-{}'.format(ecc608_serial())
        device_info['pub_key'] = ecc608_public_key()
        return device_info

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='GCP arguments')
    parser.add_argument('--service_account_json', help='Credentials to service account with right to create device')
    parser.add_argument('--project', help='GCP project id')
    parser.add_argument('--registry', help='IoT registry id ')
    parser.add_argument('--region', help='Region of the IoT core registry')
    args = parser.parse_args()
    device_info = _get_device_info()
    if not device_info:
        print("Board not found")
        sys.exit(1)
    _create_es256_device(
            args.service_account_json, args.project, args.region, args.registry, device_info)

