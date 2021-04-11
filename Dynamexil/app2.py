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




#me = singleton.SingleInstance() # will sys.exit(-1) if another instance of this program is already running


app = Flask(__name__)
redis = Redis(host='redis', port=6379)

def motor_move(serial_connection, dynamixel_id):
    serial_connection.goto(dynamixel_id, 0, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second

    # Go to -45° (45° CW)
    serial_connection.goto(dynamixel_id, -45, speed=512, degrees=True)
    time.sleep(1)    # Wait 1 second
def parse_command_line_args():
    token_life = 60 #lifetime of the JWT token (minutes)
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description=(
            'Example Google Cloud IoT Core MQTT device connection code.'))
    parser.add_argument(
            '--project_id',
            default='cobalt-catalyst-263401',
            help='GCP cloud project name')
    parser.add_argument(
            '--registry_id', 
        default='my-registry',
        help='Cloud IoT Core registry id')
    parser.add_argument(
            '--device_id', 
        default='balena',
        help='Cloud IoT Core device id')
    parser.add_argument(
            '--private_key_file',
        default='/root/.ssh/ec_private.pem',
            help='Path to private key file.')
    parser.add_argument(
            '--algorithm',
            choices=('RS256', 'ES256'),
            default='ES256',
            help='Which encryption algorithm to use to generate the JWT.')
    parser.add_argument(
            '--cloud_region', default='us-central1', help='GCP cloud region')
    parser.add_argument(
            '--ca_certs',
            default='/root/.ssh/roots.pem',
            help=('CA root from https://pki.google.com/roots.pem'))
    parser.add_argument(   
            '--mqtt_bridge_hostname',
            default='mqtt.googleapis.com',
            help='MQTT bridge hostname.')
    parser.add_argument(
            '--mqtt_bridge_port',
            choices=(8883, 443),
            default= 443,
            type=int,
            help='MQTT bridge port.')
    parser.add_argument(
            '--jwt_expires_minutes',
            default=token_life,
            type=int,
            help=('Expiration time, in minutes, for JWT tokens.'))

    return parser.parse_args()


def create_jwt(cur_time, projectID, privateKeyFilepath, algorithmType):
  token_life = 60 #lifetime of the JWT token (minutes)
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=token_life),
      'aud': projectID
  }

  with open(privateKeyFilepath, 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, algorithm=algorithmType) # Assuming RSA, but also supports ECC

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    print('on_publish')

def on_message(unused_client, unused_userdata, message):
    payload = str(message.payload)
    print('Received message \'{}\' on topic \'{}\''.format(payload, message.topic))
   

def createJSON(id, unique_id, timestamp, _data):
    data = {
    'ID' : unique_id,
    'timestamp' : timestamp,
    'data1' : _data
    }

    json_str = json.dumps(data)
    return json_str

@app.route('/')
def main():
    args = parse_command_line_args()
    project_id = args.project_id
    gcp_location = args.cloud_region
    registry_id = args.registry_id
    device_id = args.device_id
    ssl_private_key_filepath = args.private_key_file
    ssl_algorithm = args.algorithm
    root_cert_filepath = args.ca_certs
    sensorID = registry_id + "." + device_id
    googleMQTTURL = args.mqtt_bridge_hostname
    googleMQTTPort = args.mqtt_bridge_port


    serial_connection = Connection(port="/dev/ttyUSB0", baudrate=1000000)
    is_available0 = serial_connection.ping(0)
    is_available1 = serial_connection.ping(1)
    motor_move(serial_connection, 1)
    motor_move(serial_connection, 0)
    serial_connection.close()
    print("motor 0 : {}, motor 1: {}".format(is_available0, is_available1))

    
    _CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
    _MQTT_TOPIC = '/devices/{}/events'.format(device_id)
    _MQTT_CONFIG_TOPIC = '/devices/{}/config'.format(device_id)
    _MQTT_COMMANDS_TOPIC = '/devices/{}/commands/#'.format(device_id)
    token_life = 60 #lifetime of the JWT token (minutes)
    while True:

      client = mqtt.Client(client_id=_CLIENT_ID)
      cur_time = datetime.datetime.utcnow()
      # authorization is handled purely with JWT, no user/pass, so username can be whatever
      client.username_pw_set(
          username='unused',
          password=create_jwt(cur_time, project_id, ssl_private_key_filepath, ssl_algorithm))

      client.on_connect = on_connect
      client.on_publish = on_publish
      client.on_message = on_message

      client.tls_set(ca_certs=root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
      client.connect(googleMQTTURL, googleMQTTPort)
      client.subscribe(_MQTT_CONFIG_TOPIC, qos=1)
      client.subscribe(_MQTT_COMMANDS_TOPIC, qos=1)
      jwt_refresh = time.time() + ((token_life - 1) * 60) #set a refresh time for one minute before the JWT expires

      client.loop_start()

      last_checked = 0
      while time.time() < jwt_refresh:
          currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
          uniqueID = str(uuid.uuid4()) + "-" + sensorID
          payload = createJSON(sensorID, uniqueID, currentTime, 0.0)
          client.publish(_MQTT_TOPIC, payload, qos=1)
          print("{}\n".format(payload))
          time.sleep(1)
               
      client.loop_stop()

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
    
