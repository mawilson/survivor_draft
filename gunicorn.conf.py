from web_project.settings import DEBUG

bind = "0.0.0.0:443"
if not DEBUG:
    keyfile = "outdraft_key.pem"
    certfile = "outdraft_cert.pem"

errorlog = "errorlog"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'