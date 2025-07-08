"""
Gunicorn configuration file.

Settings:
    bind (str): The socket to bind. "0.0.0.0:5000" means the server will be accessible on all network interfaces at port 5000.
    workers (int): The number of worker processes for handling requests. Set to 4 for handling concurrent requests efficiently.
    timeout (int): Workers silent for more than this many seconds are killed and restarted. Set to 120 seconds.
    keepalive (int): The number of seconds to wait for requests on a Keep-Alive connection. Set to 5 seconds.
    accesslog (str): The file to write access logs to. "-" means log to stdout.
    errorlog (str): The file to write error logs to. "-" means log to stderr.
"""

bind = "0.0.0.0:5000"
workers = 4
timeout = 120
keepalive = 5
accesslog = "-"
errorlog = "-"