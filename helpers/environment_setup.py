# environment_setup.py - Environment Setup
# A script that sets up your project's environment, installs dependencies,
# and configures settings to ensure a consistent development environment for all team members.
# Typical uses include automating the setup process for a new developer or resetting an existing developer's environment.
# Save this script in the project's root directory or in a "scripts" or "utilities" folder.

import os
import subprocess
import sys

def run_command(command: str) -> None:
    """
    Run the specified command and print its output.

    :param command: The command to run.
    """
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if stdout:
        print(stdout.decode('utf-8'))

    if stderr:
        print(stderr.decode('utf-8'), file=sys.stderr)

def create_virtualenv(venv_name: str = 'venv') -> None:
    """
    Create a virtual environment with the specified name.

    :param venv_name: The name of the virtual environment to create.
    """
    run_command(f'python -m venv {venv_name}')

def activate_virtualenv(venv_name: str = 'venv') -> None:
    """
    Activate the specified virtual environment.

    :param venv_name: The name of the virtual environment to activate.
    """
    if sys.platform == 'win32':
        activation_script = os.path.join(venv_name, 'Scripts', 'activate')
    else:
        activation_script = os.path.join(venv_name, 'bin', 'activate')

    run_command(f'source {activation_script}')

def install_dependencies(requirements_file: str = 'requirements.txt') -> None:
    """
    Install dependencies from the specified requirements file.

    :param requirements_file: The path to the requirements file.
    """
    run_command(f'pip install -r {requirements_file}')

def main() -> None:
    create_virtualenv()
    activate_virtualenv()
    install_dependencies()

if __name__ == '__main__':
    main()

# TODO: Add support for other languages and package managers, such as npm for JavaScript



    """
    Script name: Environment Setup

Filename: environment_setup.py

Description: A script that sets up your project's environment, installs dependencies, 
and configures settings to ensure a consistent development environment for all team members.

Typical uses: This script can be used to automate the setup process for a new developer joining
 the project or to reset an existing developer's environment.

Typical locations: This script can be saved in the project's root directory or in a "scripts"
or "utilities" folder.

Purpose and functions: The purpose of this script is to provide an easy way to set up and 
maintain a consistent development environment across the team.

Please note that this example is for a Python project using pip and virtualenv. 

Modify the script accordingly for your project's specific needs.
    







    """