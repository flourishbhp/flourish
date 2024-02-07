from celery import shared_task
from django.core.management import call_command


@shared_task
def run_sequential_enrollment():
    call_command('sequential_enrollment')


@shared_task
def run_facet_children_turning_6_months():
    call_command('load_children_turning_6_months')
