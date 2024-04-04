import ssl

from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.utils.functional import cached_property

import certifi


class EmailBackend(SMTPBackend):
    @cached_property
    def ssl_context(self):

        ssl_context = ssl.create_default_context(cafile=certifi.where()) # manually load in certifi cert authority, in the event OS doesn't have them properly configured
        ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
        ssl_context.get_ca_certs()
        return ssl_context