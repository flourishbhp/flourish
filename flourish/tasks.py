import os
from celery import shared_task
from django.apps import apps as django_apps
from django.core.management import call_command

from flourish_caregiver.admin_site import flourish_caregiver_admin
from flourish_child.admin_site import flourish_child_admin
from flourish_facet.admin_site import flourish_facet_admin


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
        raise ValueError(f'Model class not registered {model_cls._meta.verbose_name}')
    elif not queryset.exists():
        raise ValueError(f'Empty queryset returned for {model_cls._meta.verbose_name}')
    else:
        file_path = f'media/admin_exports/{app_label}'

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
                raise ValueError(f'Empty response returned for {model_cls._meta.verbose_name}')
