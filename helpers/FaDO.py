# FaDO.py - File and Directory Operations
# A utility script to handle common file and directory operations.
# Typical uses include creating, deleting, renaming, and moving files and directories.
# Save this script in the project's "utilities" or "helpers" folder.

import os
import shutil
from pathlib import Path

def create_directory(path: str) -> None:
    """
    Create a new directory at the specified path.

    :param path: The path of the new directory.
    """
    try:
        os.makedirs(path)
        print(f"Directory '{path}' created.")
    except FileExistsError:
        print(f"Directory '{path}' already exists.")
    except Exception as e:
        print(f"Error creating directory '{path}': {e}")

def delete_directory(path: str) -> None:
    """
    Delete a directory at the specified path.

    :param path: The path of the directory to delete.
    """
    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' deleted.")
    except FileNotFoundError:
        print(f"Directory '{path}' not found.")
    except Exception as e:
        print(f"Error deleting directory '{path}': {e}")

def rename_directory(src: str, dest: str) -> None:
    """
    Rename a directory from the source path to the destination path.

    :param src: The source path of the directory.
    :param dest: The destination path of the directory.
    """
    try:
        shutil.move(src, dest)
        print(f"Directory '{src}' renamed to '{dest}'.")
    except FileNotFoundError:
        print(f"Directory '{src}' not found.")
    except Exception as e:
        print(f"Error renaming directory '{src}' to '{dest}': {e}")

def move_directory(src: str, dest: str) -> None:
    """
    Move a directory from the source path to the destination path.

    :param src: The source path of the directory.
    :param dest: The destination path of the directory.
    """
    try:
        shutil.move(src, dest)
        print(f"Directory '{src}' moved to '{dest}'.")
    except FileNotFoundError:
        print(f"Directory '{src}' not found.")
    except Exception as e:
        print(f"Error moving directory '{src}' to '{dest}': {e}")

# TODO: Add more file and directory operations as needed.

    """
    Script name: File and Directory Operations
Filename: FaDO.py
Description: A utility script to handle common file and directory operations.
Typical uses: This script can be used for file and directory management tasks 
such as creating, deleting, renaming, and moving files and directories.
Typical locations: This script can be saved in the project's "utilities" or "helpers" folder.
Purpose and functions: The purpose of this script is to simplify and streamline file 
and directory operations within the project. Functions include creating, deleting, 
renaming, and moving files and directories.

    """