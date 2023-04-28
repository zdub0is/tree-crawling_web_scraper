import requests
from bs4 import BeautifulSoup
import json
import config as cfg
from error_handle import event_log_maintain
import re
import dbms
import asyncio
import traceback
from error_handle import err_record

DBMS = dbms.DBMS()


def is_allowed(url):
  disallowed_patterns = [
    "/images", "/asp/demo_db_edit.asp", r".*\.aspx$", "/code/"
  ]

  for pattern in disallowed_patterns:
    if re.match(pattern, url):
      return False

  return True


def linkValidation(link):
  if not link.startswith('//') and is_allowed(
      link) and not link.startswith('http') and not link.startswith(
        'javascript:void') and not link.startswith('tryit.asp'):
    return True
  return False

# def regex_check(l):
#   patterns = [
#     "^html", "^css", "^w3css", "^colors", "^icons", "^graphics", "^howto", "^ai", "^datascience", "^python", "^xml", "^js", "^jquery", "^react", "^angular", "^appml", "^w3js", "^java", "^cpp", "^r", "^sql", "^mysql", "^php", "^asp", "^nodejs", "^git", "^browsers", "^whatis", "^tryit", "^typingspeed", "^tags", "^jsref", "^charsets", "^quiztest", "^sass", "^cs", "^vue", "^django", "^kotlin", "^go", "^typescript", "^jsref"
#   ]
#   for pat in patterns:
#     if re.match(pat, l):
#       return True
#   return False

# def edgecases(l):
#   cases = [
#     ['fontawesome', 'icons'],
#     ['google', 'icons'],
#     ['func_mysql', 'mysql']
#   ]

#   for case in cases:
#     if l.startswith(case[0]):
#       return f"/{case[1]}/{l}"
#   return f"/{l}"

def extract_topic(url):
  pattern = r"https://www.w3schools.com\/(.*?)\/default\.asp"
  match = re.search(pattern, url)
  if match:
    return match.group(1)
  else:
    return None

def process_link(l, parent):
  topic = extract_topic(parent)
  if not l.startswith('/') and topic != None:
    return f"/{topic}/{l}"
  elif not l.startswith('/'):
    return f"/{l}"
  return l


def extract_links(soup, url):
  links = []
  for a in soup.find_all('a', href=True):
    b = a['href']
    if linkValidation(b):
      links.append(cfg.BASE_URL + process_link(b, url))
  # print(f"Found {len(links)} links at {url}. Returning...")
  return links


def extract_snippet(soup):
  snippet = ''
  if soup.title:
    snippet += soup.title.text.strip() + ' - '
  if soup.meta and soup.meta.get('content'):
    snippet += soup.meta['content'].strip()
  event_log_maintain("Found snippet. Returning...")
  return snippet


def fix_link(l):
  removed, saved = l.rsplit('/', 1)
  return (cfg.BASE_URL + '/' + saved)


async def process_url(url_path, retry=0):
  if retry == 2:
    print("Second Retry for " + url_path + ", returning.")
    cfg.ERRLOG.append("Second Retry for " + url_path + ", returning.")
    err_record()
    return []
  event_log_maintain(f"Crawling {url_path}.")
  document = DBMS.get_data(url_path)
  if document != None:
    # print(
    #   f"Found {len(document['links'])} links at {url_path} in the database. Returning..."
    # )
    return document['links']
  soup = crawl(url_path)
  new_links = set()
  try:
    if not isinstance(soup, str):
      new_links = extract_links(soup, url_path)
      snippet = extract_snippet(soup)
      DBMS.insert_data({
        'url': url_path,
        'links': new_links,
        'snippet': snippet
      })
    else:
      retry += 1
      return await process_url(fix_link(soup), retry)
    event_log_maintain(f"Processed {url_path}.")
    return new_links
  except:
    msg = cfg.FAIL + "URL error: " + url_path + cfg.N
    print(msg)
    cfg.ERRLOG.append(msg)
    print(traceback.format_exc())
    return []


def crawl(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      return soup
    else:
      cfg.ERRLOG.append(f"Error: {response.status_code} at {url}")
      print(f"Error: {response.status_code} at {url}")
      err_record()
      return url
  except:
    cfg.ERRLOG.append(f"Error: {url}")
    print(f"Error: {url}")
    return ""
