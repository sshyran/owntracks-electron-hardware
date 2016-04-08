#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as paho   # pip install paho-mqtt
import requests
import json
import ssl
import ConfigParser
import time
import logging
import socket
import sys
import os

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2016 Jan-Piet Mens'
__license__   = """GPL2"""

def get_cloud(mqttc, token, device_id):

    payload = None
    params = {
        'access_token' : token,
    }

    r = requests.get('https://api.particle.io/v1/devices/%s/status' % device_id,
        params=params)

    if r.status_code != 200:
        print r.status_code
        print r.text
        mqttc.publish(topic + '/warn', "status=%s" % r.status_code, qos=2, retain=False)
        return None

    print r.text

    try:
        data = json.loads(r.content);
    except:
        mqttc.publish(topic + '/warn', "cannot parse JSON" % r.status_code, qos=2, retain=False)
        print "Cannot parse JSON"
        return None

    if 'result' in data:
        try:
            result = data['result']
            tst,lat,lon,vcell,soc = result.split(',')
            if int(tst) < 1:
                mqttc.publish(topic + '/warn', "ignore-zero %s" % result, qos=2, retain=False)
                print "Ignoring zeroed results:", result
                return None
            payload = {
                '_type':        'location',
                'tst':          int(tst),
                'lat':          float(lat),
                'lon':          float(lon),
                'tid':          device_id[-2:],
                'batt':         float(vcell),       # Battery voltage
                'soc':          float(soc),         # State of Charge (in %)
            }

            return json.dumps(payload)

        except:
            raise

    return payload

def on_disconnect(mosq, userdata, rc):

    reasons = {
       '0' : 'Connection Accepted',
       '1' : 'Connection Refused: unacceptable protocol version',
       '2' : 'Connection Refused: identifier rejected',
       '3' : 'Connection Refused: server unavailable',
       '4' : 'Connection Refused: bad user name or password',
       '5' : 'Connection Refused: not authorized',
    }
    reason = reasons.get(rc, "code=%s" % rc)
    print "Disconnected: ", reason

def on_log(mosq, userdata, level, string):
    print(string)

cf = ConfigParser.RawConfigParser()
cf.read("electron.ini")

hostname    = cf.get('mqtt', 'hostname')
port        = cf.get('mqtt', 'port')
tls_cert    = cf.get('mqtt', 'tls_cert')
username    = cf.get('mqtt', 'username')
password    = cf.get('mqtt', 'password')
topic       = cf.get('mqtt', 'topic')

token       = cf.get('particle', 'token')
device_id   = cf.get('particle', 'device_id')

clientid = 'owntracks-electron-pub-%s' % os.getpid()
protocol=paho.MQTTv31  # 3
protocol=paho.MQTTv311 # 4

mqttc = paho.Client(clientid, clean_session=True, userdata=None, protocol=protocol)
mqttc.on_disconnect = on_disconnect
mqttc.on_log = on_log

mqttc.tls_set(tls_cert)
mqttc.username_pw_set(username, password)

# Set OwnTracks-compatible LWT
mqttc.will_set(topic,
    payload=json.dumps({'_type':"lwt", "tst":int(time.time())}),
    qos=0, retain=False)

mqttc.loop_start()

mqttc.connect(hostname, port, 60)

while True:
    try:
        payload = get_cloud(mqttc, token, device_id)
        if payload is not None:
            (res, mid) =  mqttc.publish(topic, payload, qos=2, retain=True)
    except socket.error:
        print("MQTT server disconnected; sleeping")
        time.sleep(5)
    except KeyboardInterrupt:
        mqttc.disconnect()
        mqttc.loop_stop()
        sys.exit(0)
    except:
        raise

    time.sleep(10)

mqttc.loop_stop()
