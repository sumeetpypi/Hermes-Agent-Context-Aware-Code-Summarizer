import time
import queue
import threading
from typing import Callable, Any

class HermesScheduler:
    """Manages background job queues, multi-threading, and 24/7 execution loops."""
    
    def __init__(self):
        self.job_queue = queue.Queue()
        self.is_running = False
        self.workers = []

    def add_job(self, task_func: Callable[..., Any], *args, **kwargs):
        """Thread-safely pushes a new job execution block into the processing queue."""
        self.job_queue.put((task_func, args, kwargs))

    def _worker_loop(self):
        """Internal thread loop pulling and executing code tasks infinitely."""
        while self.is_running:
            try:
                # Blocks for 1 second waiting for an incoming code job
                task_func, args, kwargs = self.job_queue.get(timeout=1)
                try:
                    task_func(*args, **kwargs)
                except Exception as e:
                    print(f" [Worker Error] Task execution failed: {str(e)}")
                finally:
                    self.job_queue.task_done()
            except queue.Empty:
                continue

    def start_service(self, worker_count: int = 2):
        """Spawns dedicated active worker threads to process tasks concurrently."""
        self.is_running = True
        print(f"⚙️ Spawning {worker_count} active concurrent worker threads...")
        for i in range(worker_count):
            t = threading.Thread(target=self._worker_loop, name=f"HermesWorker-{i}", daemon=True)
            t.start()
            self.workers.append(t)

    def run_forever(self, interval_seconds: int, cron_task: Callable[..., Any]):
        """The 24/7 heartbeat execution engine block."""
        print(f" Heartbeat active. Running background loop every {interval_seconds}s.")
        try:
            while True:
                # Automatically injects a project scan task into the worker queue
                self.add_job(cron_task)
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\n Shutting down active daemon loops gracefully...")
            self.is_running = False
