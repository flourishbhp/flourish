import os, shutil, redis
from tqdm import tqdm
from celery import shared_task, group
from django.apps import apps as django_apps
from django.core.management import call_command
from django.core.mail import send_mail
from django.conf import settings

from edc_base.utils import get_utcnow
from flourish_caregiver.admin_site import flourish_caregiver_admin
from flourish_child.admin_site import flourish_child_admin
from flourish_facet.admin_site import flourish_facet_admin
from flourish_export.identifiers import ExportIdentifier


@shared_task
def run_sequential_enrollment():
    call_command('sequential_enrollment')


@shared_task
def run_facet_children_turning_6_months():
    call_command('load_children_turning_6_months')


@shared_task
def run_exports(model_cls, app_label):
    """ Executes the csv model export method from admin export action(s) and writes response
        content to an excel file.
        @param model_cls: Specific model class definition
        @param app_label: Specific app label for the model class 
    """
    admin_site_map = {'flourish_child': flourish_child_admin,
                      'flourish_caregiver': flourish_caregiver_admin,
                      'flourish_facet': flourish_facet_admin}

    model_cls = django_apps.get_model(model_cls)
    app_admin_site = admin_site_map.get(app_label, None)

    model_admin_cls = app_admin_site._registry.get(model_cls, None)

    queryset = model_cls.objects.all()

    if not model_admin_cls:
        print(f'Model class not registered {model_cls._meta.verbose_name}')
    elif not queryset.exists():
        print(f'Empty queryset returned for {model_cls._meta.verbose_name}')
    else:
        file_path = f'media/admin_exports/{app_label}_{get_utcnow().date()}'

        if hasattr(model_admin_cls, 'export_as_csv'):
            """
            Can be used to exclude some models not needed in the exports
            by excluding the mixin from the model admin of interest
            """
            response = model_admin_cls.export_as_csv(
                request=None, queryset=queryset)

            if response:
                if response.status_code == 200:
                    if not os.path.exists(file_path):
                        os.makedirs(file_path)
                    with open(f'{file_path}/{model_admin_cls.get_export_filename()}.xlsx', 'wb') as file:
                        file.write(response.content)
                else:
                    response.raise_for_status()
            else:
                print(f'Empty response returned for {model_cls._meta.verbose_name}')


@shared_task
def generate_exports(
        app_list, export_type, create_zip=False, user_emails=[]):

    app_labels = set()

    # Initialize a Redis client
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    # Construct the lock key based on the export type
    lock_key = f'export_lock_{export_type}'

    # Attempt to acquire the lock
    is_locked = redis_client.set(lock_key, 'locked', nx=True, ex=60)

    # Check if lock is acquired successfully and initiate export
    if is_locked:
        try:
            # Create a list to store the group of export tasks
            export_tasks = []
    
            for _, model_cls in tqdm(app_list.items()):
                app_label = model_cls.split('.')[0]
                app_labels.add(app_label)
    
                # Call the export_data task asynchronously and store the task
                export_tasks.append(run_exports.si(model_cls, app_label))
        
            # Group all export tasks together
            export_group = group(export_tasks)
        
            # Execute the group of export tasks and wait for all tasks to complete
            result = export_group.delay()
            if create_zip:
                print('Zipping........')
                result.then(zip_and_send_email.si(app_labels, user_emails))
    
        finally:
            redis_client.delete(lock_key)
    else:
        return {'status': 'warning',
                'message':
                (f'Export for {export_type} that was initiated is still running '
                 'please wait until an export is fully prepared.')}

@shared_task
def zip_and_send_email(app_labels, user_emails):
    for app_label in app_labels:
        export_model_cls = django_apps.get_model('flourish_export.exportfile')
        zip_folder = f'media/admin_exports/{app_label}__{get_utcnow().date()}'
    
        # Zip the exported files
        if not os.path.isfile(zip_folder):
            shutil.make_archive(zip_folder, 'zip', zip_folder)
    
        export_identifier = ExportIdentifier().identifier
        description = f'{app_label.replace("_", " ").title()} Export(s)'
        model_options = {
            'description': description,
            'study': app_label,
            'export_identifier': export_identifier,
            'download_time': get_utcnow().time(),
            'document': f'{zip_folder}.zip'}
    
        print('Inside.....')
        export_model_cls.objects.create(**model_options)
    
        subject = f'{export_identifier} {description}'
        message = (f'{export_identifier} {description} have been successfully '
                   'generated and ready for download. This is an automated message.')
    
        try:
            send_mail(subject=subject,
                      message=message,
                      from_email=settings.DEFAULT_FROM_EMAIL,
                      receipient_list=user_emails,
                      fail_silently=False)
        except Exception as e:
            print(f'Error sending email: {str(e)}')
