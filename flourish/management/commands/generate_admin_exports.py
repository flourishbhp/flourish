from django.apps import apps as django_apps
from django.core.management.base import BaseCommand, CommandError

from flourish_caregiver.admin_site import flourish_caregiver_admin
from flourish_child.admin_site import flourish_child_admin
from flourish_facet.admin_site import flourish_facet_admin

from flourish.tasks import generate_exports
from flourish_export.admin_export_helper import AdminExportHelper

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
        export_helper_cls = AdminExportHelper()
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

        app_list = export_helper_cls.remove_exclude_models(app_list)

        generate_exports.delay(app_list, 'management_command', )
