import os
import json
import hashlib
from components.parser import CodeParser

class ProjectConfigCrawler:
    """Scans directories, tracks state changes, and builds structural indexes."""

    def __init__(self, config_path: str = None, skeleton_path: str = None, target_project_path: str = None):
        print(">>>>> config path:", config_path)
        self.config_path = config_path
        self.skeleton_path = skeleton_path
        self.target_project_path = target_project_path
        self.config = self._load_json(config_path)
        self.skeleton = self._load_skeleton_json(skeleton_path)

    def _load_json(self, path: str) -> dict:
        print("🔍 Loading Config from:", path)
        # BUG FIX 1: If path is already a file path, do not join it again
        path_ = path if path.endswith(".json") else os.path.join(path, "config.json")
        if os.path.exists(path_):
            with open(path_, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_skeleton_json(self, path: str) -> dict:
        print("Loading Skeleton from:", path)
        path_ = path if path.endswith(".json") else os.path.join(path, "project_skeleton.json")
        if os.path.exists(path_):
            with open(path_, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_skeleton_json(self, path: str) -> dict:
        print("Loading Skeleton from:", path)
        path_ = path if path.endswith(".json") else os.path.join(path, "project_skeleton.json")
        if os.path.exists(path_):
            with open(path_, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    # SAFETY NET: If the loaded data is a string or not a dict, force it to be an empty dict!
                    if not isinstance(data, dict):
                        print("Stored skeleton cache was corrupted (found string instead of dict). Resetting.")
                        return {}
                    return data
                except json.JSONDecodeError:
                    print(" JSON format corrupted. Returning empty dictionary.")
                    return {}
        return {}

    def _save_skeleton(self):
        # BUG FIX 1: Ensure path resolution points directly to the real file name
        path_ = self.skeleton_path if self.skeleton_path.endswith(".json") else os.path.join(self.skeleton_path,
                                                                                             "project_skeleton.json")

        os.makedirs(os.path.dirname(path_), exist_ok=True)
        with open(path_, "w", encoding="utf-8") as f:
            # BUG FIX 2: Dump the actual 'self.skeleton' data dictionary, NOT the path string!
            json.dump(self.skeleton, f, indent=2)
        print(f"[SUCCESS] Persistent state tracking index cached out to: {path_}")

    def _calculate_hash(self, file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def scan_project(self) -> bool:
        """Scans workspace directories and updates the index if modifications occur."""
        # BUG FIX 3: Set robust fallback defaults if the config json data is empty
        exclude_dirs = set(self.config.get("exclude_dirs", [".git", "__pycache__", "venv"]))
        extensions = tuple(self.config.get("watch_extensions", [".py", ".json", ".md"]))

        target_root = self.target_project_path
        if not target_root or not os.path.exists(target_root):
            raise ValueError(f"Invalid target project path route provided: {target_root}")

        os.chdir(target_root)
        root_dir = os.getcwd()
        print(">> Core Target Scanning Root:", root_dir)

        changes_detected = False
        current_files = {}

        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]

            for file in files:
                if file.endswith(extensions):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, root_dir)
                    print("📁 Found Watchable File Target:", rel_path)

                    try:
                        file_hash = self._calculate_hash(full_path)
                    except IOError:
                        continue

                    current_files[rel_path] = file_hash

                    # Check if file has been modified or is entirely new to our cache
                    if self.skeleton.get("files", {}).get(rel_path, {}).get("hash") != file_hash:
                        changes_detected = True
                        print(f"[MODIFY] Structure mutation detected in: {rel_path}")

                        if rel_path.endswith(".py"):
                            symbols = CodeParser.parse_python_file(full_path)
                        else:
                            symbols = {
                                "summary": "Non-python structural summary tracking not fully implemented.",
                                "classes": {},
                                "functions": {}
                            }

                        # Populate data back into the operational skeleton tracking memory mapping
                        self.skeleton.setdefault("files", {})[rel_path] = {
                            "hash": file_hash,
                            "symbols": symbols
                        }

        # Handle file deletions (purge files from skeleton cache that no longer exist on drive)
        cached_files = list(self.skeleton.get("files", {}).keys())
        for path in cached_files:
            if path not in current_files:
                changes_detected = True
                print(f"[DELETE] Purging deleted file asset trace from cache: {path}")
                del self.skeleton["files"][path]

        # Save updates to disk if changes were caught
        if changes_detected:
            self._save_skeleton()

        return changes_detected

