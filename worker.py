from error_handle import event_log_maintain
import crawler
import time


def worker(url_queue, visited, archive, visited_lock, exit_event):
    while not exit_event.is_set():
      if url_queue.empty():
          # Set the exit_event to signal other workers and the main thread
          exit_event.set()
          break
  
      try:
          url_path = url_queue.get(timeout=1)
      except Empty:
          continue
  
      # Check for the sentinel value
      if url_path is None:
          break
  
      with visited_lock:
          if url_path in visited:
              continue
          visited.add(url_path)
  
      new_links, _ = crawler.process_url(url_path, archive)
  
      with visited_lock:
          new_links_set = set(new_links) - visited
          visited.update(new_links_set)
  
      for link in new_links_set:
          url_queue.put(link)
  
      url_queue.task_done()
