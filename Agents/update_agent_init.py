import os
import re

def generate_imports(base_path):
    imports = []
    
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Get the subdirectory path without the base path
                subdir = root.replace(base_path, "").lstrip(os.sep)
                module_path = subdir.replace(os.sep, ".")
                
                with open(os.path.join(root, file), "r") as f:
                    content = f.read()
                    
                    # Match class and function names
                    matches = re.findall(r"^(?:class|def)\s+(\w+)", content, re.MULTILINE)
                    
                    for match in matches:
                        import_line = f"from {module_path}.{file[:-3]} import {match}"
                        imports.append(import_line)
                        
    return imports

if __name__ == "__main__":
    agents_path = os.path.join("Agents")
    imports = generate_imports(agents_path)
    
    with open(os.path.join("my_library", "__init__.py"), "w") as f:
        f.write("# my_library folder libraries\n")
        f.write("# my_library/__init__.py\n\n")
        
        for import_line in imports:
            f.write(import_line + "\n")
