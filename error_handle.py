import config
import sys
from datetime_to_string import datetime_to_string


def err_exit():
  err_record()
  sys.exit(1)


def err_record():
  with open('errlog.txt', 'w') as f:
    for line in config.ERRLOG:
      f.write(line + "\n")


def event_log_maintain(message):
  pass
  # config.EVENTLOG.append(f"[{datetime_to_string()}] - {message}")
  # print(f"[{datetime_to_string()}] - {message}")
