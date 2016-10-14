from flask import Flask
from flask_restful import Api, Resource
from werkzeug.contrib.cache import SimpleCache

from resources.dining import Dining, DiningInformation, DiningSearch, DiningToday
from resources.weather import Weather
from resources.wifi import Wifi, WifiNearMe
from resources.laundry import Laundry, LaundryID, LaundryName
from resources.main import Main
from resources.free_food import FreeFood
from resources.ews_status import EWSStatus
from resources.athletic_schedule import AthleticSchedule
from resources.buildings import Buildings
from resources.directory import FacultyDirectory
from resources.daily_illini import News, SubCategoryNews, SportsNews, RecentNews
from resources.calendar import Calendar
from celery import Celery
import sys


def make_celery(app):
    celery = Celery(app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
            broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery



app = Flask(__name__)
app.config.update(
        CELERY_BROKER_URL='redis://localhost:6379',
        CELERY_RESULT_BACKEND='redis://localhost:6379'
        )
celery = make_celery(app)
api = Api(app)
cache = SimpleCache(app)

# Define routes
api.add_resource(Main, '/')

'''Dining'''
api.add_resource(DiningToday, '/dining/<string:hall>')
api.add_resource(Dining, '/dining/<string:hall>/<string:dateFrom>/<string:dateTo>')
api.add_resource(DiningSearch, '/dining/search/<string:query>')
api.add_resource(DiningInformation, '/dining/information')

'''Wifi'''
api.add_resource(Wifi, '/wifi')
#api.add_resource(WifiNearMe, '/wifi/<string:latitude>/<string:longitude>')

api.add_resource(Weather, '/weather')

api.add_resource(Laundry, '/laundry')
api.add_resource(LaundryID, '/laundry/<string:id>')
api.add_resource(LaundryName, '/laundry/<string:name>')


api.add_resource(FacultyDirectory, '/directory/faculty')

'''News'''
api.add_resource(News, '/news/<string:category>')
api.add_resource(SubCategoryNews, '/news/<string:category>/<string:subcategory>')
api.add_resource(SportsNews, '/news/<string:category>/<string:subcategory>/<string:sportcategory>')
api.add_resource(RecentNews, '/news/recent')

api.add_resource(Buildings, '/buildings')

api.add_resource(AthleticSchedule, '/athleticschedule/<string:sport>')

#api.add(Maintenance, '', '')

api.add_resource(FreeFood, '/freefood')

api.add_resource(EWSStatus, '/ews-status')

api.add_resource(Calendar, '/calendar/<string:year>')

@celery.task(trail=True)
def hello():
    print("hi!!")
    return 1

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "debug":
            app.debug = True
        else:
            app.debug = False

    import logging
    import os
    from logging.handlers import RotatingFileHandler
    
    
    app_dir = os.path.dirname(os.path.realpath(__file__))
    file_handler = RotatingFileHandler('{}/app.log'.format(app_dir), maxBytes=1024 * 1024 * 100, backupCount=20)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    access_logger = logging.getLogger('werkzeug')
    access_handler = RotatingFileHandler('{}/access.log'.format(app_dir), maxBytes=1024 * 1024 * 100, backupCount=20)
    access_logger.addHandler(access_handler)
    app.run(debug=True, host='0.0.0.0')
