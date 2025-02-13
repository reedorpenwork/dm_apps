from django.conf import settings
from django.template import loader

from dm_apps.context_processor import my_envr

from_email = settings.SITE_FROM_EMAIL


class SendInstructionsEmail:
    def __init__(self, object, request):
        self.request = request
        self.subject = 'Your NAS user account has been created'
        self.message = self.load_html_template(object)
        self.from_email = from_email
        self.to_list = [object.user.email]

    def load_html_template(self, object, ):
        t = loader.get_template('shares/email_instructions.html')
        context = {'object': object, 'request': self.request}
        context.update(my_envr(self.request))
        rendered = t.render(context)
        return rendered
