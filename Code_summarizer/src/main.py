import json
import os
import sys
import time

from components.fileReadCrawler import ProjectFileCrawler
from hermes_agent.tools.terminal_tool import terminal_tool, _active_environments
# from hermes_agent.tools.file_operations import ShellFileOperation
from components.fileReadCrawler import ProjectFileCrawler
from components.crawler import ProjectConfigCrawler


class DocumentationGenerator:
    """Assembles structural indexes into clean system-wide Markdown files."""
    
    def __init__(self, crawler: ProjectConfigCrawler):
        self.crawler = crawler

def main():
    
    #user_path = input("Enter the absolute path to your project directory:").strip()
    
    print("🚀 Initializing Context-Aware Code Summarizer Service Engine...")
    user_path = UserInput()

    skeleton_path = user_path.get("skeleton_path")
    user_config_path = user_path.get("config_path")
    target_config_path = user_path.get("target_path")
    print("show config path", user_config_path)
    crawler = ProjectConfigCrawler(config_path=user_config_path, skeleton_path=skeleton_path,
                                   target_project_path=target_config_path)
    DocumentationGenerator(crawler)
    crawler.scan_project()

    validate_path(user_path=user_config_path, target_path=target_config_path)


def UserInput():

    target_project = input("Enter the target project path: ").strip()
    if target_project:
        print("Target path project added")
    else:
        raise Exception

    user_path_config = input("Enter the absolute path to your project directory:").strip()

    if user_path_config:
        print("config path project added")
    else:
        raise Exception


    user_skeleton_path = input("Enter project skeletion folder path(Where you want to keep your project skeleton config file").strip()

    if user_path_config:
        print("skeletion path project added ")

    else:
        raise Exception

    # Clean up quotes if the user dragged and dropped the folder into the console
    path_config  = user_path_config.strip('"').strip("'") 
    skeleton_path = user_skeleton_path.strip('"').strip("'")
    target_path = target_project.strip('"').strip("'")
    input_user = {"config_path": str(path_config), "skeleton_path": str(skeleton_path), "target_path": str(target_path)}
    return input_user

def validate_path(user_path, target_path):
    #1. Validate that the directory actually exists before passing it to the tool
    # if os.path.isdir(user_path):
    #     # Pass the user's path into the terminal tool commandD:\git-project\code_summarizer\Code_summarizer\src\hermes\config.json
    #     dir_change = terminal_tool(f"cd {user_path}")

    if os.path.isdir(user_path):

        print("user path", user_path)
        clean_bash_path = os.path.normpath(user_path).replace('\\', '/')
        print("Cleaned Bash Path:", clean_bash_path)

        dir_change = terminal_tool(f"cd {clean_bash_path}  && ls")
        # print(terminal_tool(f"dir"))

        data_dict = json.loads(dir_change)
        print(data_dict)


        if data_dict and data_dict.get("exit_code") == 0:
                print("✨ Directory validation passed. Syncing project environment metadata...")

                # 1. Clean and parse the multiline console file list output safely
                raw_output = data_dict.get("output", "")
                file_list = [line.strip() for line in raw_output.split("\n") if line.strip()]

                # 2. Extract specific targets dynamically instead of relying on fragile indexes
                config_file = next((f for f in file_list if f.endswith(".json") and "config" in f.lower()), None)
                skeleton_file = next((f for f in file_list if f.endswith(".json") and "skeleton" in f.lower()), None)

                # Fallback to defaults if specific pattern match heuristics fail
                if not config_file or not skeleton_file:
                    print(" Direct string keyword matching failed. Falling back to default structural mapping.")
                    config_file = next((f for f in file_list if f.endswith(".json")), "config.json")
                    skeleton_file = next((f for f in file_list if f.endswith(".json") and f != config_file), "project_skeleton.json")

                # 3. Resolve absolute system file paths securely using your validated user_path
                file_path = os.path.join(user_path, config_file)
                file_ske = os.path.join(user_path, skeleton_file)

                print(f"🔎 Located Target Profile Config: {file_path}")
                print(f"🔎 Located Target State Cache:  {file_ske}")

                # 4. Initialize your core engine crawler pipeline context
                ProjectFileCrawler(config_path=file_path, skeleton_path=file_ske, target_path=target_path)

        else:
                # Throw an explicit runtime diagnostic crash payload
                error_details = data_dict.get("error") if data_dict else "No response mapping received from backend shell thread context."
                raise RuntimeError(f"Failed to synchronize workspace directory directory structure. Details: {error_details}")






if __name__ == "__main__":
    main()
