from datetime import datetime

from dateutil.relativedelta import MO, TU, WE, TH, FR, SA, SU
from dateutil.tz import gettz
from django.apps import AppConfig as DjangoAppConfig
from edc_base.apps import AppConfig as BaseEdcBaseAppConfig
from edc_constants.constants import FAILED_ELIGIBILITY
from edc_data_manager.apps import AppConfig as BaseEdcDataManagerAppConfig
from edc_facility.apps import AppConfig as BaseEdcFacilityAppConfig
from edc_locator.apps import AppConfig as BaseEdcLocatorAppConfig
from edc_metadata.apps import AppConfig as BaseEdcMetadataAppConfig
from edc_protocol.apps import AppConfig as BaseEdcProtocolAppConfig
from edc_timepoint.apps import AppConfig as BaseEdcTimepointAppConfig
from edc_timepoint.timepoint import Timepoint
from edc_timepoint.timepoint_collection import TimepointCollection

from edc_appointment.appointment_config import AppointmentConfig
from edc_appointment.apps import AppConfig as BaseEdcAppointmentAppConfig
from edc_appointment.constants import COMPLETE_APPT
from edc_odk.apps import AppConfig as BaseEdcOdkAppConfig
from edc_senaite_interface.apps import AppConfig as BaseEdcSenaiteInterfaceAppConfig
from edc_visit_tracking.apps import AppConfig as BaseEdcVisitTrackingAppConfig
from edc_visit_tracking.constants import SCHEDULED, UNSCHEDULED, LOST_VISIT, \
    COMPLETED_PROTOCOL_VISIT, MISSED_VISIT
from flourish_dashboard.patterns import subject_identifier


class AppConfig(DjangoAppConfig):
    name = 'flourish'


class EdcAppointmentAppConfig(BaseEdcAppointmentAppConfig):
    configurations = [
        AppointmentConfig(
            model='edc_appointment.appointment',
            related_visit_model='flourish_caregiver.maternalvisit',
            appt_type='clinic'),
        AppointmentConfig(
            model='pre_flourish.caregiverappointment',
            related_visit_model='pre_flourish.preflourishcaregivervisit',
            appt_type='clinic'),
        AppointmentConfig(
            model='flourish_child.appointment',
            related_visit_model='flourish_child.childvisit',
            appt_type='clinic')
    ]


class EdcBaseAppConfig(BaseEdcBaseAppConfig):
    project_name = 'Flourish'
    institution = 'Botswana-Harvard AIDS Institute'


class EdcDataManagerAppConfig(BaseEdcDataManagerAppConfig):
    identifier_pattern = subject_identifier
    extra_assignee_choices = {
        'td_clinic': [
            ('clinic', 'Clinic'),
            ['gmasasa@bhp.org.bw']],
        'se_dmc': [
            ('se_dmc', 'SE & DMC'),
            ['adiphoko@bhp.org.bw', 'ckgathi@bhp.org.bw', 'imosweu@bhp.org.bw',
             'mchawawa@bhp.org.bw']]}
    child_subject = True


class EdcProtocolAppConfig(BaseEdcProtocolAppConfig):
    protocol = 'BHP142'
    protocol_name = 'Flourish'
    protocol_number = '142'
    protocol_title = ''
    study_open_datetime = datetime(
        2020, 7, 1, 0, 0, 0, tzinfo=gettz('UTC'))
    study_close_datetime = datetime(
        2025, 6, 30, 23, 59, 59, tzinfo=gettz('UTC'))


class EdcTimepointAppConfig(BaseEdcTimepointAppConfig):
    timepoints = TimepointCollection(
        timepoints=[
            Timepoint(
                model='edc_appointment.appointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='edc_appointment.historicalappointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='pre_flourish.caregiverappointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='pre_flourish.caregiverappointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='flourish_child.appointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT),
            Timepoint(
                model='flourish_child.historicalappointment',
                datetime_field='appt_datetime',
                status_field='appt_status',
                closed_status=COMPLETE_APPT)
        ])


class EdcLocatorAppConfig(BaseEdcLocatorAppConfig):
    name = 'edc_locator'
    reference_model = 'flourish_caregiver.maternallocator'


class EdcVisitTrackingAppConfig(BaseEdcVisitTrackingAppConfig):
    visit_models = {
        'flourish_caregiver': (
            'maternal_visit', 'flourish_caregiver.maternalvisit'),
        'flourish_child': (
            'child_visit', 'flourish_child.childvisit'),
        'pre_flourish': (
            'pre_flourish_caregiver_visit', 'pre_flourish.preflourishcaregivervisit'),
    }


class EdcFacilityAppConfig(BaseEdcFacilityAppConfig):
    country = 'botswana'
    definitions = {
        '7-day clinic': dict(days=[MO, TU, WE, TH, FR, SA, SU],
                             slots=[100, 100, 100, 100, 100, 100, 100]),
        '5-day clinic': dict(days=[MO, TU, WE, TH, FR],
                             slots=[100, 100, 100, 100, 100])}


class EdcMetadataAppConfig(BaseEdcMetadataAppConfig):
    reason_field = {
        'pre_flourish.preflourishcaregivervisit': 'reason',
        'flourish_caregiver.maternalvisit': 'reason',
        'flourish_child.childvisit': 'reason', }
    create_on_reasons = [SCHEDULED, UNSCHEDULED, COMPLETED_PROTOCOL_VISIT]
    delete_on_reasons = [LOST_VISIT, MISSED_VISIT, FAILED_ELIGIBILITY]


class EdcOdkAppConfig(BaseEdcOdkAppConfig):
    adult_child_study=False
    adult_consent_model='flourish_caregiver.subjectconsent'
    child_assent_model='flourish_child.childassent'
    clinician_notes_form_ids = {
        'flourish_child': 'child_cliniciannotes_v1.0',
        'flourish_caregiver': 'caregiver_cliniciannotes_v1.0'}

    clinician_notes_models = {
        'flourish_child': 'childcliniciannotes',
        'flourish_caregiver': 'cliniciannotes'}


class EdcSenaiteInterfaceAppConfig(BaseEdcSenaiteInterfaceAppConfig):
    host = "https://bhplims.bhp.org.bw"
    client = "Flourish"
    courier = ""
    sample_type_match = {'viral_load': 'Whole Blood EDTA',
                         'cd4': 'Whole Blood EDTA',
                         'hematology': 'Whole Blood EDTA',
                         'complete_blood_count': 'Whole Blood EDTA',
                         'infant_pl_cytokines': 'Whole Blood EDTA',
                         'dna_pcr': 'Dry Blood Spot',
                         'stool_sample': 'Stool',
                         'rectal_swab': 'Swab',
                         'chemistry': 'Whole Blood SST',
                         'fasting_glucose': 'Whole Blood SST',
                         'fasting_insulin': 'Whole Blood SST',
                         'lead_level': 'Whole Blood EDTA',
                         'fbc': 'Whole Blood EDTA',
                         'child_pl_store': 'Whole Blood EDTA',
                         'lithium_heparin': 'Whole Blood Lithium Heparin',
                         'serum_storage': 'Whole Blood SST'}
    container_type_match = {'viral_load': 'EDTA tube',
                            'cd4': 'EDTA tube',
                            'hematology': 'EDTA tube',
                            'complete_blood_count': 'EDTA Tube',
                            'infant_pl_cytokines': 'EDTA Tube',
                            'dna_pcr': 'Filter paper',
                            'stool_sample': 'Cryogenic Vial',
                            'rectal_swab': 'Cryogenic Vial',
                            'chemistry': 'SST Tube',
                            'fasting_glucose': 'SST Tube',
                            'fasting_insulin': 'SST Tube',
                            'lead_level': 'EDTA tube',
                            'fbc': 'EDTA tube',
                            'child_pl_store': 'EDTA tube',
                            'lithium_heparin': 'Lithium Heparin tube',
                            'serum_storage': 'SST Tube'}
    template_match = {'viral_load': 'HIV RNA PCR',
                      'cd4': 'CD4/CD8',
                      'hematology': 'CBC',
                      'complete_blood_count': 'CBC',
                      'infant_pl_cytokines': 'Plasma for Cytokines',
                      'dna_pcr': 'HIV DNA PCR',
                      'stool_sample': 'Stool Storage',
                      'rectal_swab': 'Rectal Swab Storage',
                      'chemistry': 'Chemistry',
                      'fasting_glucose': 'Fasting glucose',
                      'fasting_insulin': 'Insulin',
                      'lead_level': 'Lead',
                      'fbc': 'CBC',
                      'child_pl_store': 'Storage plasma',
                      'lithium_heparin': 'QuantiFERON-TB Gold Plus',
                      'serum_storage': 'Storage serum'}
