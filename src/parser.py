import ast
import os

class CodeParser:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def get_python_files(self):
        """Walks through the directory to find all Python files, omitting environment folders."""
        py_files = []
        for root, _, files in os.walk(self.root_dir):
            if 'venv' in root or '.git' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    def parse_file(self, file_path):
        """Parses a specific file and extracts functions and classes into structural chunks."""
        chunks = []
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            print(f"Skipping {file_path} due to a syntax error.")
            return chunks

        relative_path = os.path.relpath(file_path, self.root_dir)

        for node in ast.walk(tree):
            # Extract Individual Functions
            if isinstance(node, ast.FunctionDef):
                docstring = ast.get_docstring(node) or "No documentation provided."
                func_code = ast.get_source_segment(code, node) or ""
                
                chunks.append({
                    "id": f"{relative_path}::{node.name}",
                    "type": "function",
                    "name": node.name,
                    "file": relative_path,
                    "docstring": docstring,
                    "code": func_code
                })
                
            # Extract Individual Classes
            elif isinstance(node, ast.ClassDef):
                docstring = ast.get_docstring(node) or "No documentation provided."
                class_code = ast.get_source_segment(code, node) or ""
                
                chunks.append({
                    "id": f"{relative_path}::{node.name}",
                    "type": "class",
                    "name": node.name,
                    "file": relative_path,
                    "docstring": docstring,
                    "code": class_code
                })

        return chunks

    def parse_all(self):
        """Parses the entire codebase directory."""
        all_chunks = []
        files = self.get_python_files()
        for file in files:
            all_chunks.extend(self.parse_file(file))
        return all_chunks

if __name__ == "__main__":
    # Test the parser on itself to confirm it works
    parser = CodeParser(root_dir=".")
    parsed_chunks = parser.parse_file("src/parser.py")
    
    print(f"--- Testing Parser on parser.py ---")
    print(f"Found {len(parsed_chunks)} structural code chunks.")
    for chunk in parsed_chunks[:2]:  # Print the first couple of results
        print(f"\n[ID]: {chunk['id']} ({chunk['type'].upper()})")
        print(f"[Docstring]: {chunk['docstring']}")