import requests
from bs4 import BeautifulSoup
import json
import config as cfg
from error_handle import event_log_maintain
import re

def is_allowed(url):
  disallowed_patterns = [] # respect robots.txt! add disallows here.
  # "/images", "/asp/demo_db_edit.asp", r".*\.aspx$", "/code/"
  for pattern in disallowed_patterns:
    if re.match(pattern, url):
      return False

  return True


def extract_links(soup):
  links = []
  for a in soup.find_all('a', href=True):
    if a['href'].startswith(
        '/') and not a['href'].startswith('//') and is_allowed(a['href']):
      links.append(cfg.BASE_URL + a['href'])
  event_log_maintain(f"Found {len(links)} links. Returning...")
  return links


def extract_snippet(soup):
  snippet = ''
  if soup.title:
    snippet += soup.title.text.strip() + ' - '
  if soup.meta and soup.meta.get('content'):
    snippet += soup.meta['content'].strip()
  event_log_maintain("Found snippet. Returning...")
  return snippet


def process_url(url_path):
  event_log_maintain(f"Crawling {url_path}.")
  soup = crawl(url_path)
  new_links = set()

  if soup:
    new_links = extract_links(soup)
    snippet = extract_snippet(soup)
  event_log_maintain(f"Processed {url_path}.")
  return new_links, url_path, snippet


def crawl(url):
  try:
    response = requests.get(url)
    if response.status_code == 200:
      soup = BeautifulSoup(response.text, 'html.parser')
      return soup
    else:
      cfg.ERRLOG.append(f"Error: {response.status_code} at {url}")
      print(f"Error: {response.status_code} at {url}")
      return None, None
  except:
    cfg.ERRLOG.append(f"Error: {url}")
    print(f"Error: {url}")
    return None, None
