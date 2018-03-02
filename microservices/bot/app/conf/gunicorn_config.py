import os
import multiprocessing

bind = "0.0.0.0:8080"
workers = 1
accesslog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
loglevel = "None"
capture_output = True
enable_stdio_inheritance = True
