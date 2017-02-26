from flask_restful import Resource, reqparse
import urllib2
import json
import requests
import redis

class Dining(Resource):
    def get(self, hall, date_str):
        dt_str = date_str.replace('_', '/')
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        key = 'app.tasks.dining.{}.{}'.format(dt_str, hall)
        retval = r.get(key)
        try:
            return json.loads(retval)
        except ValueError:
            return "error!!"

