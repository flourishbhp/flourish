from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flourish.settings')

app = Celery('flourish')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Configure an over age calculation task to run Mon-Fri at 6a.m
app.conf.beat_schedule = {
    "schedule-over-age-calculation": {
        "task": "flourish_child.utils.over_age_limit",
        "schedule": crontab(hour=6, minute=0, day_of_week='mon-fri')
    },
    "schedule-odk-data-pull": {
        "task": "edc_odk.tasks.pull_all_data_from_odkcentral",
        "schedule": crontab(minute="*", day_of_week='*')
    },
    "schedule-load-previous-study-data": {
        "task": "flourish_reports.tasks.populate_study_data",
        "schedule": crontab(hour='5,13', minute=0, day_of_week='mon-fri')
    }
}
