import os
from watchdog.events import FileSystemEventHandler
from typing import Callable

class HermesFileWatcherHandler(FileSystemEventHandler):
    """Listens for OS file system changes and forwards them to the scheduler queue."""
    
    def __init__(self, config: dict, on_change_callback: Callable[[], None]):
        super().__init__()
        self.on_change_callback = on_change_callback
        self.exclude_dirs = set(config.get("exclude_dirs", []))
        self.watch_extensions = tuple(config.get("watch_extensions", []))

    def _should_trigger(self, file_path: str) -> bool:
        """Determines if the altered file should trigger a project-wide re-index."""
        # 1. Skip directories
        if os.path.isdir(file_path):
            return False
            
        # 2. Check if the file is inside an excluded directory
        normalized_path = os.path.normpath(file_path)
        parts = normalized_path.split(os.sep)
        if any(excluded in parts for excluded in self.exclude_dirs):
            return False

        # 3. Verify it matches our watched extensions (e.g., .py, .ts)
        return file_path.endswith(self.watch_extensions)

    def on_modified(self, event):
        if self._should_trigger(event.src_path):
            self.on_change_callback()

    def on_created(self, event):
        if self._should_trigger(event.src_path):
            self.on_change_callback()

    def on_deleted(self, event):
        if self._should_trigger(event.src_path):
            self.on_change_callback()
