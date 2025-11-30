"""File and Directory Operations Module.

This module provides utility functions for common file and directory
operations including creating, deleting, renaming, and moving.

Typical usage example:
    >>> from helpers.FaDO import create_directory, delete_directory
    >>> create_directory("./my_new_folder")
    >>> delete_directory("./old_folder")

Attributes:
    create_directory: Create a new directory.
    delete_directory: Delete a directory and its contents.
    rename_directory: Rename a directory.
    move_directory: Move a directory to a new location.

TODO(enhancement): Add file copy and move functions.
TODO(enhancement): Add file size and modification time functions.
TODO(feature): Add recursive directory listing function.
FIXME(security): Add path validation to prevent directory traversal.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List


def create_directory(path: str) -> bool:
    """Create a new directory at the specified path.

    This function creates a directory and all necessary parent directories.
    If the directory already exists, it logs a message but does not raise
    an error.

    Args:
        path: The path of the new directory to create.

    Returns:
        True if the directory was created successfully or already exists,
        False if an error occurred.

    Example:
        >>> create_directory("./my_project/data")
        Directory './my_project/data' created.
        True
        >>> create_directory("./existing_dir")
        Directory './existing_dir' already exists.
        True

    Note:
        This function uses os.makedirs which creates parent directories
        as needed, similar to 'mkdir -p' in Unix.
    """
    try:
        os.makedirs(path)
        print(f"Directory '{path}' created.")
        return True
    except FileExistsError:
        print(f"Directory '{path}' already exists.")
        return True
    except Exception as e:
        print(f"Error creating directory '{path}': {e}")
        return False


def delete_directory(path: str) -> bool:
    """Delete a directory at the specified path.

    This function recursively deletes a directory and all its contents,
    including subdirectories and files.

    Args:
        path: The path of the directory to delete.

    Returns:
        True if the directory was deleted successfully,
        False if an error occurred or directory not found.

    Warning:
        This operation is destructive and cannot be undone. All files
        and subdirectories within the specified path will be permanently
        deleted.

    Example:
        >>> delete_directory("./temp_folder")
        Directory './temp_folder' deleted.
        True
        >>> delete_directory("./nonexistent")
        Directory './nonexistent' not found.
        False

    Note:
        Uses shutil.rmtree which removes the entire directory tree.
    """
    try:
        shutil.rmtree(path)
        print(f"Directory '{path}' deleted.")
        return True
    except FileNotFoundError:
        print(f"Directory '{path}' not found.")
        return False
    except Exception as e:
        print(f"Error deleting directory '{path}': {e}")
        return False


def rename_directory(src: str, dest: str) -> bool:
    """Rename a directory from the source path to the destination path.

    This function renames a directory by moving it to a new path within
    the same filesystem.

    Args:
        src: The current path of the directory.
        dest: The new path (name) for the directory.

    Returns:
        True if the directory was renamed successfully,
        False if an error occurred.

    Example:
        >>> rename_directory("./old_name", "./new_name")
        Directory './old_name' renamed to './new_name'.
        True

    Note:
        This function uses shutil.move, so it can also move directories
        across filesystems if needed.
    """
    try:
        shutil.move(src, dest)
        print(f"Directory '{src}' renamed to '{dest}'.")
        return True
    except FileNotFoundError:
        print(f"Directory '{src}' not found.")
        return False
    except Exception as e:
        print(f"Error renaming directory '{src}' to '{dest}': {e}")
        return False


def move_directory(src: str, dest: str) -> bool:
    """Move a directory from the source path to the destination path.

    This function moves a directory and all its contents to a new location.

    Args:
        src: The source path of the directory to move.
        dest: The destination path where the directory should be moved.

    Returns:
        True if the directory was moved successfully,
        False if an error occurred.

    Example:
        >>> move_directory("./data", "./backup/data")
        Directory './data' moved to './backup/data'.
        True

    Note:
        The destination path becomes the new location of the directory.
        If dest is an existing directory, src will be moved inside it.
    """
    try:
        shutil.move(src, dest)
        print(f"Directory '{src}' moved to '{dest}'.")
        return True
    except FileNotFoundError:
        print(f"Directory '{src}' not found.")
        return False
    except Exception as e:
        print(f"Error moving directory '{src}' to '{dest}': {e}")
        return False


def list_directory(path: str, recursive: bool = False) -> Optional[List[str]]:
    """List contents of a directory.

    This function lists all files and subdirectories in the specified path.

    Args:
        path: The path of the directory to list.
        recursive: If True, list contents recursively. Defaults to False.

    Returns:
        A list of file and directory names, or None if an error occurred.

    Example:
        >>> list_directory("./my_project")
        ['file1.py', 'file2.py', 'subdir']
        >>> list_directory("./my_project", recursive=True)
        ['file1.py', 'file2.py', 'subdir/file3.py']
    """
    try:
        p = Path(path)
        if not p.exists():
            print(f"Directory '{path}' not found.")
            return None

        if recursive:
            return [str(f.relative_to(p)) for f in p.rglob("*") if f.is_file()]
        else:
            return [f.name for f in p.iterdir()]
    except Exception as e:
        print(f"Error listing directory '{path}': {e}")
        return None


def file_exists(path: str) -> bool:
    """Check if a file exists at the specified path.

    Args:
        path: The path to check.

    Returns:
        True if the file exists, False otherwise.

    Example:
        >>> file_exists("./config.json")
        True
        >>> file_exists("./nonexistent.txt")
        False
    """
    return Path(path).is_file()


def directory_exists(path: str) -> bool:
    """Check if a directory exists at the specified path.

    Args:
        path: The path to check.

    Returns:
        True if the directory exists, False otherwise.

    Example:
        >>> directory_exists("./my_project")
        True
        >>> directory_exists("./nonexistent")
        False
    """
    return Path(path).is_dir()