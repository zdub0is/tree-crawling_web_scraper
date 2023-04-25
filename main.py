from concurrent.futures import ThreadPoolExecutor, as_completed
import config as cfg
import save_state
import time
import crawler
from error_handle import err_exit
from error_handle import event_log_maintain
import traceback
from queue import Empty, Queue
from threading import Lock, Barrier


def main():
  last_crawl, archive = save_state.load_state()
  to_visit = {cfg.BASE_URL}
  visited = set()
  save_interval = 10
  if last_crawl != None:
    if cfg.BASE_URL in last_crawl: last_crawl.remove(cfg.BASE_URL)
    visited = set(last_crawl)

  if archive == None:
    archive = dict()
  try:
    url_queue = Queue()
    url_queue.put(cfg.BASE_URL)
    future = []
    while not url_queue.empty():
      with ThreadPoolExecutor(max_workers=5) as executor:
        next_url = url_queue.get(timeout=10)
        visited.add(next_url)
        future.append(executor.submit(
          crawler.process_url,
          next_url))  # Fix: pass function and argument separately

        for f in as_completed(future):
          result = f.result()
          new_urls, title, snip = result
          for url in new_urls:
            if url not in visited: url_queue.put(url)
          archive[title] = snip

          # Save the state periodically
        if len(visited) % save_interval == 0:
          save_state.save_pages(list(visited), archive)

  except:
    cfg.ERRLOG.append("An error happened in threads.")
    print(cfg.FAIL + cfg.ERRLOG[-1] + cfg.N)
    print(traceback.format_exc())
    save_state.save_pages(list(visited), archive)
    err_exit()
  save_state.save_pages(list(visited), archive)
  save_state.event_log()


if __name__ == '__main__':
  main()
