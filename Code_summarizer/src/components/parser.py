import ast
import os


class CodeParser:
    """Extracts structural metadata from source code using AST parsing."""

    @staticmethod
    def parse_python_file(file_path: str) -> dict:
        """Parses a Python file to extract classes, functions, and docstrings."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            return {"error": f"Syntax error during parsing: {str(e)}"}

        metadata = {
            "summary": ast.get_docstring(tree) or "No module-level documentation.",
            "classes": {},
            "functions": {}
        }

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                class_methods = {}
                for sub_node in node.body:
                    if isinstance(sub_node, ast.FunctionDef):
                        class_methods[sub_node.name] = ast.get_docstring(sub_node) or "Undocumented."

                metadata["classes"][node.name] = {
                    "docstring": ast.get_docstring(node) or "Undocumented.",
                    "methods": class_methods
                }

            elif isinstance(node, ast.FunctionDef):
                metadata["functions"][node.name] = ast.get_docstring(node) or "Undocumented."

        return metadata
