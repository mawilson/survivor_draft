from web_project.settings import DEBUG

bind = "0.0.0.0:5000"
if not DEBUG:
    keyfile = "outdraft.me_private_key.key"
    certfile = "outdraft.me_ssl_certificate.cer"