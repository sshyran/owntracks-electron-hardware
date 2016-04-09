#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.publish as mqtt
from sseclient import SSEClient
import json
import ConfigParser
import ssl
import time
import sys
import os

__author__    = 'Jan-Piet Mens <jpmens()gmail.com>'
__copyright__ = 'Copyright 2016 Jan-Piet Mens'
__license__   = """GPL2"""

eventname = 'owntracks'

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

auth = {
    "username" : username,
    "password" : password
}
tls = {
    "ca_certs" : tls_cert,
    "tls_version" : ssl.PROTOCOL_TLSv1,
}

will = {
    "topic":    topic,
    "qos":      2,
    "retain":   False,
    "payload":  json.dumps({'_type':"lwt", "tst":int(time.time())}),
}

clientid = 'owntracks-electron-pub-%s' % os.getpid()
protocol=3

def process(csv):
    try:
        tst,lat,lon,soc,interval = csv.split(',')
        if int(tst) < 1:
            print "Ignoring zeroed results:", result
        payload = {
            '_type':        'location',
            'tst':          int(tst),
            'lat':          float(lat),
            'lon':          float(lon),
            'tid':          device_id[-2:],
            'batt':         float(soc),       # State of Charge in %
            '_interval':           int(interval),
        }

        mqtt.single(topic, json.dumps(payload), qos=2, retain=True,
            hostname=hostname, port=int(port), client_id=clientid,
            auth=auth, will=will,
            tls=tls, protocol=int(protocol))

    except Exception, e:
        print str(e)
        raise


messages = SSEClient('https://api.spark.io/v1/events/%s?access_token=%s' % (eventname, token))

for msg in messages:
    event = str(msg.event).encode('utf-8')
    data = str(msg.data).encode('utf-8')
    # print "Event=", event
    # print "Data=[",data,"]"

    if event == eventname:
        print "Data=",data
        try:
            #   {
            #     "coreid": "nnnnnnnnnnnnnnnnnnnnnnnn",
            #     "published_at": "2016-04-09T08:29:40.532Z",
            #     "ttl": "600",
            #     "data": "1460190580,xx.543674,yy.422098,3.7,30.8,31"
            #   }

            j = json.loads(data)

            if 'coreid' in j and 'data' in j:
                if j['coreid'] == device_id:
                    process(j['data'])
        except:
            continue

