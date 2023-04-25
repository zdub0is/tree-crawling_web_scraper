import datetime
import os
import json
import config
from datetime_to_string import datetime_to_string
from error_handle import event_log_maintain


def save_pages(visited, pages):
  n = datetime_to_string()
  file_name = f"output_{n}.json"
  file_path = os.path.join('output', file_name)
  json_data = json.dumps({'visited': visited, 'pages': pages})
  with open(file_path, 'w') as f:
    f.write(json_data)
  config.EVENTLOG.append(f"[{n}] - New file written at {file_path}")
  print(f"Saved to {file_path}")


def event_log():
  n = datetime_to_string()
  file_name = f"event_{n}.txt"
  file_path = os.path.join('event', file_name)
  with open(file_path, 'w') as f:
    for line in config.EVENTLOG:
      f.write(line + "\n")
  config.EVENTLOG.append(f"[{n}] - New file written at {file_path}")
  print(f"[{n}] - Exported event log.")


def get_most_recent_file():
  files = [
    os.path.join('output', f) for f in os.listdir('output')
    if os.path.isfile(os.path.join('output', f))
  ]
  if not files:
    return None

  most_recent_file = max(files, key=os.path.getmtime)
  return most_recent_file


def load_state():
  most_recent_file = get_most_recent_file()

  if most_recent_file != None:
    event_log_maintain(
      f"Opening the most recently edited file: {most_recent_file}")
    with open(most_recent_file, 'r') as f:
      content = json.load(f)
    event_log_maintain("File opened.")
    return content["visited"], content["pages"]
  else:
    event_log_maintain("No files found in the folder.")
    return None, None
