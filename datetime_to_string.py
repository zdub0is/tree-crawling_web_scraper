import datetime
def datetime_to_string():
  now = datetime.datetime.now()
  return now.strftime("%d%m%Y-%H%M%S")