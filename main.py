import config as cfg
import time
import crawler
from error_handle import err_exit
from error_handle import event_log_maintain
import traceback
import asyncio

last_save = time.time()

def time_passed(old):
  return time.time() - old >= 120

async def process_queue(semaphore, url_queue, visited, new_links_handler):
  async with semaphore:
    while True:
      try:
        next_url = url_queue.get_nowait()
      except asyncio.QueueEmpty:
        next_url = ""

      if next_url in visited or next_url == "":
        continue

      visited.add(next_url)
      new_links = await crawler.process_url(next_url)
      await new_links_handler(new_links, visited, url_queue)
      await asyncio.sleep(0)


async def new_links_handler(new_links, visited, url_queue):
  for url in new_links:
    if url not in visited:
      await url_queue.put(url)


# async def save_state():
#   if time_passed(last_save):
#     save_state.save_pages(list(visited), archive)
#     last_save = time.time()
#     print(f"There are currently: {url_queue.qsize()} link(s) in the queue.")

async def task_manager(concurrency=7):
  url_queue = asyncio.Queue()
  visited = set()

  # Initialize the queue with your starting URL(s)
  await url_queue.put(cfg.BASE_URL)

  # Create a semaphore to limit concurrent tasks
  semaphore = asyncio.Semaphore(concurrency)

  tasks = []
  for _ in range(concurrency):
      task = asyncio.create_task(process_queue(semaphore, url_queue, visited, new_links_handler))
      tasks.append(task)

  await asyncio.gather(*tasks)



def main():
  print("Program started.")
  try:
    asyncio.run(task_manager())
  except:
    cfg.ERRLOG.append("An error happened in threads.")
    print(cfg.FAIL + cfg.ERRLOG[-1] + cfg.N)
    print(traceback.format_exc())
    # save_state.save_pages(list(visited), archive)
    err_exit()
  event_log_maintain("Completed.")
  # save_state.save_pages(list(visited), archive)
  save_state.event_log()


if __name__ == '__main__':
  main()
