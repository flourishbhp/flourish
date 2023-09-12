from celery import shared_task
from django.core.management import call_command

@shared_task()
def run_sequential_enrollment():
    call_command('sequential_enrollment')
