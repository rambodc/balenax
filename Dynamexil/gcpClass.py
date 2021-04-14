from __future__ import print_function
from flask import  Flask, jsonify, request, redirect,render_template, Response
from redis import Redis
import time
import requests
import argparse
import time
import datetime
import uuid
import json
import jwt
from tendo import singleton
import paho.mqtt.client as mqtt
from serial.tools import list_ports
import serial
import re
import os
import io
import threading

class gcp(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.token_life = 60
        self.project_id = 'cobalt-catalyst-263401'
        self.registry_id = 'my-registry'
        self.device_id = 'balena'
        self.private_key_file = '/root/.ssh/ec_private.pem'
        self.algorithm = 'ES256'
        self.cloud_region = 'us-central1'
        self.ca_certs = '/root/.ssh/roots.pem'
        self.mqtt_bridge_hostname = 'mqtt.googleapis.com'
        self.mqtt_bridge_port = 443
        self.jwt_expires_minutes = self.token_life
        self.running = True
        self.daemon = True
        self.start()
        pass

    def stop(self):
        self.join()
        self.running = False

    def create_jwt(self, cur_time, projectID, privateKeyFilepath, algorithmType):
        token = {
            'iat': cur_time,
            'exp': cur_time + datetime.timedelta(minutes= self.token_life),
            'aud': projectID
        }
        with open(privateKeyFilepath, 'r') as f:
            private_key = f.read()
        return jwt.encode(token, private_key, algorithm=algorithmType)  # Assuming RSA, but also supports ECC
        pass

    def error_str(self, rc):
        return '{}: {}'.format(rc, mqtt.error_string(rc))

    def on_connect(self, unusued_client, unused_userdata, unused_flags, rc):
        print('on_connect', self.error_str(rc))

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        print('on_publish')

    def on_message(self, unused_client, unused_userdata, message):
        payload = str(message.payload)
        print('Received message \'{}\' on topic \'{}\''.format(payload, message.topic))

    def createJSON(self, id, unique_id, timestamp, _data):
        data = {
            'ID': unique_id,
            'timestamp': timestamp,
            'data1': _data
        }

        json_str = json.dumps(data)
        return json_str

    def run(self):
        project_id = self.project_id
        gcp_location = self.cloud_region
        registry_id = self.registry_id
        device_id = self.device_id
        ssl_private_key_filepath = self.private_key_file
        ssl_algorithm = self.algorithm
        root_cert_filepath = self.ca_certs
        sensorID = registry_id + "." + device_id
        googleMQTTURL = self.mqtt_bridge_hostname
        googleMQTTPort = self.mqtt_bridge_port
        _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id,
                                                                                device_id)
        _MQTT_TOPIC = '/devices/{}/events'.format(device_id)
        _MQTT_CONFIG_TOPIC = '/devices/{}/config'.format(device_id)
        _MQTT_COMMANDS_TOPIC = '/devices/{}/commands/#'.format(device_id)
        while self.running:
            client = mqtt.Client(client_id=_CLIENT_ID)
            cur_time = datetime.datetime.utcnow()
            # authorization is handled purely with JWT, no user/pass, so username can be whatever
            client.username_pw_set(
                username='unused',
                password=self.create_jwt(cur_time, project_id, ssl_private_key_filepath, ssl_algorithm))

            client.on_connect = self.on_connect
            client.on_publish = self.on_publish
            client.on_message = self.on_message

            client.tls_set(
                ca_certs=root_cert_filepath)  # Replace this with 3rd party cert if that was used when creating registry
            client.connect(googleMQTTURL, googleMQTTPort)
            client.subscribe(_MQTT_CONFIG_TOPIC, qos=1)
            client.subscribe(_MQTT_COMMANDS_TOPIC, qos=1)
            jwt_refresh = time.time() + (
                        (self.token_life - 1) * 60)  # set a refresh time for one minute before the JWT expires

            client.loop_start()

            last_checked = 0
            while time.time() < jwt_refresh:
                currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                uniqueID = str(uuid.uuid4()) + "-" + sensorID
                payload = self.createJSON(sensorID, uniqueID, currentTime, 0.0)
                client.publish(_MQTT_TOPIC, payload, qos=1)
                print("{}\n".format(payload))
                time.sleep(1)

            client.loop_stop()
