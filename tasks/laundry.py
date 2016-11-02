from __future__ import absolute_import


import time
import urllib2
import json
import redis
import datetime
from tasks.celery import app
from resources.basics import dict_setdefault


@app.task(name='laundry.update')
def laundry_update():
    request_url = "http://23.23.147.128/homes/mydata/urba7723"
    response = urllib2.urlopen(request_url)
    data = json.load(response)

    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    r.set('app.tasks.laundry', json.dumps(data))

    room_names = []
    t = time.time()

    if not data['location']['rooms']:
        return

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


def laundry_stats_reset():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    room_names = json.loads(r.get("app.tasks.laundry.rooms"))

    for room in room_names:
        r.delete("app.tasks.laundry.stats.{}".format(room))


def laundry_stats_update():
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    room_names = json.loads(r.get("app.tasks.laundry.rooms"))

    for room in room_names:
        room_info = json.loads(r.get(room))
        room_stats_json = r.get("app.tasks.laundry.stats.{}".format(room))

        if room_stats_json:
            room_stats = json.loads(room_stats_json)
            room_stat = room_stats['room_stat']
            machine_stats = room_stats['machine_stats']
            last_timestamp = room_stats['timestamp']
        else:
            room_stat = {}
            machine_stats = {}
            last_timestamp = 0.

        current_timestamp = room_info['timestamp']
        delta_t = min(5 * 60, current_timestamp - last_timestamp)

        if delta_t > 0:
            machine_in_use = 0

            for machine in room_info['machine']:
                machine_id = machine['label']
                if machine_id not in machine_stats:
                    machine_stats[machine_id] = {}
                machine_stat = machine_stats[machine_id]
                dict_setdefault(machine_stat, {
                    'total_powered': 0.,
                    'total_usage': 0.,
                })

                machine_stat['total_powered'] += delta_t
                if machine['status'] == 'In Use':
                    machine_stat['total_usage'] += delta_t
                    machine_in_use += 1
                machine_stat['daily_usage'] = machine_stat['total_usage'] / max(86400, machine_stat['total_powered']) * 86400

            current_date = datetime.datetime.fromtimestamp(current_timestamp)
            hour, day = current_date.hour, current_date.weekday()

            dict_setdefault(room_stat, {
                'total_open_by_hour': [0.] * 24,
                'total_usage_by_hour': [0.] * 24,
                'average_usage_by_hour': [0.] * 24,

                'total_open_by_day': [0.] * 7,
                'total_usage_by_day': [0.] * 7,
                'average_usage_by_day': [0.] * 7,
            })

            room_stat['total_open_by_hour'][hour] += delta_t
            room_stat['total_usage_by_hour'][hour] += delta_t * machine_in_use
            room_stat['average_usage_by_hour'][hour] = room_stat['total_usage_by_hour'][hour] / room_stat['total_open_by_hour'][hour]

            room_stat['total_open_by_day'][day] += delta_t
            room_stat['total_usage_by_day'][day] += delta_t * machine_in_use
            room_stat['average_usage_by_day'][day] = room_stat['total_usage_by_day'][day] / room_stat['total_open_by_day'][day]

        r.set("app.tasks.laundry.stats.{}".format(room), json.dumps({
            'version': 1,
            'room_stat': room_stat,
            'machine_stats': machine_stats,
            'timestamp': current_timestamp
        }))
