import config
import sys
from datetime_to_string import datetime_to_string


def err_exit():
  err_record()
  sys.exit(1)


def err_record():
  with open('errlog.txt', 'w') as f:
    f.write('/n'.join(config.ERRLOG))


def event_log_maintain(message):
  config.EVENTLOG.append(f"[{datetime_to_string()}] - {message}")
  print(f"[{datetime_to_string()}] - {message}")
