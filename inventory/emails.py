from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader

from dm_apps.context_processor import my_envr
from . import models

app_name = settings.WEB_APP_NAME  # should be a single word with one space
from_email = settings.SITE_FROM_EMAIL


class CertificationRequestEmail:

    def __init__(self, me, person_object, request):
        self.request = request
        self.me = me
        self.person_object = person_object
        self.subject = 'Your metadata inventory'
        self.message = self.load_html_template()
        try:
            self.from_email = me.user.email
        except AttributeError:
            # if the user has no email, use the default app email
            self.from_email = from_email

        self.to_list = [person_object.user.email, self.from_email]
        # self.cc_list = [admin_email,]

    def load_html_template(self):
        t = loader.get_template('inventory/emails/email_certification_request.html')
        context = {
            'me': self.me,
            'object': self.person_object,
            'queryset': self.person_object.resource_people.filter(role=1)
        }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)


class FlagForDeletionEmail:

    def __init__(self, object, user, request):
        self.request = request
        self.subject = 'A data resource has been flagged for deletion'
        self.message = self.load_html_template(object, user)
        self.from_email = from_email
        self.to_list = [user.email for user in User.objects.filter(groups__name="inventory_dm")]

    def load_html_template(self, object, user):
        t = loader.get_template('inventory/emails/email_flagged_for_deletion.html')
        context = {
            'object': object,
            'user': user,
        }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)


class FlagForPublicationEmail:

    def __init__(self, object, user, request):
        self.request = request
        self.subject = 'A data resource has been flagged for publication'
        self.message = self.load_html_template(object, user)
        self.from_email = from_email
        self.to_list = [user.email for user in User.objects.filter(groups__name="inventory_dm")]

    def load_html_template(self, object, user):
        t = loader.get_template('inventory/emails/email_flagged_for_publication.html')
        context = {
            'object': object,
            'user': user,
        }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)


class AddedAsCustodianEmail:

    def __init__(self, object, user, request):
        self.request = request
        self.subject = 'You have been added as a custodian'
        self.message = self.load_html_template(object, user)
        self.from_email = from_email
        self.to_list = [user.email, ]

    def load_html_template(self, object, user):
        t = loader.get_template('inventory/emails/email_added_as_custodian.html')
        context = {
            'object': object,
            'user': user,
        }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)


class RemovedAsCustodianEmail:

    def __init__(self, object, user, request):
        self.request = request
        self.subject = 'You have been removed as a custodian'
        self.message = self.load_html_template(object, user)
        self.from_email = from_email
        self.to_list = [user.email, ]

    def load_html_template(self, object, user):
        t = loader.get_template('inventory/emails/email_removed_as_custodian.html')
        context = {
            'object': object,
            'user': user,
        }
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered

    def __str__(self):
        return "FROM: {}\nTO: {}\nSUBJECT: {}\nMESSAGE:{}".format(self.from_email, self.to_list, self.subject, self.message)
