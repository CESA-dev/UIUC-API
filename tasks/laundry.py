from __future__ import absolute_import


import time
import urllib2
import json
import redis
from tasks.celery import app


@app.task(name='laundry.update')
def laundry_update():
    request_url = "http://23.23.147.128/homes/mydata/urba7723"
    response = urllib2.urlopen(request_url)
    data = json.load(response)

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set('app.tasks.laundry', json.dumps(data))

    room_names = []
    t = time.time()

    for room in data['location']['rooms']:
        room_name = room['name']
        room_info = {
            'machine': room['machines'],
            'id': room['id'],
            'networked': room['networked'],
            'timestamp': t
        }

        room_names.append(room_name)
        r.set(room_name, json.dumps(room_info))

    r.set("app.tasks.laundry.rooms", json.dumps(room_names))
