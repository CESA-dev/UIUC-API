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
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    st = json.dumps(json.load(response))
    r.set('app.tasks.laundry', st)

    data = json.loads(st)
    length = len(data['location']['rooms'])
        
    id_str = ["" for x in range(length)]
    machine = [ dict() for x in range(length)]
    name = ["" for x in range(length)]
    network = ["" for x in range(length)]
    i = 0

    while(i < length):
        id_str[i] = data['location']['rooms'][i]['id']
        machine[i] = data['location']['rooms'][i]['machines']
        name[i] = data['location']['rooms'][i]['name']
        network[i] = data['location']['rooms'][i]['networked']
        i = i + 1


    somelist = []
    i = 0
    t = time.time()
    while(i < length):                              
        temp = {}
        temp['machine'] = machine[i]
        temp['id'] = id_str[i]
        temp['networked'] = network[i]
        temp['timestamp'] = t
        somelist.append(json.dumps(temp))
        i = i + 1
        
    i = 0
    print name[i]
    print somelist[i]                          
    while(i < length):                              #set name as key
        
        r.set(name[i], somelist[i])
        i = i + 1


