from __future__ import absolute_import

from celery import Celery
from tasks import celeryconfig
app = Celery('tasks',broker='redis://localhost:6379', backend='redis://localhost:6379', include=['tasks.laundry', 'tasks.crawl_dining'])
app.config_from_object(celeryconfig)


if __name__ == '__main__':
    app.start()


