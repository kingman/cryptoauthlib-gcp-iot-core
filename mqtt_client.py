#!/usr/bin/env python

# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import paho.mqtt.client as mqtt
import ssl
import time
import json
import JWT_generator

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_disconnect(unused_client, unused_userdata, rc):
    print('on_disconnect', error_str(rc))

class MQTTClient(object):
    mqtt_bridge_hostname = 'mqtt.googleapis.com'
    mqtt_bridge_port = 8883
    connected = False

    def __init__(self, project_id, registry_id, device_id, cloud_region, ca_certs):
        self.client = mqtt.Client(
            client_id=('projects/{}/locations/{}/registries/{}/devices/{}'
                   .format(
                           project_id,
                           cloud_region,
                           registry_id,
                           device_id)))
        self.client.username_pw_set(
            username='unused',
            password=JWT_generator.generate_token(project_id))
        self.client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.on_disconnect = on_disconnect

    def attach_device(self, device_id, device_jwt=None):
        attach_topic = '/devices/{}/attach'.format(device_id)
        attach_payload = {}
        if device_jwt:
            attach_payload['authorization'] = device_jwt
        self.client.loop(.1)
        self.client.publish(attach_topic, json.dumps(attach_payload), qos=1)

    def connect_to_server(self):
        self.client.connect(self.mqtt_bridge_hostname, self.mqtt_bridge_port)
        self.connected = True

    def disconnect_from_server(self):
        self.client.disconnect()
        self.connected = False

    def _send(self, topic, msg):
        self.client.loop(.1)
        msgInfo = self.client.publish(topic, msg, qos=1)

    def send_event(self, device_id, msg, sub_topic=None):
        topic = '/devices/{}/events'.format(device_id)
        if sub_topic:
            topic = '{}/{}'.format(topic, sub_topic)
        self._send(topic, msg)

    def send_state(self, device_id, msg):
        topic = '/devices/{}/state'.format(device_id)
        self._send(topic, msg)
