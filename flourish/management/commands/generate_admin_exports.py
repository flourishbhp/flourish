import os, json
from tqdm import tqdm
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError
from edc_base.model_mixins import ListModelMixin

from flourish_caregiver.admin_site import flourish_caregiver_admin
from flourish_child.admin_site import flourish_child_admin
from flourish_facet.admin_site import flourish_facet_admin

from flourish.tasks import generate_export_and_send_email

admin_site_map = {'flourish_child': flourish_child_admin,
                  'flourish_caregiver': flourish_caregiver_admin,
                  'flourish_facet': flourish_facet_admin}


class Command(BaseCommand):
    help = 'Run export method from model admin to generate csv data for all CRF and non-CRF models.'

    def add_arguments(self, parser):
        parser.add_argument(
            'args',
            metavar='app_label[.ModelName]',
            nargs='*',
            help='Exports data for a specified app_label or app_label.ModelName')

    def handle(self, *args, **kwargs):
        app_list = {}
        if not args:
            # Get all CRF models from `flourish_caregiver` and `flourish_child` app configs,
            # update to dictionary {model_name: models_cls} key, value pair.
            args = ('flourish_caregiver', 'flourish_child', )

        # Check args defined for specific app_label and/or model name(s)
        for model_args in args:
            try:
                _app_label, _model_name = model_args.split('.')
            except ValueError:
                # This is just an app - no model qualifier
                try:
                    app_config = django_apps.get_app_config(model_args)
                except LookupError as e:
                    raise CommandError(str(e))
                else:
                    app_list.update(app_config.models)
            else:
                # Assumes this is an app_label.model_name definition
                try:
                    model_cls = django_apps.get_model(model_args)
                except LookupError as e:
                    raise CommandError(
                        f'Model not loaded/recognised {model_args}')
                else:
                    app_list.update(
                        {f'{model_cls._meta.model_name}': model_cls})

        app_list = {key: value._meta.label_lower for key, value in app_list.items() if not self.exclude_rel_models(value)}

        generate_export_and_send_email.delay(app_list, 'management_command', )

    def exclude_rel_models(self, model_cls):
        """ Restrict the export to only CRFs and enrolment forms, excludes m2m,
            inlines and any other relationship models that will be included as
            part of the main parent data.
            @param app_list: dictionary of model_name: model_cls
        """
        exclude = False
        # Check model class is m2m, skip
        if issubclass(model_cls, ListModelMixin):
            exclude = True
        intermediate_model = model_cls._meta.verbose_name.endswith(
            'relationship')
        if intermediate_model:
            exclude = True
        return exclude
