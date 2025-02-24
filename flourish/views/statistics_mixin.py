from edc_base.view_mixins import EdcBaseViewMixin
from django.apps import apps as django_apps
from django.db.models import Q
from django.views.generic import TemplateView
from django.core.cache import cache
from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from edc_constants.constants import DEAD


class StatisticsMixin(EdcBaseViewMixin):
    subject_consent_model = 'flourish_caregiver.subjectconsent'

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    maternal_dataset_model = 'flourish_caregiver.maternaldataset'

    child_dataset_model = 'flourish_child.childdataset'

    caregiver_offstudy_model = 'flourish_prn.caregiveroffStudy'

    child_offstudy_model = 'flourish_prn.childoffstudy'

    antenatal_enrollment_model = 'flourish_caregiver.antenatalenrollment'

    maternal_delivery_model = 'flourish_caregiver.maternaldelivery'

    maternal_visit_model = 'flourish_caregiver.maternalvisit'

    child_visit_model = 'flourish_child.childvisit'

    child_death_report_model = 'flourish_prn.childdeathreport'

    caregiver_death_report_model = 'flourish_prn.caregiverdeathreport'

    anc_schedule_model = 'flourish_caregiver.onschedulecohortaantenatal'

    ssh_model = 'edc_visit_schedule.subjectschedulehistory'

    @property
    def child_death_report_cls(self):
        return django_apps.get_model(self.child_death_report_model)

    @property
    def caregiver_death_report_cls(self):
        return django_apps.get_model(self.caregiver_death_report_model)

    @property
    def maternal_visit_cls(self):
        return django_apps.get_model(self.maternal_visit_model)

    @property
    def child_visit_cls(self):
        return django_apps.get_model(self.child_visit_model)

    @property
    def maternal_delivery_cls(self):
        return django_apps.get_model(self.maternal_delivery_model)

    @property
    def antenatal_enrollment_cls(self):
        return django_apps.get_model(self.antenatal_enrollment_model)

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model(self.child_offstudy_model)

    @property
    def caregiver_offstudy_cls(self):
        return django_apps.get_model(self.caregiver_offstudy_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)

    @property
    def subject_consent_cls(self):
        return django_apps.get_model(self.subject_consent_model)

    @property
    def maternal_dataset_cls(self):
        return django_apps.get_model(self.maternal_dataset_model)

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)

    @property
    def caregiver_offstudies(self):
        return self.caregiver_offstudy_cls.objects.values_list(
            'subject_identifier', flat=True)

    @property
    def child_offstudies(self):
        return self.child_offstudy_cls.objects.values_list(
            'subject_identifier', flat=True)

    @property
    def anc_schedule_model_cls(self):
        return django_apps.get_model(self.anc_schedule_model)

    @property
    def ssh_model_cls(self):
        return django_apps.get_model(self.ssh_model)

    @property
    def prior_bhp_maternal_subject_identifiers(self):
        subject_identifiers = set(
            self.subject_consent_cls.objects.filter(
                recruitment_clinic__iexact='prior').values_list(
                    'subject_identifier', flat=True))
        return subject_identifiers

    @property
    def prior_bhp_child_subject_identifiers(self):
        study_child_identifiers = self.child_dataset_cls.objects.values_list(
            'study_child_identifier', flat=True)

        subject_identifiers = set(self.caregiver_child_consent_cls.objects.filter(
            study_child_identifier__in=study_child_identifiers
        ).values_list('subject_identifier', flat=True))

        return subject_identifiers

    @property
    def total_flourish_consents(self):
        """
            Returns all caregiver consents (on and off study).
        """
        return len(set(self.subject_consent_cls.objects.values_list(
            'subject_identifier', flat=True)))

    @property
    def total_child_assents(self):
        child_assent_cls = django_apps.get_model('flourish_child.childassent')
        return len(set(child_assent_cls.objects.values_list(
            'subject_identifier', flat=True)))

    @property
    def total_child_consents(self):
        """
            Returns all caregiver child consents (on and off study).
        """
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        return len(set(child_consent_cls.objects.values_list(
            'subject_identifier', flat=True)))

    @property
    def total_continued_consents(self):
        continued_consent_cls = django_apps.get_model(
            'flourish_child.childcontinuedconsent')
        return len(set(continued_consent_cls.objects.values_list(
            'subject_identifier', flat=True)))

    @property
    def total_caregiver_prev_study(self):
        """
            Caregivers from previous BHP studies Currently on-Study
        """
        dataset_sidx = self.maternal_dataset_cls.objects.values_list(
            'screening_identifier', flat=True)

        subject_consents = set(self.subject_consent_cls.objects.exclude(
            subject_identifier__in=self.caregiver_offstudies).filter(
                screening_identifier__in=dataset_sidx).values_list(
                    'subject_identifier', flat=True))
        return len(subject_consents)

    @property
    def total_child_prev(self):
        """
            Children from previous BHP studies Currently on-Study
        """
        total_children = set(self.caregiver_child_consent_cls.objects.exclude(
            subject_identifier__in=self.child_offstudies).filter(
                study_child_identifier__isnull=False).values_list(
                    'subject_identifier', flat=True))

        return len(total_children)

    @property
    def total_all_preg_women(self):
        """
            All women who consented when pregnant (on and off study)
        """

        return len(set(self.antenatal_enrollment_cls.objects.values_list(
            'subject_identifier', flat=True)))

    @property
    def total_consented_pregnant_women(self):
        """
            All women who consented when pregnant – Currently ON- study
        """

        all_consented_women = set(self.antenatal_enrollment_cls.objects.exclude(
            subject_identifier__in=self.caregiver_offstudies).values_list(
                'subject_identifier', flat=True))
        return len(all_consented_women)

    @property
    def total_currently_pregnant_women(self):
        """
            Currently Pregnant Women On-Study
        """
        currently_preg = 0
        preg_enrol = self.antenatal_enrollment_cls.objects.exclude(
            subject_identifier__in=self.caregiver_offstudies).values_list(
                'child_subject_identifier', flat=True)

        for child_idx in preg_enrol:
            delv = self.maternal_delivery_cls.objects.filter(
                child_subject_identifier=child_idx).exists()
            if delv:
                continue
            onschedule = self.anc_schedule_model_cls.objects.filter(
                child_subject_identifier=child_idx).values(
                    'subject_identifier', 'schedule_name').first()
            is_onschedule = self.ssh_model_cls.objects.filter(
                subject_identifier=onschedule.get('subject_identifier', None),
                schedule_name=onschedule.get('schedule_name', None),
                schedule_status='onschedule').exists()
            if is_onschedule:
                currently_preg += 1

        return currently_preg

    @property
    def total_maternal_delivery(self):
        """
            Newly recruited (not from previous BHP studies) women enrolled in
            pregnancy who gave birth who are currently On-Study
        """

        return self.maternal_delivery_cls.objects.exclude(
            subject_identifier__in=self.caregiver_offstudies).count()

    @property
    def total_prev_caregivers_offstudy(self):
        return self.caregiver_offstudy_cls.objects.filter(
            subject_identifier__in=self.prior_bhp_maternal_subject_identifiers
        ).count()

    @property
    def total_prev_child_offstudy(self):
        return self.child_offstudy_cls.objects.filter(
            subject_identifier__in=self.prior_bhp_child_subject_identifiers
        ).count()

    @property
    def total_caregivers_deaths(self):
        return self.caregiver_death_report_cls.objects.count()

    @property
    def total_child_deaths(self):
        return self.child_death_report_cls.objects.count()

    @property
    def total_prev_caregivers_deaths(self):
        return self.caregiver_death_report_cls.objects.filter(
            subject_identifier__in=self.prior_bhp_maternal_subject_identifiers,
        ).count()

    @property
    def total_prev_child_deaths(self):
        return self.child_death_report_cls.objects.filter(
            subject_identifier__in=self.prior_bhp_child_subject_identifiers,
        ).count()
