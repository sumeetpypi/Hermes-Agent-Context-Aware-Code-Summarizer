import os
import json
import hashlib
from components.parser import CodeParser
from hermes_agent.tools.terminal_tool import _active_environments
from hermes_agent.tools.file_operations import ShellFileOperations


class ProjectFileCrawler:
    """Scans directories, tracks state changes, and builds structural indexes."""

    def __init__(self, config_path, skeleton_path, target_path):
        self.config_path = config_path
        self.skeleton_path =   skeleton_path

        self.target_path = target_path
        self.shell_operations()
        

    def shell_operations(self):
          #1. Pass the actual environment OBJECT (not the dictionary) to File Operations
        envs = self.ExtractEnv()
        file_ops = ShellFileOperations(envs)
        print("File ops initialised successfully:", file_ops)

        # 4. Read your target file
        try:
            result = file_ops.read_file(self.skeleton_path)
            if hasattr(result, 'content'):
                    raw_content = result.content
            else:
                # Fallback if it evaluates to a string or dict
                raw_content = str(result)

            # Clean up the custom formatting (strips line numbers and pipes)
            clean_lines = []
            for line in raw_content.splitlines():
                # Splitting at the pipe character '|' if it exists to remove line numbers
                if '|' in line:
                    parts = line.split('|', 1)
                    clean_lines.append(parts[1])
                else:
                    clean_lines.append(line)

            # Rejoin and print the perfectly formatted text
            final_output = "\n".join(clean_lines)
            print(final_output)
        
        except Exception as e:
            print(f"Failed to read file: {e}")

    
    def ExtractEnv(self):   
        # 1. Extract the environment object out of the global tracking dictionary
        env_registry = _active_environments
        print("Available environments:", list(env_registry.keys()))
        if env_registry:
        # Gets the first available environment object value
            active_env_obj = next(iter(env_registry.values()))
            return active_env_obj
        else:
            raise RuntimeError("No active environment sessions found. Run a terminal_tool command first.")

