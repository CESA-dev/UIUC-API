

from datetime import timedelta

CELERYBEAT_SCHEDULE = {
    'add-every-30-seconds': {
        'task': 'laundry.update',
        'schedule': timedelta(seconds=30),
    },

    'add-every-day': {
        'task': 'dining.update',
        'schedule': timedelta(days=1),
       
    },

}

CELERY_TIMEZONE = 'UTC'




