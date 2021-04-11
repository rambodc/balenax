import argparse
import time
import datetime
import uuid
import json
import jwt
import RPi.GPIO as io
from tendo import singleton
import paho.mqtt.client as mqtt


# Define some project-based variables to be used below. This should be the only
# block of variables that you need to edit in order to run this script

ssl_private_key_filepath = '/home/pi/.ssh/ec_private.pem'
ssl_algorithm = 'ES256' # Either RS256 or ES256
root_cert_filepath = '/home/pi/.ssh/roots.pem'
project_id = 'cobalt-catalyst-263401'
gcp_location = 'us-central1'
registry_id = 'my-registry'
device_id = 'balena'

# end of user-variables

cur_time = datetime.datetime.utcnow()

def create_jwt():
  token = {
      'iat': cur_time,
      'exp': cur_time + datetime.timedelta(minutes=60),
      'aud': project_id
  }

  with open(ssl_private_key_filepath, 'r') as f:
    private_key = f.read()

  return jwt.encode(token, private_key, ssl_algorithm)

_CLIENT_ID = 'projects/{}/locations/{}/registries/{}/devices/{}'.format(project_id, gcp_location, registry_id, device_id)
_MQTT_TOPIC = '/devices/{}/events'.format(device_id)

client = mqtt.Client(client_id=_CLIENT_ID)
# authorization is handled purely with JWT, no user/pass, so username can be whatever
client.username_pw_set(
    username='unused',
    password=create_jwt())

def error_str(rc):
    return '{}: {}'.format(rc, mqtt.error_string(rc))

def on_connect(unusued_client, unused_userdata, unused_flags, rc):
    print('on_connect', error_str(rc))

def on_publish(unused_client, unused_userdata, unused_mid):
    pass
    #print('on_publish')

def createJSON(id, unique_id, timestamp, _data):
    data = {
    'ID' : unique_id,
    'timestamp' : timestamp,
    'data1' : _data
    }

    json_str = json.dumps(data)
    return json_str

client.on_connect = on_connect
client.on_publish = on_publish

client.tls_set(ca_certs=root_cert_filepath) # Replace this with 3rd party cert if that was used when creating registry
client.connect('mqtt.googleapis.com', 8883)
client.loop_start()

# Could set this granularity to whatever we want based on device, monitoring needs, etc
temperature = 0
humidity = 0
pressure = 0

sensorID = 1
for i in range(0, 1000):
    currentTime = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    uniqueID = uuid.uuid4()
    payload = createJSON(sensorID, i, currentTime, 0.0)

    # Uncomment following line when ready to publish
    client.publish(_MQTT_TOPIC, payload, qos=1)

    #print("{}\n".format(payload))
print('job done')
client.loop_stop()
