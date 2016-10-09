from flask_restful import Resource
import urllib2
import json
import redis

class Laundry(Resource):
    def get(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        #print str(json.load(response))
        output =""
        try: 
            output = json.loads(r.get('app.tasks.laundry'))
        except Exception as e:
            output = str(e)
        return output

class LaundryID(Resource):
    def get(self, id):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        #print str(json.load(response))
        output =""
        try: 
            output = json.loads(r.get(str(id)))
        except Exception as e:
            output = str(e)
        return output