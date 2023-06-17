import os
import importlib.util

def list_names():
    script_names = {}
    current_directory = os.path.dirname(os.path.abspath(__file__))

    for file in os.listdir(current_directory):
        file_path = os.path.join(current_directory, file)
        if file.endswith(".py") and os.path.isfile(file_path) and file != "list_names.py" and file != "__init__.py":
            module_name = file[:-3]

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            names = [name for name in dir(module) if not name.startswith("__")]
            script_names[module_name] = names

    return script_names
